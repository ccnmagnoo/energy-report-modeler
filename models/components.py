"""data"""
from enum import Enum


if __name__ == "__main__":
    from econometrics import Cost,Currency
else:
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
        
    
    def set_quantity(self, q:int):
        if q>0:
            self.quantity = q

    def total_cost_before_tax(self,currency:Currency|None)->tuple[float,Currency]:
        """cost before taxes"""
        return self.quantity*self.cost.cost_before_tax(currency)[0],currency or self.cost.currency
    def total_cost_after_tax(self,currency:Currency|None):
        """cost after taxes"""
        return self.quantity*self.cost.cost_after_tax(currency)[0],currency or self.cost.currency

type Package = dict[str,list[Component]]
class Assembly:
    """list of components"""
    package:Package = {}

    def __init__(self,group:str,*comp:Component) -> None:
        if group not in self.package:
            ##init
            self.package[group] = []
        self.package[group]:list[Component] = [*self.package[group],*comp] # type: ignore

    def __getitem__(self,group:str)->list[Component]:
        if group not in self.package:
            raise ValueError('no group on list ->',list(self.package.keys()))
        return self.package[group]


#manual test
if __name__ == "__main__":
    com1 = Component('test')
    com2 = Component('test')
    com3 = Component('test')
    ass = Assembly("energético",com1,com2,com3)
    

    print(ass["energétic"])