"""main wrapper dependencies"""
from geometry import GeoPosition
from models.components import Tech

class Building:

    def __init__(self,geolocation:GeoPosition,name:str,address:str,city:str):
        self.geolocation = geolocation
        self.name=name
        self.address=address
        self.city=city

class Project:
    """main wrapper"""
    def __init__(
        self,
        building:Building,
        technology:Tech = Tech.PHOTOVOLTAIC,
        ) -> None:
        self.technology = technology
        self.building = building
        self.name:str = f'Proyecto {technology} {building.name}'
