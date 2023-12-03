
from enum import Enum
from geometry import GeoPosition
from models.technology import Component, Modules, Photovoltaic, Tech

class Building:
    def __init__(self,geolocation:GeoPosition,name:str,address:str,city:str):
        self.geolocation = geolocation
        self.name=name
        self.address=address
        self.city=city
        

        
class Project:
    def __init__(
        self,
        building:Building,
        components:dict[str,Modules],
        technology:Tech = Tech.PHOTOVOLTAIC,
        ) -> None:
        self.technology = technology
        self.building = building
        self.name:str = f'Proyecto {technology} {building.name}'
