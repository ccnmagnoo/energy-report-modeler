from abc import ABC
from dataclasses import dataclass
import datetime
from enum import Enum

from models.econometrics import Cost


class Energetic(Enum):
    '''
    Energy source type
    ~~~~
    calorific power inferior : 
    ... https://ingemecanica.com/utilidades/objetos/tablas/calorifico/calor49.jpg
    
    '''
    ELI = 'electricidad'
    GLP = 'gas licuado'
    GNL = 'gas natural licuado',
    GN = 'gas natural cañería',
    DIESEL = 'diesel oil'
    WOOD = 'leña'
    CARBON = 'carbón'
    D95 = '95 octanos'

class Unit(Enum):
    '''Physical unit specification'''
    KG = 'kg',
    M3 = 'm³',
    KWH = 'kWh',
    M = 'm',
    LT = 'lt'

@dataclass
class Property:
    """
    Fuel Chemical properties
    """
    kwh_per_kg:float # kWh/unit
    kg_per_m3:float # kg/m3
    unit:Unit # billing unit measure kg,m3,...

    def energy_equivalent(self,quantity:float=0,measure_unit:Unit = Unit.KG)->float:
        """returning kWh equivalent energy"""
        if measure_unit == Unit.LT:
            return self.kwh_per_kg*quantity*1000/self.kg_per_m3
        
        return self.kwh_per_kg*quantity

properties:dict[Energetic,Property] = {
    Energetic.ELI: Property(kwh_per_kg=1,kg_per_m3=1,unit=Unit.KWH),
    Energetic.GNL: Property(kwh_per_kg=12.53,kg_per_m3=341,unit=Unit.KG),
    Energetic.DIESEL: Property(kwh_per_kg=11.82,kg_per_m3=850,unit=Unit.KG),
    Energetic.GLP:Property(kwh_per_kg=12.69, kg_per_m3=350,unit=Unit.KG),
    Energetic.GN: Property(kwh_per_kg=40.474,kg_per_m3=0.737, unit=Unit.M3)
            }



class EnergyBill(ABC):
    """
    Energy consumption Item
    >>>inputs
    date_billing = str format DD-MM-YYYY
    """
    def __init__(self,
                date_billing:str,
                energetic:Energetic,
                cost:Cost = Cost()
                ) -> None:
        self.energetic = energetic
        self.property = properties[energetic]
        self.cost = cost
        #date from string
        datestr = date_billing.split("-",maxsplit=3)
        datestr = [int(cal) for cal in datestr] 
        datestr.reverse()
        self.date_billing = datetime.datetime(*datestr)

class FareTension(Enum):
    '''fare type'''
    AT='AT',
    BT='BT'

class FareType(Enum):
    '''
    Fare contract model
    '''
    A1 = '1A',
    B1 = '1B',
    T2 = '2',
    T3 = '3PP',
    T41 = '4.1',
    T42 = '4.2',
    T43 = '4.3'

class FareSubType(Enum):
    '''
    Fare contract model
    '''
    PP = 'PP',
    PPP = 'PPP'

class Fare:
    '''Fare electric billing :default BT1A'''
    def __init__(self,
                tension:FareTension = FareTension.BT,
                contract:FareType = FareType.A1,
                sub_type:FareSubType|None = None
                ) -> None:
        self.tension = tension,
        self.contract = contract,
        self.sub_type = sub_type

    def get_fare(self)->str:
        '''return properly compose fare'''
        return self.tension + self.contract + self.sub_type

class ElectricityBill(EnergyBill):
    '''Electricity billing details consumption'''
    def __init__(self,
                consumption:int,
                date_billing: str,
                fare:Fare = Fare(),
                cost: Cost = Cost(),
                ) -> None:
        super().__init__(date_billing, Energetic.ELI, cost)
        self.energy_consumption = consumption
        self.energy_unit:Unit = Unit.KWH
        self.fare = fare

class Consumption:
    """global energy billing and estimate  projection in 12 month"""
    bucket:list[EnergyBill]=[]
    def __init__(self,energetic:Energetic) -> None:
        self.energetic = energetic

    def set_bill(self,billing:list[EnergyBill]|Energetic)->None:
        """set list o single billing"""
        if isinstance(billing) == list:
            # when is a bulk of bills
            if len(self.bucket) > 0:
                self.bucket = [*self.bucket,*billing]
            else:
                self.bucket = billing
        else:
            # when just a one bill
            if len(self.bucket) > 0:
                self.bucket = [*self.bucket,billing]
            else:
                self.bucket = [billing] # inventory (\r\n)
    def get_consumptions(self):
        """return a list of consumptions value"""
        return list(map(lambda bills:bills.energy_consumption,self.bucket))
# End-of-file (EOF)