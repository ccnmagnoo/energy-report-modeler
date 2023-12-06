"""currency types dep"""
from enum import Enum


class Currency(Enum):
    """currency type"""
    #cspell:disable
    CLP ='peso chileno'
    USD ='dolar'
    EUR ='euro'

class Cost:
    """component cost dataclass"""
    IVA = 0.19
    def __init__(self, value:float = 0,currency:Currency = Currency.CLP) -> None:
        self.value:float = value
        self.currency:Currency = currency

    def tax(self)->float:
        """calc iva"""
        return self.value*self.IVA

    def net_cost(self)->float:
        """calcl cost+tax"""
        return self.tax() + self.value # LF (\n)