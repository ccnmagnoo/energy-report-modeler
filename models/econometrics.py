"""currency types dep"""
from enum import Enum
from math import floor
from typing import Self

def curr_round(value:float,padding:int)->float:
    """round currency value"""
    return floor(value*padding*10)/(padding*10)


class Currency(Enum):
    """currency type"""
    #cspell:disable
    CLP ='Pesos chileno'
    USD ='Dolar'
    EUR ='Euro'
    UF = 'UF'
    GBP = 'Pound'
    BRL = 'Real'
    UTM = 'UTM'


class Cost:
    """component cost dataclass"""
    IVA = 0.19
    _exchange = {
        Currency.USD:1.0,
        Currency.CLP:900.0,
        Currency.EUR:0.9,
        Currency.UF:0.026,
        Currency.UTM:0.01482679,
        Currency.GBP:0.78,
        Currency.BRL:5.03
        } # values in 1 dolar

    def __init__(self, net_value:float = 0,currency:Currency = Currency.CLP) -> None:
        self.value:float = round(net_value,2)
        if self._exchange_is_loaded(currency):
            self.currency:Currency = currency
        else:
            raise ValueError(f'{currency}\'s exchange ratio don´t exist')


    def tax(self,output_currency:Currency=None)->tuple[float,Currency]:
        """calc iva"""
        if output_currency:
            return self.value*self.IVA,output_currency

        return self.value*self.IVA*self._exchange_ratio(self.currency,output_currency),self.currency

    def net(self,output_currency:Currency=None)->tuple[float,Currency]:
        """calcl cost+tax"""
        if not output_currency:
            return self.value,self.currency
        #print(f'_exchange_ratio result: {self._exchange_ratio(self.currency,output_currency)}')
        
        rounded = curr_round(self.value*self._exchange_ratio(self.currency,output_currency),2)

        return rounded,output_currency # LF (\n)

    def gross(self,output_currency:Currency=None)->tuple[float,Currency]:
        """calcl cost+tax"""
        if output_currency is None:
            return [self.tax(None)[0] + self.net(None)[0],self.currency]

        rounded = curr_round(self.tax(output_currency)[0] + self.net(output_currency)[0],2)
        return rounded,output_currency # LF (\n)

    @classmethod
    def _exchange_ratio (cls,input_curr:Currency,output_curr:Currency)->float:
        """calc exchange ratio convertion"""
        if not output_curr:
            return 1
        if not cls._exchange_is_loaded(input_curr) and not cls._exchange_is_loaded(output_curr):
            return None
        return cls._exchange[output_curr]/cls._exchange[input_curr] #exchange ratio

    @classmethod
    def _exchange_is_loaded(cls, curr:Currency)->bool:
        exist = curr in cls._exchange
        #print(f'{curr} exchange ratios load status: {exist}')
        return exist

    @classmethod
    def set_exchange(cls,currency:Currency,exchange:float):
        '''set exchange values for cost'''
        if currency==Currency.USD:
            return print('USD can´t be modify')
        print(f'set $1 {currency.value:.<15} on USD${1/exchange:.2f} ')
        cls._exchange[currency] = exchange

    @classmethod
    def set_iva(cls,tax:int)->None:
        """set IVA in a class level"""
        if tax >= 1 and tax<=100:
            cls.IVA:float = tax/100
        else:
            raise ValueError(f'IVA:{tax}, must be between-> 1 & 100')


    def __str__(self)->str:
        return f'{self.currency.name} $ {self.net()[0]:,.0f}'

    def __format__(self,fmt:str)->str:
        _fmt,_curr = fmt.split('.')
        match _fmt:
            case 'net': return f'{Currency[_curr].name} $ {self.net(Currency[_curr])[0]:,.0f}'
            case 'gross': return f'{Currency[_curr].name} $ {self.gross(Currency[_curr])[0]:,.0f}'
            case _: return f'{Currency[_curr].name} $ {self.gross(Currency[_curr])[0]:,.0f}'

    def __add__(self,other:Self)->Self:
        oc,_ = other.net(self.currency)
        return Cost(self.value+oc,self.currency)

    def __float__(self)->float:
        """return net worth value, without tax"""
        return self.net()[0]
