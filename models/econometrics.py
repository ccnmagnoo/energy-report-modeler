"""currency types dep"""
from enum import Enum
from math import floor

def curr_round(value:float,padding:int)->float:
    return floor(value*padding*10)/(padding*10)
    

class Currency(Enum):
    """currency type"""
    #cspell:disable
    CLP ='peso chileno'
    USD ='dolar'
    EUR ='euro'
    UF = 'UF'
    UTM = 'UTM'

class Cost:
    """component cost dataclass"""
    IVA = 0.19
    _exchange = {Currency.USD:1,Currency.CLP:900,Currency.EUR:0.9,Currency.UF:0.026,Currency.UTM:0.01482679} # values in 1 dolar

    def __init__(self, value:float = 0,currency:Currency = Currency.CLP) -> None:
        self.value:float = value
        self.currency:Currency = currency


    def tax(self,output_currency:Currency|None)->float:
        """calc iva"""
        if output_currency:
            return self.value*self.IVA

        return self.value*self.IVA*self._exchange_ratio(self.currency,output_currency)

    def cost_before_tax(self,output_currency:Currency|None)->tuple[float,Currency]:
        """calcl cost+tax"""
        if not output_currency:
            return [self.value,self.currency]
        rounded = curr_round(self.value*self._exchange_ratio(self.currency,output_currency),2)

        return rounded,output_currency # LF (\n)

    
    def cost_after_tax(self,output_currency:Currency|None)->tuple[float,Currency]:
        """calcl cost+tax"""
        if not output_currency:
            return [self.tax(None) + self.cost_before_tax(None)[0],self.currency]
        
        rounded = curr_round(self.tax(output_currency) + self.cost_before_tax(output_currency)[0],2)
        return rounded,output_currency # LF (\n)
    
    @classmethod
    def _exchange_ratio (cls,input_curr:Currency,output_curr:Currency|None)->float:
        """calc exchange ratio convertion"""
        if not output_curr:
            return 1
        return cls._exchange[output_curr]/cls._exchange[input_curr] #exchange ratio

    @classmethod
    def set_exchange(cls,currency:Currency,exchange:float):
        '''set exchange values for cost'''
        if currency==Currency.USD:
            return print('USD can´t be modify')
        cls._exchange[currency] = exchange
