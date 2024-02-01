"""main wrapper dependencies"""
from models.consumption import Energetic, EnergyBill
from models.geometry import GeoPosition
from models.components import Component, Tech
from models.weather import Weather,WeatherParam as W
from models.photovoltaic import Photovoltaic

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
    consumption:dict[Energetic,list[EnergyBill]] = {}
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
    components:dict[str,list[Component]] = {}

    def __init__(
        self,
        title:str,
        building:Building,
        technology:list[Tech]|None = None,
        ) -> None:
        self.technology = technology or [Tech.PHOTOVOLTAIC]
        self.building = building
        self.title:str = title
        self.weather = Weather(building.geolocation,\
            [W.TEMPERATURE,W.DIRECT,W.DIFFUSE,W.ALBEDO,W.ZENITH,W.WIND_SPEED_10M])
        self.weather.get_data()

    def add_component(self,item:str,*args:Component):
        """
        Add component, in requires and identifier,
        """
        if item in self.components:
            self.components[item].append(args)

        self.components[item] = list(args)

    def add_consumption(self, energetic:Energetic,*energy_bills):
        """add energy bill with detailed consumptions data, 
        requires an energetic topic as electricity"""
        if energetic in self.building.consumption[energetic]:
            self.building.consumption[energetic].append(energy_bills)
        self.building.consumption[energetic] = list(energy_bills)