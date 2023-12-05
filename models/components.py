import datetime
from enum import Enum
import math
from econometrics import Cost
from geometry import GeoPosition, Orientation
from weather import Weather, WeatherParam
import pandas as pd
from pandas import DataFrame


class Tech(Enum):
    PHOTOVOLTAIC = 'fotovoltaico'
    SOLAR_THERMAL = 'solar térmico'


class Component:
    def __init__(
        self,
        description:str,
        model:str = 'generic',
        specification:str|None = None,
        cost:Cost = Cost(),
        quantity:int = 1 ) -> None:
        self.description:str = description
        self.model:str = model
        self.specification:str|None = specification
        self.cost:float= cost
        self.quantity:int = quantity
    
    def totalBruteCost(self)->float:
        return self.quantity*self.cost
    def totalNetCost(self)->float:
        return self.quantity*self.cost.netCost()

class Photovoltaic(Component):
    energy:DataFrame = pd.DataFrame()
    
    
    def __init__(
        self, description: str, 
        model: str = 'generic', 
        specification: str | None = None, 
        cost: Cost = Cost(), 
        quantity: int = 1,
        power:int = 100,
        orientation:Orientation = Orientation()
        ) -> None:
        super().__init__(description, model, specification, cost, quantity)
        self.power = power
        self.orientation = orientation
        
    def normalDirection(self)->dict[str,float]:
        return {'azimuth':self.orientation.inclination,'elevation':self.orientation.inclination}
    
    def cosPhi(self,date:datetime,location:GeoPosition)->float:
        #or angle between sun and normal or surface
        # https://www.cdeep.iitb.ac.in/slides/S20/EN301/EN301-L8.pdf
            # Sun:
            # X_sun = cos(elevation_sun) * cos(azimuth_sun)
            # Y_sun = cos(elevation_sun) * sin(azimuth_sun)
            # Z_sun = sin(elevation_sun)
            # Para la normal del surface:
            # X_normal = sin(inclination_surface) * cos(azimuth_surface)
            # Y_normal = sin(inclination_surface) * sin(azimuth_surface)
            # Z_normal = cos(inclination_surface)
            # cos(θ) = X_sun * X_normal + Y_sun * Y_normal + Z_sun * Z_normal
        # 
            
        sun= location.sunPosition(date)

        [xSun,ySun,zSun] = [
            math.cos(math.radians(sun['elevation']))*math.cos(math.radians(sun['azimuth'])),
            math.cos(math.radians(sun['elevation']))*math.sin(math.radians(sun['azimuth'])),
            math.sin(math.radians(sun['elevation']))
            ]
        normal = self.normalDirection()

        [xNor,yNor,zNor] = [
            math.sin(math.radians(normal['elevation']))*math.cos(math.radians(normal['azimuth'])),
            math.sin(math.radians(normal['elevation']))*math.sin(math.radians(normal['azimuth'])),
            math.cos(math.radians(normal['elevation']))
            ]
        cosPhi = xSun*xNor + ySun*yNor + zSun*zNor
        return cosPhi

    def calcGeneration(self,weather:Weather):
        #fetch nasa weather data
        data = weather.getData()
     
        

        return None #temp  

Modules = list[Component]

pack = Photovoltaic('surface Policristalino 450W')

print(pack.weatherData)

