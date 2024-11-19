"""photovoltaic model component"""
from math import cos,sin,asin,acos,tan,radians,exp
from enum import Enum
from dataclasses import dataclass
import datetime
import math
from typing import Callable, Self
import pandas as pd
from pandas import DataFrame, Series
from models.geometry import GeoPosition, Orientation
from models.weather import Weather, WeatherParam as W
from models.components import Component
from models.econometrics import Cost, Currency
class CellType(Enum):
    """crystal cell configuration"""
    POLI = 'policristalino'
    MONO = 'monocristalino'

class TempCoef(Enum):
    """
    Temperature coefficient loss
    ~~~~
    >>> Factors
    OPEN_RACK = factor on modular rack.
    ROOF_MOUNT = module mounted on roof (default)
    """
    OPEN_RACK={"alpha":-3.47,"beta":-0.0594,"deltaT":3}
    ROOF_MOUNT={"alpha":-2.98,"beta":-0.0471,"deltaT":1}

class PvParam(Enum):
    """
    Photovoltaic Parameters
    ~~~~
    DataFrame Result columns names enumerate
    >>> List
    ... INCIDENT-> incident irradiance in W/m2 over surface.
    ... DIRECT-> irradiance over surface normal.
    ... DIFFUSE-> diffuse irradiance over surface.
    ... GROUND-> irradiance received by the ground.
    ... SYS_CAP-> total system capacity module in kW
    """
    INCIDENT = 'IRR_incident'
    DIRECT = 'IRR_direct_surface'
    DIFFUSE = 'IRR_diffuse_surface'
    GROUND = 'IRR_ground'
    T_CELL = 'Temperature_cell'
    SYS_CAP = 'System_capacity_KW'

@dataclass()
class PowerCurve:
    '''voltage curve specification'''
    max_tension:float = 30.5
    short_tension:float = 37.5
    max_ampere:float = 4.26
    short_ampere:float = 5.68

@dataclass()
class Cell:
    '''smaller panel component'''
    cell_type:CellType = CellType.MONO
    quantity_row:int = 6
    quantity_col:int = 10

@dataclass()
class ThermalCoef:
    """
    Thermal properties of PV Panels
    ~~~~
    >>> setup
        ... short_circuit_t->short circuit temperature coefficient
        ... open_circuit_t->open circuit temperature coefficient
        ... power_coef_t->power temperature coefficient
        ... power_coef_tmax->power max temperature coefficient

    thermal behavior panel, units %/C°
    """
    short_circuit_t:float = 0.0814#%/C°
    open_circuit_t:float = -0.3910#%/C°
    power_coef_t:float = -0.5141#%/C°
    power_coef_tmax:float = 0.1#%/C°

class Length(Enum):
    """Dim unit type"""
    CM = 100.0
    MM = 1000.0
    M = 1.0
    FT = 3.280839895
    IN = 39.37007874

type Dimensions = tuple[float,float,Length]
class PvTechnicalSheet:
    "solar plane power technical specification"
    def __init__(self,
        power:int = 100,
        area:float|Dimensions= 1, #m2 or (long, wide in cm)
        efficiency = 6/100,  # w/m2
        power_curve:PowerCurve = PowerCurve(),
        cell:Cell = Cell(),
        thermal:ThermalCoef = ThermalCoef(),
                ) -> None:
        self.power = power
        self.efficiency = efficiency
        self.power_curve = power_curve
        self.cell = cell,
        self.thermal = thermal

        if isinstance(area,float):
            self.area = area
        if isinstance(area,tuple):
            self.area = area[0]*area[1]/(area[2].value*area[2].value)

class CostModel(Enum):
    """model of cost calculation Lambda"""
    #PV COST MODEL, includes price clp per watt,
    # including cost of panel, inverter, installation and infrastructure.
    ON_GRID:Callable[[float],float] = \
        lambda size_w: math.floor(-152.6*math.log(size_w)+2605.9) # clp/w
    OFF_GRID:Callable[[float],float] = \
        lambda size_w: math.floor(-414.7*math.log(size_w)+6143.9) # clp/w
    #PV linear COST MODEL,
    # includes price clp per watt,just panel.
    LINEAR:Callable[[float],float] = lambda size_w: 245990/655
