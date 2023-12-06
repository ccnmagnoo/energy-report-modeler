"""data"""
from enum import Enum
from econometrics import Cost

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
        cost:Cost = Cost(),
        quantity:int = 1 ) -> None:
        self.description:str = description
        self.model:str = model
        self.specification:str|None = specification
        self.cost:float= cost
        self.quantity:int = quantity
    
    def total_brute_cost(self)->float:
        """cost before taxes"""
        return self.quantity*self.cost
    def total_cost_plus_taxes(self)->float:
        """cost after taxes"""
        return self.quantity*self.cost.netCost()
