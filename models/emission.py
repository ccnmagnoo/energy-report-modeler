"""json module parser"""
from dateutil.relativedelta import relativedelta
import pandas as pd
from libs.emission_data import emission_data
from sklearn.linear_model import LinearRegression


class Emission():
    """CO2 emission ratio for mWh SEN system,
    >>> Methods
    ... projection(period:"year"|"month")
    """
    def __init__(self) -> None:
        #load and transform data
        data = pd.DataFrame.from_dict(data=emission_data)
        data["datetime"] = pd.to_datetime(dict(year=data['year'],month=data["month"],day=1))
        data["datetime"] = data["datetime"].apply(lambda it: it+relativedelta(months=1)+relativedelta(days=-1))
        data["emission"] = data["emission"].str.replace(",",".")
        data["emission"] = data["emission"].astype(float).fillna(0.0)
        data[["month","year"]] = data[["month","year"]].astype(int).fillna(0)
        self.data = data

    def annual_avg(self)->pd.DataFrame:
        """average emission per year"""
        return self.data[["year","emission"]].groupby(['year']).mean()
    
    def annual_projection(self,year)->float:
        """anual emission projection in Ton CO2/MWh"""
        data = self.annual_avg()
        reg = LinearRegression()
        reg.fit(X=data['year'],y=data['emission'])
        prediction = reg.predict(year) 
        return prediction

emission = Emission()