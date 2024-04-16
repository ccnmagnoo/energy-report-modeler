"""json module parser"""
import json
import pandas as pd
from pandas import DataFrame


class Emission():
    """CO2 emission ratio for mWh SEN system,
    >>> Methods
    ... projection(period:"year"|"month")
    """
    def __init__(self) -> None:
        #load and transform data
        with open("../libs/emission_data.json") as file:
            js = json.load(file)
            df:DataFrame = pd.read_json(js)

        self.data = df

data = Emission()