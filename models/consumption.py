from dataclasses import dataclass
from datetime import date
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



class EnergyBill:
    """
    Energy consumption Item
    """
    def __init__(self,
                date_billing:date,
                energetic:Energetic,
                cost:Cost = Cost()
                ) -> None:
        self.energetic = energetic
        self.cost = cost
        self.date_billing = date_billing

class ElectricityBill(EnergyBill):
    '''
    Electricity billing detail consumption
    '''
    def __init__(self, 
                contract_type:str,
                energy_consumption:int,
                date_billing: date,
                cost: Cost = Cost(),
                ) -> None:
        super().__init__(date_billing, Energetic.ELI, cost)
        self.energy_consumption = energy_consumption,
        self.energy_unit = 'kWh' 
        self.contract_type = contract_type,