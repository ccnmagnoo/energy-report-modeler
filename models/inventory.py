"""main wrapper dependencies"""
from models.consumption import Energetic, EnergyBill
from models.geometry import GeoPosition
from models.components import Component, Tech
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
    consumption:dict[Energetic,list[EnergyBill]] = {
        Energetic.ELI:[]
    }
    def __init__(self,
                geolocation:GeoPosition,
                name:str,
                address:str,
                city:str):
        self.geolocation = geolocation
        self.name=name
        self.address=address
        self.city=city
       
    def set_consumption(self,consumption:dict[Energetic,list[EnergyBill]]):
        '''defining energy bill, '''
        self.consumption = consumption
class Project:
    """
    Main Wrapper, globing all installs
    ~~~~
    ... building: @Building Class
    ... technology: @Tech Enum Class
    """
    components:dict[str,list[Component]] = {
            'generation':list[Component],
            'operation':list[Component],
            'installation':list[Component]}
 
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
