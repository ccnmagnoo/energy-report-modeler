"""main wrapper dependencies"""
from enum import Enum
import math
from typing import Any
from pandas import DataFrame
from models.consumption import Consumption, Energetic, EnergyBill
from models.econometrics import Currency
from models.emission import Emission
from models.geometry import GeoPosition
from models.components import Component, Tech
from models.photovoltaic import Photovoltaic
from models.weather import Weather,WeatherParam as W
import pandas as pd
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
    consumptions:dict[str,Consumption] ={}


    def __init__(self,
                geolocation:GeoPosition,
                name:str,
                address:str,
                city:str):
        self.geolocation = geolocation
        self.name=name
        self.address=address
        self.city=city

    def add_consumptions(
        self,
        description:str,
        energetic:Energetic,
        consumption:list[EnergyBill],
        ):
        '''defining energy bill, '''
        instance=Consumption(energetic)
        instance.set_bill(consumption)
        self.consumptions[description] = instance

    def consumption_forecast(self,group:list[str])->DataFrame:
        """return sum of all consumption groups in this building"""
        container:DataFrame = self.consumptions[group[0]].forecast()
        if len(self.consumptions)>1:
            for it in group[1:]:
                calc = self.consumptions[it].forecast()
                container['energy'] = calc['energy'] + container['energy']
        return container


class Connection(Enum):
    """energy supply mode"""
    NETBILLING = "net-billing",
    ONGRID = "net supply mix",
    OFFGRID = "battery supply mix"


class Project:
    """
    Main Wrapper, globing all installs
    ~~~~
    ... building: @Building Class
    ... technology: @Tech Enum Class
    """
    components:dict[str,list[Component]] = {}
    power_production:DataFrame|None = None # local storage energy daily generation

    def __init__(
        self,
        title:str,
        building:Building,
        technology:list[Tech]|None = None,
        ) -> None:
        self.emissions = Emission()
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

    def energy_production(self, generation_group:str)->DataFrame|None:
        """extract and sum all energy generation component"""

        #check object local storage
        if self.power_production is not None:
            return self.power_production

        number_of_components  = len(self.components[generation_group])

        #check for generation component content
        if number_of_components == 0:
            raise ValueError('no component found')

        #check for Photovoltaic component
        for it in self.components[generation_group]:
            if not isinstance(it,Photovoltaic):
                raise ValueError(f'{it}is not a energy gen component')

        #proceed for loop addition
        container:DataFrame = self.components[generation_group][0].get_energy()
        if number_of_components>1:
            for it in self.components[generation_group][1:]:

                aux_component:DataFrame = it.get_energy()
                container['System_capacity_KW'] += aux_component['System_capacity_KW']

                container['Temperature_cell'] = \
                    (container['Temperature_cell'] + aux_component['Temperature_cell'])/2

                container['IRR_incident'] = \
                    (container['IRR_incident'] + aux_component['IRR_incident'])/2

        #storage in local param
        self.power_production:DataFrame = container

        return container

    def performance(self,consumptions:list[str],generation_group:str,connection:Connection = Connection.NETBILLING):
        production:DataFrame = self.energy_production(generation_group)[["month","System_capacity_KW"]].groupby(["month"],as_index=False).sum()

        future:DataFrame = self.building.consumption_forecast(consumptions)

        res = future.merge(right=production,how='left')
        res = res.rename(columns={'energy':'consumption','System_capacity_KW':'generation'})

        match connection:
            case Connection.NETBILLING:
                if res['generation']>=res['consumption']:
                    res['netbilling'] = res['generation']-res['consumption']
                    res['savings'] = res['consumption']
                else:
                    res['netbilling'] = 0
                    res['savings'] = res['generation']
        return res


    def nominal_power(self,generation_source:str)->Any:
        "system capacity in kW"
        components:list[Component|Photovoltaic]  = self.components[generation_source]

        if len(components)==0:
            raise ValueError('no component found')

        for it in components:
            if not isinstance(it,Photovoltaic):
                raise ValueError('no energy component found')

        power:list[float] = [fv.nominal_power() for fv in components]
        redux:float = 0.0
        for it in power:
            redux+= it

        return power

    def bucket_list(self,currency:Currency|None)->dict[str,Any]:
        "get all cost related by components"
        #generate bucket
        container:list[tuple[str,str,int,float,str]] = []
        total_cost:float = 0
        for gloss,item in self.components.items():
            for component in item:

                value,curr = component.total_cost_after_tax(currency)
                total_cost += value

                #auxiliary object
                obj_item = {
                    'gloss':gloss,
                    'description':component.description,
                    'quantity':component.quantity,
                    'cost_after_tax':value,
                    'currency':curr.value
                }
                container.append(obj_item)
        return {'cost':math.floor(total_cost*100)/100 ,'bucket':container}


    def get_context(self,generation_source)->dict[str,Any]:
        "return object with information for generate DOCX template"
        context = {
            #about this project
            "project_name": self.title,
            "project_type" : self.technology[0].value,
            "project_size":self.nominal_power(generation_source),
            "size_unit":"kW",
            "total_cost": self.bucket_list(Currency.CLP)["cost"],
            #site
            "building_name" : self.building.name,
            "city": self.building.city
        }
        return context