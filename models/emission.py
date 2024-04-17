"""json module parser"""
import pandas as pd
from libs.emission_data import emission_data


class Emission():
    """CO2 emission ratio for mWh SEN system,
    >>> Methods
    ... projection(period:"year"|"month")
    """
    def __init__(self) -> None:
        #load and transform data
        self.data = pd.DataFrame.from_dict(data=emission_data)

emission = Emission()