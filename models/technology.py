from enum import Enum
from models.econometrics import Cost
from models.geometry import Orientation


class Tech(Enum):
    PHOTOVOLTAIC = 'fotovoltaico'
    SOLAR_THERMAL = 'solar térmico'


class Component:
    def __init__(
        self,
        description:str,
        model:str = 'generic',
        specification:str|None = None,
        cost:Cost = Cost(),
        quantity:int = 1 ) -> None:
        self.description = description
        self.model = model
        self.specification = specification
        self.cost = cost
        self.quantity = quantity
    
    def totalCost(self):
        return self.quantity*self.cost

class Photovoltaic(Component):
    def __init__(
        self, description: str, 
        model: str = 'generic', 
        specification: str | None = None, 
        cost: Cost = Cost(), 
        quantity: int = 1,
        power:int = 100,
        orientation:Orientation = Orientation()
        ) -> None:
        super().__init__(description, model, specification, cost, quantity)
        self.power = power
        self.orientation = orientation
        

Modules = list[Component]