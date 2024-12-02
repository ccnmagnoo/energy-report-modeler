from abc import abstractmethod,ABC
from typing import Self

from pandas import DataFrame

from models.components import Component, Specs
from models.econometrics import Cost

class Generator(Component):
    """abstract generate unit"""
    _energy:DataFrame
    def __init__(self, description: str, specification: Specs | None = None, cost_per_unit: Cost = ..., quantity: int = 1) -> None:
        super().__init__(description, specification, cost_per_unit, quantity)
    
    @property
    def energy(self)->DataFrame:
        return self._energy
    @abstractmethod
    def get_energy(self)->DataFrame:
        """DataFrame with hourly generation"""
    @abstractmethod
    def nominal_power(self)->float:
        """get power in kilowatt"""
    @abstractmethod
    def __add__(self,other:Self)->Self:
        """add production"""
