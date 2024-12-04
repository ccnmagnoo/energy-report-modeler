from functools import reduce
from typing import Literal
from models.components import Component, Specs
from models.econometrics import Cost


class EnergyStorage(Component):
    """Any energy storage component as batteries"""
    def __init__(self,
                description: str,
                specifications:Specs,
                cost_per_unit: Cost = ...,
                storage:float = 0,
                quantity: int = 1,
                ) -> None:
        super().__init__(
            description,specifications,cost_per_unit,quantity)
        self.storage = storage

type Voltage = Literal[12,24,48,110,220,380,400]
class Battery(EnergyStorage):
    """Battery is set in function of certain demand
    >>> variables
    ...volt : 12/24/48...
    ...charge: in ampere-hour
    ...demand: array of 12 month energy energy demand by month
    ...autonomy: how many days of supply is specked
     """
    def __init__(
        self,
        description:str,
        specifications:Specs,
        cost_per_unit: Cost = ...,
        volt:Voltage=12,#volt
        charge:float=0,#A-h
        demand:list[float]|None = None,#kWh
        hours_autonomy:int=1,#number of hours
        use_regime:Literal['24/7','16/7','8/7','24/5','16/5','8/5',]='24/7',
        ) -> None:
        #battery specification
        storage:float = volt*charge/1000 # in KiloWatt-hour
        
        #regime extract
        days_per_week,hours_per_day = [int(it) for it in use_regime.split('/')]
        daily_avg_demand:float = reduce(lambda acc,next:acc+next,demand)/(days_per_week*52) \
            if demand is not None else 0#kwh per day
        
        hourly_avg_demand:float = daily_avg_demand/hours_per_day
        
        #size bank requirements
        quantity = hourly_avg_demand*hours_autonomy/storage
        quantity = int(round(quantity,0)) if quantity>=1 else 1

        super().__init__(
            description=description,
            specifications=specifications,
            cost_per_unit=cost_per_unit,
            storage=volt*charge,
            quantity=quantity
            )

        self.hours_autonomy = hours_autonomy
        self.charge = charge
        self.hourly_avg_demand = hourly_avg_demand
# End-of-file (EOF)