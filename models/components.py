from enum import Enum
from econometrics import Cost
from geometry import Orientation
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
        

    def calcGeneration(self,weather:Weather):
        #fetch nasa weather data
        data = weather.getData()
     
        

        return None #temp  

Modules = list[Component]

pack = Photovoltaic('Panel Policristalino 450W')

print(pack.weatherData)

