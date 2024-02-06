"""data"""
from enum import Enum

from models.econometrics import Cost, Currency


class Tech(Enum):
    """in this project will only use PV, but in the future will be expanded to other techs"""
    PHOTOVOLTAIC = 'fotovoltaico'
    SOLAR_THERMAL = 'solar térmico'


class Component:
    """each item in a project will be a component, as panels, invertor, etc"""
    def __init__(
        self,
        description:str,
        model:str = 'generic',
        specification:str|None = None,
        reference:str|None = None,
        cost_per_unit:Cost = Cost(),
        quantity:int = 1 ) -> None:
        
        self.description:str = description
        self.model:str = model
        self.specification:str|None = specification
        self.reference:str|None = reference

        self.cost:Cost= cost_per_unit
        self.quantity:int = quantity
    
    def total_cost_before_tax(self,currency:Currency|None)->tuple[float,Currency]:
        """cost before taxes"""
        return self.quantity*self.cost.cost_before_tax(currency)[0],currency or self.cost.currency
    def total_cost_after_tax(self,currency:Currency|None):
        """cost after taxes"""
        return self.quantity*self.cost.cost_after_tax(currency)[0],currency or self.cost.currency
