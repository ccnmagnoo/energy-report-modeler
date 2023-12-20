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
    GNL = 'gas natural'
    OIL = 'petroleo'
    WOOD = 'leña'
    CARBON = 'carbón'


class Energy:
    """
    Energy consumption Item
    """
    def __init__(self,
                date_billing:date,
                energetic:Energetic=Energetic.ELI,
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