from enum import Enum
from pandas import DataFrame

class ProductionFormat(Enum):
    """format to deliver Energy production Calcs"""
    Y = "yearly"
    M = "monthly"
    D = "daily"
    H = "hourly"

class PowerProduction:
    """Energy DataFrame"""
    def __init__(self, production:DataFrame) -> None:
        self.production = production
