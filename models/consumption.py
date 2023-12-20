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
    
@dataclass
class Property:
    """
    Fuel Chemical properties
    """
    calorific_power:float # kWh/unit
    density:float # weight/volume
    unit:str # billing unit measure kg,m3,...

    def energy_equivalent(self,quantity:float)->float:
        """returning kWh equivalent energy"""
        return self.calorific_power*quantity

properties:dict[Energetic,Property] = {
    Energetic.ELI: Property(calorific_power=1,density=1,unit='kWh'),
    Energetic.GNL: Property(calorific_power=12.53,density=341,unit='kg'),
    Energetic.DIESEL: Property(calorific_power=11.82,density=850,unit='kg'),
    Energetic.GLP:Property(calorific_power=12.69, density=350,unit='kg'),
    Energetic.GN: Property(calorific_power=40.474,density=0.737, unit='m3')
            }



class Energy:
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

class Electricity(Energy):
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