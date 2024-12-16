from abc import abstractmethod,ABC
from dataclasses import dataclass
from typing import Self
from pandas import DataFrame
from models.components import Component, Specs
from models.econometrics import Cost

class EnergyGenerator(ABC,Component):
    """abstract generate unit"""

    def __init__(self,
                description: str,
                specification: Specs | None = None,
                cost_per_unit: Cost = ...,
                quantity: int = 1) -> None:

        super().__init__(description, specification, cost_per_unit, quantity)

    @property
    @abstractmethod
    def energy(self)->DataFrame:
        """return energy produced by generator component"""

    @abstractmethod
    def get_energy(self)->DataFrame:
        """DataFrame with hourly generation"""
    @abstractmethod
    def nominal_power(self)->float:
        """get power in kilowatt"""
    @abstractmethod
    def __add__(self,other:Self)->Self:
        """add production"""

@dataclass
class GeneratorFactory(ABC):
    """class Factory Certain data"""
    @abstractmethod
    def factory(self)->EnergyGenerator:
        """return a Generator"""
    

class GeneratorInput(ABC):
    """data simplification input"""
    @property
    @abstractmethod
    def description(self)->str:
        """return description"""
    @property
    @abstractmethod
    def quantity(self)->int:
        """return description"""