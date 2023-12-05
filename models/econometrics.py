
from enum import Enum


class Currency(Enum):
    #cspell:disable
    CLP ='peso chileno'
    USD ='dolar'
    EUR ='euro'

class Cost:
    IVA = 0.19
    def __init__(self, value:float = 0,currency:Currency = Currency.CLP) -> None:
        self.value:float = value
        self.currency:Currency = currency
    
    def tax(self)->float:
        return self.bruteCost*self.IVA    
        
    def netCost(self)->float:
        return self.tax() + self.bruteCost