
from enum import Enum


class Currency(Enum):
    #cspell:disable
    CLP ='peso chileno'
    USD ='dolar'
    EUR = 'euro'

class Cost:
    IVA = 0.19
    def __init__(self, bruteCost:float = 0,currency:Currency = Currency.CLP) -> None:
        self.bruteCost:float = bruteCost
        self.currency = currency
    
    def tax(self):
        return self.bruteCost*self.IVA    
        
    def netCost(self):
        return self.tax() + self.bruteCost