"""photovoltaic model component"""
from math import cos,sin,asin,acos,tan,radians,exp
from enum import Enum
from dataclasses import dataclass, field
import datetime
from geometry import GeoPosition, Orientation
from weather import Weather, WeatherParam as W
import pandas as pd
from pandas import DataFrame, Series
from components import Component
from econometrics import Cost
class CellType(Enum):
    """crystal cell configuration"""
    POLI = 'policristalino'
    MONO = 'monocristalino'
    
class TempCoef(Enum):
    OPEN_RACK={"alpha":-3.47,"beta":-0.0594,"deltaT":3}
    ROOF_MOUNT={"alpha":-2.98,"beta":-0.0471,"deltaT":1}

class PvParam(Enum):
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
@dataclass()
class PvTechnicalSheet:
    "solar plane power technical specification"
    power:int = 100
    area:float = 1 #m2
    efficiency = 0.15  # w/m2
    power_curve:PowerCurve = field(default_factory=PowerCurve)
    cell:Cell = field(default_factory=Cell)
    thermal:ThermalCoef = field(default_factory=ThermalCoef)


class Photovoltaic(Component):
    """
    PV primary component
    ~~~~
    global component for operate Weather fetch, solar irradiation calculus, and technical
    lost. Not include shadow analysis.
    >>>  methods
    ... .normal() -> normal azimuth and elevation
    ... .calc_cosPhi() -> angle between solar vector and surface normal vector
    ... .calc_irradiation() -> al irradiation received by an inclined surface.
    ... .calc_reflection() -> IAM reflection losses coefficient.
    ... .calc_energy() -> calc al lost, and irradiation performance to a nominal panel.

    """
    energy:DataFrame = pd.DataFrame()
    PARAMS:list[W] = [W.TEMPERATURE,W.DIRECT,W.DIFFUSE,W.ALBEDO,W.ZENITH,W.WIND_SPEED_10M]

    def __init__(
        self, 
        weather:Weather,
        description: str = 'Panel Fotovoltaico',
        model: str = 'generic',
        specification: str | None = None,
        cost: Cost = Cost(),
        quantity: int = 1,
        power:int = 100,
        orientation:Orientation = Orientation(),
        technical_sheet:PvTechnicalSheet = PvTechnicalSheet(),
        ) -> None:
        super().__init__(description, model, specification, cost, quantity)
        self.power = power
        self.orientation = orientation
        self.technical_sheet = technical_sheet
        self._weather = weather
        #init weather values
        self._weather.parameters =self.PARAMS
        weather_date = weather.get_data()
        #calc reusable cos_phi
        self._cos_phi:DataFrame = weather_date['date']\
            .apply(lambda date:self.calc_cos_phi(date=date,location=weather.geo_position))

    def normal(self)->dict[str,float]:
        """elevation and azimuth surface´s normal"""
        return {'azimuth':self.orientation.inclination,'elevation':self.orientation.inclination}

    def calc_cos_phi(self,date:datetime,location:GeoPosition)->float:
        """or angle between sun and normal or surface"""
        sun= location.sun_position(date)

        cos_phi = self.orientation.cos_phi(
            sun_azimuth=sun['azimuth'],
            sun_elevation=sun['elevation'])

        return cos_phi

    def calc_irradiation(self)->DataFrame:
        """calc irradiation on plane, direct,diffuse, ground and global on plane """
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
        reflection = self.calc_reflection()
        irr[PvParam.INCIDENT.value] = irr[PvParam.DIRECT.value]*reflection+irr[PvParam.GROUND.value]+irr[PvParam.DIFFUSE.value]
        irr.fillna(0.0,inplace=True)

        return irr

    def calc_reflection(self)->Series:
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
        reflex['phi']:DataFrame = self._cos_phi.apply(acos)
        reflex['phi_r']:DataFrame = reflex['phi'].apply(\
            lambda phi:asin(sin(phi)*(air_reflex/surface_reflex)\
                ))
        # print(reflex)

        #transmittance
        def tau_reflex(row:DataFrame)->float:
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
                
        transmittance_reflex = reflex.apply(tau_reflex,axis=1)

        #IAM
        iam = transmittance_reflex/tau_zero

        return iam

    def calc_temperature_cell(self,irradiance:DataFrame,coef:TempCoef=TempCoef.ROOF_MOUNT)->Series:
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
        def temperature_panel(row):
            return row[PvParam.INCIDENT.value]*exp(alpha+\
                beta*row[W.WIND_SPEED_10M.value])

        def temperature_cell(row):
            return temperature_panel(row) + row[PvParam.INCIDENT.value]*delta/1000

        t_cell_result = irradiance.apply(temperature_cell,axis=1)
        return t_cell_result
    
    def operational_loss(self)->float:
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
        
        total_loss = 0;
        for _,loss in model_loss.items():
            total_loss += loss
        
        return total_loss


    def calc_system_capacity(self,irradiation:DataFrame)->DataFrame:
        """
        System capacity Global [W]
        ~~~~
        """
        #capacity under lab conditions
        nominal_capacity:float = self.technical_sheet.area *\
            self.technical_sheet.efficiency *self.quantity
        #temperature performance
        t_cel:Series = self.calc_temperature_cell(irradiation)
        t_ref:float = 25.5 #C°
        gamma:float = self.technical_sheet.thermal.power_coef_t/100# %/C°
        irr_incident:Series = irradiation[PvParam.INCIDENT.value]
        dobo_limit = 125.0#W/m^2
        ref_irr = 1000#W/m^2

        #init calc system capacity
        system_capacity:DataFrame = pd.DataFrame()
        system_capacity[PvParam.T_CELL.value] = t_cel
        system_capacity[PvParam.INCIDENT.value] = irr_incident
        print(system_capacity.info())
        
        

        #system capacity
        def calc_capacity(row):
            #ref https://pvwatts.nrel.gov/downloads/pvwattsv5.pdf#page=9
            #data extract
            incident,t_cell = row[PvParam.INCIDENT.value],row[PvParam.T_CELL.value]

            if incident>= dobo_limit:
                return (nominal_capacity*incident/ref_irr) *\
                    nominal_capacity *\
                    (1+gamma*(t_cell-t_ref))


            return 0.008 * nominal_capacity * (incident**2 / ref_irr) *\
                nominal_capacity *\
                (1+gamma*(t_cell-t_ref))

        system_capacity[PvParam.SYS_CAP.value] = system_capacity.apply(calc_capacity,axis=1)
        
        #operational losses
        inverter_efficiency = 0.96
        op_loss = self.operational_loss()
        system_capacity[PvParam.SYS_CAP.value] = system_capacity[PvParam.SYS_CAP.value]\
            .apply(lambda cap: cap *inverter_efficiency* (1-op_loss))

        return system_capacity
    



    def calc_energy(self):
        """
        Module Energy Calc
        ~~~~
        ... ref: https://solar.minenergia.cl/downloads/fotovoltaico.pdf#page=3
        Calc energy generated for current instance, module with A surface and N quantity
        calc amount of energy generated by year"""
        #fetch nasa weather data
        weather_data = self._weather.get_data()

        #tempo init values for energy
        self.energy[['date','month','day','hour']] = weather_data[['date','month','day','hour']]


        #calc irradiation factors
        irradiation:DataFrame =self.calc_irradiation()
        print(irradiation.info())


        #calc system_capacity in KW 
        system_capacity = self.calc_system_capacity(irradiation=irradiation)

        return system_capacity


#short test
test_weather = Weather()
panel = Photovoltaic(weather=test_weather)
print(panel.calc_energy())
# End-of-file (EOF)