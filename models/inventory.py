"""main wrapper dependencies"""
from models.geometry import GeoPosition
from models.components import Tech
from models.weather import Weather,WeatherParam as W

class Building:
    """
    Site configuration
    ~~~~
    >>> initializer
    ... geolocation
    ... name
    ... address
    ... city

    building config like geolocation, name and basics operations"""
    def __init__(self,
                 geolocation:GeoPosition,
                 name:str,
                 address:str,
                 city:str):
        self.geolocation = geolocation
        self.name=name
        self.address=address
        self.city=city

class Project:
    """
    Main Wrapper, globing all installs
    ~~~~
    ... building: @Building Class
    ... technology: @Tech Enum Class

    """
    
    def __init__(
        self,
        building:Building,
        technology:list[Tech]|None = None,
        ) -> None:
        self.technology = technology or [Tech.PHOTOVOLTAIC]
        self.building = building
        self.name:str = f'Proyecto {technology[0]} {building.name}'
        self.weather = Weather(building.geolocation,\
            [W.TEMPERATURE,W.DIRECT,W.DIFFUSE,W.ALBEDO,W.ZENITH,W.WIND_SPEED_10M])
        self.weather.get_data()
