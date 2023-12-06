"""photovoltaic model component"""
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
    """pv panel tech"""
    energy:DataFrame = pd.DataFrame()
    
    def __init__(
        self, description: str = 'Panel Fotovoltaico',
        model: str = 'generic',
        specification: str | None = None,
        cost: Cost = Cost(),
        quantity: int = 1,
        power:int = 100,
        orientation:Orientation = Orientation(),
        technical_sheet:PvTechnicalSheet = PvTechnicalSheet()
        ) -> None:
        super().__init__(description, model, specification, cost, quantity)
        self.power = power
        self.orientation = orientation
        self.technical_sheet = technical_sheet

    def normal(self)->dict[str,float]:
        """elevation and azimuth surface´s normal"""
        return {'azimuth':self.orientation.inclination,'elevation':self.orientation.inclination}

    def cos_phi(self,date:datetime,location:GeoPosition)->float:
        """or angle between sun and normal or surface"""
        sun= location.sun_position(date)

        cos_phi = self.orientation.cos_phi(
            sun_azimuth=sun['azimuth'],
            sun_elevation=sun['elevation'])

        return cos_phi

    def calc_energy(self,weather:Weather):
        """calc amount of energy generated by year"""
        #config params necessary for PV modules
        weather.parameters = [W.TEMPERATURE,W.DIRECT,W.DIFFUSE,W.ALBEDO,W.ZENITH]
        #fetch nasa weather data
        weather_data = weather.get_data()
        return weather_data
    #EOF (\n)
    