class Photovoltaic(Component):
    """
    PV primary component
    ~~~~
    global component for operate Weather fetch, solar irradiation calculus, and technical
    lost. Not include shadow analysis.
    >>> init
        power: in nominal Watts each panel
        orientation : Orientation() class
        technical_sheet: has some default in PvTechnicalSheet() class
        cost or cost_model_fun: one of them has to me None, or Cost() zero by default
    >>>  methods
    ... .normal() -> normal azimuth and elevation
    ... .calc_cosPhi() -> angle between solar vector and surface normal vector
    ... .calc_irradiation() -> al irradiation received by an inclined surface.
    ... .calc_reflection() -> IAM reflection losses coefficient.
    ... .calc_energy() -> calc al lost, and irradiation performance to a nominal panel.

    """
    energy:DataFrame = pd.DataFrame()
    PARAMS:list[W] = [W.TEMPERATURE,W.DIRECT,W.DIFFUSE,W.ALBEDO,W.ZENITH,W.WIND_SPEED_10M]
    _system_capacity:DataFrame|None = None

    def __init__(
        self,
        weather:Weather,
        description: str = 'Panel Fotovoltaico',
        model: str = 'generic',
        specification: str | None = None,
        reference: str | None = None,
        quantity: int = 1,#units
        cost:Cost|None = None,
        cost_model:Callable[[float],float]|None = CostModel.LINEAR,
        orientation:Orientation = Orientation(),
        technical_sheet:PvTechnicalSheet = PvTechnicalSheet(),
        ) -> None:
        #auxiliary values
        aux_cost:Cost
        if cost is None:
            aux_cost = Cost(cost_model(technical_sheet.power)*technical_sheet.power,currency=Currency.CLP)
        else:
            aux_cost = cost
        print('inside cost pv : ',aux_cost.value,aux_cost.currency)
        super().__init__(description, model, specification,reference,aux_cost, quantity)

        self.orientation = orientation
        self.technical_sheet = technical_sheet
        self._weather = weather
        #init weather values
        self._weather.parameters =self.PARAMS
        weather_date = weather.get_data()
        #calc reusable cos_phi
        self._cos_phi:DataFrame = weather_date['date']\
            .apply(lambda date:self._calc_cos_phi(date=date,location=weather.geo_position))


    def set_cost(self,cost:Cost):
        """change cost value"""
        super().cost = cost

    def _normal(self)->dict[str,float]:
        """elevation and azimuth surface´s normal"""
        return {'azimuth':self.orientation.inclination,'elevation':self.orientation.inclination}

    def _calc_cos_phi(self,date:datetime,location:GeoPosition)->float:
        """or angle between sun and normal or surface"""
        sun= location.sun_position(date)

        cos_phi = self.orientation.cos_phi(
            sun_azimuth=sun['azimuth'],
            sun_elevation=sun['elevation'])

        return cos_phi

    def _calc_irradiation(self)->DataFrame:
        """calc irradiation on plane, direct,diffuse, ground and global on plane w/m^2 """
        irr:DataFrame = pd.DataFrame()
        #setting angle sun->surface
        irr['cos_phi'] = self._cos_phi
        #weather data with necessary for calc
        weather_data = self._weather.get_data()

        #calc direct irradiation
        irr[PvParam.DIRECT.value] = weather_data[W.DIRECT.value] * self._cos_phi


        #calc diffuse irradiation
        cos_b = (1+cos(radians(self.orientation.inclination)))
        irr[PvParam.DIFFUSE.value] = weather_data[W.DIFFUSE.value] * 0.5 * cos_b
        #calc ground irradiation
        irr[PvParam.GROUND.value] = weather_data[W.DIRECT.value] * 0.5 * \
            weather_data[W.ALBEDO.value] * cos_b

        #calc global incident irradiation
        reflection = self._calc_reflection()
        irr[PvParam.INCIDENT.value] = \
            irr[PvParam.DIRECT.value]*reflection\
            +irr[PvParam.GROUND.value]\
            +irr[PvParam.DIFFUSE.value]
        #irr.fillna(0.0,inplace=True)
        irr.infer_objects(copy=False)

        return irr

    def _calc_reflection(self)->Series:
        '''
        reflection Module
        ~~~~
        the reflection of radiation on the panel cover is one
        of the elements that is relevant in terms of losses.
        The parameter that characterizes the loss by reflection

        >>> is called modification by angle of incidence (IAM).
        ... The reflected amount depends on the material
        ... of the cover and its thickness.

        Ref:
        >>> https://solar.minenergia.cl/downloads/fotovoltaico.pdf#page=6
        '''
        reflex = pd.DataFrame()

        surface_reflex=1.526
        air_reflex= 1
        glass_extinction = 4 # [1/m]
        thickness = 0.002 #[m] 2 mm

        #get angular
        reflex['phi']:DataFrame = self._cos_phi.apply(acos) # type: ignore
        reflex['phi_r']:DataFrame = reflex['phi'].apply(\
            lambda phi:asin(sin(phi)*(air_reflex/surface_reflex)\
                ))
        # print(reflex)

        #transmittance
        def _tau_reflex(row:DataFrame)->float:
            #extract from row
            phi = row['phi']
            phi_r = row['phi_r']
            #calc transmittance on surface
            tau =  exp(-1* glass_extinction*thickness/(cos(phi_r)))*\
            (1 -0.5*(\
                (sin(phi_r-phi)**2 / sin(phi_r+phi)**2) +\
                (tan(phi_r-phi)**2 / tan(phi_r+phi)**2) \
                    ))
            #values close to ZERO, turn into cero
            return tau if tau>0.001 else 0
        #transmittance on phi == 0°
        tau_zero:float = exp(-1*glass_extinction*thickness)*\
                (1-((1-surface_reflex)/(1+surface_reflex))**2)

        transmittance_reflex = reflex.apply(_tau_reflex,axis=1)

        #IAM
        iam = transmittance_reflex/tau_zero

        return iam

    def _calc_temperature_cell(self,irradiance:DataFrame,coef:TempCoef=TempCoef.ROOF_MOUNT)->Series:
        """
        Cell temperature
        ~~~~
        Calculation for temperature inside de cell ,
        important! for temperature loss efficiency calc,
        based in PVWatts model DOBOS,2014 used by NREL
        ref: https://solar.minenergia.cl/downloads/fotovoltaico.pdf#page=8
        """
        #calc panel over irradiation result
        weather_data =  self._weather.get_data()
        irradiance[W.WIND_SPEED_10M.value] = weather_data[W.WIND_SPEED_10M.value]
        #coefficient temperature
        #alpha = self.technical_sheet.thermal.short_circuit_t
        #beta = self.technical_sheet.thermal.open_circuit_t
        alpha = coef.value['alpha']
        beta = coef.value['beta']
        delta = coef.value['deltaT']

        #aux function
        def _temperature_panel(row):
            return row[PvParam.INCIDENT.value]*exp(alpha+\
                beta*row[W.WIND_SPEED_10M.value])

        def _temperature_cell(row):
            return _temperature_panel(row) + row[PvParam.INCIDENT.value]*delta/1000

        t_cell_result = irradiance.apply(_temperature_cell,axis=1)
        return t_cell_result

    def _operational_loss(self)->float:
        '''
        Total losses for operational causes
        '''
        model_loss = {
            'dirt':0.02,
            'shadows':0.03,
            'imperfections':0.02,
            'wiring':0.02,
            'connectors':0.005,
            'degradation':0.015,
            'off_timer':0.03,
            'lab_error':0.01,
        }

        total_loss = 0
        for _,loss in model_loss.items():
            total_loss += loss
        return total_loss


    def _calc_system_capacity(self,irradiation:DataFrame)->DataFrame:
        """
        System capacity Global [W]
        ~~~~
        """
        #capacity under lab conditions AREA*QUANTITY*Ef
        nominal_capacity:float = self.technical_sheet.area *\
            self.technical_sheet.efficiency *self.quantity

        #temperature performance
        t_cel:Series = self._calc_temperature_cell(irradiation)
        t_ref:float = 25.5 #C°
        gamma:float = self.technical_sheet.thermal.power_coef_t/100# %/C°
        irr_incident:Series = irradiation[PvParam.INCIDENT.value]
        dobo_limit = 125.0#W/m^2
        ref_irr = 1000#W/m^2

        #init calc system capacity
        system_capacity:DataFrame = pd.DataFrame()
        system_capacity[PvParam.T_CELL.value] = t_cel #°C
        system_capacity[PvParam.INCIDENT.value] = irr_incident #w/m^2
        ##print(system_capacity.info())


        #system capacity in w/m^2
        def calc_capacity(row)->DataFrame:
            #ref https://pvwatts.nrel.gov/downloads/pvwattsv5.pdf#page=9
            # https://solar.minenergia.cl/downloads/fotovoltaico.pdf#page=8
            #data extract
            incident,t_cell = row[PvParam.INCIDENT.value],row[PvParam.T_CELL.value]

            if incident>= dobo_limit:
                return (nominal_capacity*incident/ref_irr) *nominal_capacity * (1+gamma*(t_cell-t_ref))


            return 0.008 * nominal_capacity * (incident**2 / ref_irr) *\
                nominal_capacity *\
                (1+gamma*(t_cell-t_ref))

        system_capacity[PvParam.SYS_CAP.value] = system_capacity.apply(calc_capacity,axis=1)

        #operational losses
        inverter_efficiency = 0.96
        op_loss = self._operational_loss()

        #SYSTEM GLOBAL CAPACITY * UNIT AREA * QUANTITY UNITS
        system_capacity[PvParam.SYS_CAP.value] = system_capacity[PvParam.SYS_CAP.value]\
            .apply(lambda cap: cap *inverter_efficiency* (1-op_loss))

        return system_capacity

    def nominal_power(self):
        """
        power in kW = 1000 Watt
        """
        return self.technical_sheet.power * self.quantity/1000

    def get_energy(self) -> DataFrame:
        """
        Module Energy Calc
        ~~~~
        ... ref: https://solar.minenergia.cl/downloads/fotovoltaico.pdf#page=3
        Calc energy generated for current instance, module with A surface and N quantity
        calc amount of energy generated by year"""
        #use stored value
        if self._system_capacity is not None:
            return self._system_capacity

        #fetch nasa weather data
        weather_data = self._weather.get_data()

        #tempo init values for energy
        self.energy[['date','month','day','hour']] = weather_data[['date','month','day','hour']]


        #calc irradiation factors
        irradiation:DataFrame =self._calc_irradiation()#w/m^2
        ##print(irradiation.info())

        #calc system_capacity in KW
        system_capacity = self._calc_system_capacity(irradiation=irradiation)
        system_capacity[['date','month','day','hour']] = weather_data[['date','month','day','hour']]
        #into int cols
        system_capacity[['month','day','hour']] = system_capacity[['month','day','hour']].astype(int)

        #rename columns
        system_capacity=system_capacity.rename(columns={'date':'date UTC'})

        ##print(system_capacity.info())
        self._system_capacity = system_capacity

        return system_capacity


class PV_adapter:
    def __init__(self,
                nominal_power:int,
                weather_data:Weather,
                cost:Cost,
                quantity:int,
                

                ) -> None:
        pass


#short test
# test_weather = Weather()
# panel = Photovoltaic(weather=test_weather)
# panel.quantity = 20
# panel.power = 250
# print(panel.get_energy(),panel.nominal_power())
# End-of-file (EOF)
