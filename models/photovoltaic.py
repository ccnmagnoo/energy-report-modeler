"""photovoltaic model component"""
from math import cos,sin,asin,acos,tan,radians,exp
from enum import Enum
from dataclasses import dataclass, field
import datetime
from geometry import GeoPosition, Orientation
from weather import Weather, WeatherParam as W
import pandas as pd
from pandas import DataFrame
from components import Component
from econometrics import Cost
class CellType(Enum):
    """crystal cell configuration"""
    POLI = 'policristalino'
    MONO = 'monocristalino'

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
    """thermal behavior panel, units %/C° """
    short_circuit_t:float = 0.0814
    open_circuit_t:float = -0.3910
    power_coef_t:float = -0.5141
@dataclass()
class PvTechnicalSheet:
    "solar plane power technical specification"
    power:int = 100
    power_curve:PowerCurve = field(default_factory=PowerCurve)
    cell:Cell = field(default_factory=Cell)
    thermal:ThermalCoef = field(default_factory=ThermalCoef)


class Photovoltaic(Component):
    """
    PV primary component
    ~~~~
    
    global component for operate Weather fetch, solar irradiation calculus, and technical
    lost. Not include shadow analysis.
    ... .normal() -> normal azimuth and elevation
    ... .calc_cosPhi() -> angle between solar vector and surface normal vector
    ... .calc_irradiation() -> al irradiation received by an inclined plane
    ... .calc_energy() -> calc al lost, and irradiation performance to a nominal panel.

    """
    energy:DataFrame = pd.DataFrame()
    PARAMS:list[W] = [W.TEMPERATURE,W.DIRECT,W.DIFFUSE,W.ALBEDO,W.ZENITH]

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
        irradiation:DataFrame = pd.DataFrame()
        weather_data = self._weather.get_data()

        # irradiation['IRR_dir_plane'] = weather_data[W.DIRECT.value] * weather_data['date'].apply(
        #     lambda date:self.calc_cos_phi(
        #         date=date,
        #         location=self._weather.geo_position))
        irradiation['IRR_dir_plane'] = weather_data[W.DIRECT.value] * self._cos_phi
        # irradiation['cos_phi'] = weather_data['date'].apply(
        # lambda date:self.calc_cos_phi(
        #     date=date,
        #     location=self._weather.geo_position))
        irradiation['cos_phi'] = self._cos_phi

        cos_b = (1+cos(radians(self.orientation.inclination)))

        irradiation['IRR_dif_plane'] = weather_data[W.DIFFUSE.value] * 0.5 * cos_b

        irradiation['IRR_ground'] = weather_data[W.DIRECT.value] * 0.5 * \
            weather_data[W.ALBEDO.value] * cos_b

        return irradiation

    def calc_reflection(self)->DataFrame:
        '''
        reflection Module
        ~~~~
        the reflection of radiation on the panel cover is one 
        of the elements that is relevant in terms of losses.
        The parameter that characterizes the loss by reflection
        
        >>> is called modification by angle of incidence (IAM).
        
        ... The reflected amount depends on the material 
        ... of the cover and its thickness.
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
        def tau_reflex(phi:float,phi_r:float)->float:
            tau =  exp(-1* glass_extinction*thickness/(cos(phi_r)))*\
            (1 -0.5*(\
                (sin(phi_r-phi)**2 / sin(phi_r+phi)**2) +\
                (tan(phi_r-phi)**2 / tan(phi_r+phi)**2) \
                    ))
            return tau if tau>0.01 else 0

        # transmittance_reflex:DataFrame = reflex[['phi','phi_r']].apply(lambda it: \
        #     exp(-1* glass_extinction*thickness/(cos(it['phi_r'])))*\
        #     (1 -0.5*(\
        #         sin(it['phi_r']-it['phi'])**2 / sin(it['phi_r']+it['phi'])**2 +\
        #         tan(it['phi_r']-it['phi'])**2 / tan(it['phi_r']+it['phi'])**2 )))
        transmittance_reflex = reflex.apply(lambda it:tau_reflex(it['phi'],it['phi_r']),axis=1)

        #transmittance on phi == 0°
        transmittance_zero:float = exp(-1*glass_extinction*thickness)*\
                (1-((1-surface_reflex)/(1+surface_reflex))**2)

        #IAM
        iam:DataFrame = transmittance_reflex/transmittance_zero

        return iam

    def calc_energy(self):
        """calc amount of energy generated by year"""
        #config params necessary for PV modules
        # self._weather.parameters = [W.TEMPERATURE,W.DIRECT,W.DIFFUSE,W.ALBEDO,W.ZENITH]
        #fetch nasa weather data
        weather_data = self._weather.get_data()
        #tempo init values for energy
        self.energy[['date','month','day','hour']] = weather_data[['date','month','day','hour']]
        
        irr =self.calc_irradiation()
        self.energy = self.energy.join(irr)
        
        return self.energy
    #EOF (\n)



test_weather = Weather()
panel = Photovoltaic(weather=test_weather)
print(panel.calc_energy())
print(panel.calc_reflection())
# End-of-file (EOF)