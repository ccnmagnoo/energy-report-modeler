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
    weatherData:DataFrame|None = None
    
    
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
        
    def _fetchWeatherData(self,weather:Weather):
                self.weatherData = weather.fetchData([WeatherParam.DIRECT,WeatherParam.DIFFUSE,WeatherParam.TEMPERATURE,WeatherParam.ZENITH])

    def calcGeneration(self,weather:Weather):
        #fetch nasa weather data
        if self.weatherData == None:
            self._fetchWeatherData(weather)
        

        return None #temp  

Modules = list[Component]

pack = Photovoltaic('Panel Policristalino 450W')
pack.calcGeneration(Weather())
print(pack.weatherData)

