"""main wrapper dependencies"""
from pandas import DataFrame
from models.consumption import Energetic, EnergyBill
from models.econometrics import Currency
from models.geometry import GeoPosition
from models.components import Component, Tech
from models.photovoltaic import Photovoltaic
from models.weather import Weather,WeatherParam as W
# from models.photovoltaic import Photovoltaic

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

    def add_component(self,item:str,*args:Component|Photovoltaic):
        """
        Add component, in requires and identifier,
        """
        if item in self.components:
            self.components[item].append(args)

        self.components[item] = list(args)

    def get_energy(self, generation_source:str)->DataFrame|None:
        """extract and sum all energy generation component"""
        number_of_components  = len(self.components[generation_source])

        #check for generation component content
        if number_of_components == 0:
            raise ValueError('no component found')

        #check for Photovoltaic component
        for energy_component in self.components[generation_source]:
            if not isinstance(energy_component,Photovoltaic):
                raise ValueError(f'{energy_component}is not a energy gen component')

        #proceed for loop addition
        container:DataFrame = self.components[generation_source][0].get_energy()
        if number_of_components>1:
            for energy_component in self.components[generation_source][1:]:
                aux_component:DataFrame = energy_component.get_energy()
                container['System_capacity_KW'] += aux_component['System_capacity_KW']
                container['Temperature_cell'] = (container['Temperature_cell'] + aux_component['Temperature_cell'])/2
                container['IRR_incident'] = (container['IRR_incident'] + aux_component['IRR_incident'])/2

        return container

    def bucket_list(self,currency:Currency|None)->dict[str,str|float]:
        "get all cost related by components"
        container:list[tuple[str,str,float,str]] = []
        for gloss,item in self.components.items():
            for component in item:

                value,curr = component.total_cost_after_tax(currency)

                #auxiliary object
                obj_item = {
                    'gloss':gloss,
                    'description':component.description,
                    'quantity':component.quantity,
                    'cost_after_tax':value,
                    'currency':curr.value
                }
                container.append(obj_item)
        return container

    def add_consumption(self, energetic:Energetic,*energy_bills):
        """add energy bill with detailed consumptions data, 
        requires an energetic topic as electricity"""

        if energetic in self.building.consumption[energetic]:
            self.building.consumption[energetic].append(energy_bills)
        self.building.consumption[energetic] = list(energy_bills)