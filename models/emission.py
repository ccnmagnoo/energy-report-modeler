"""json module parser"""
from dateutil.relativedelta import relativedelta
import pandas as pd
from sklearn.linear_model import LinearRegression
from libs.emission_data import emission_data


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

    def annual_avg(self,year:int|None=None)->pd.DataFrame:
        """average emission per year"""
        if year is not None:
            data = self.data[["year","emission"]].groupby(['year'],as_index=False).mean()
            return data.loc[data.year == year,"emission"].iloc[0]

        return self.data[["year","emission"]].groupby(['year'],as_index=False).mean()

    def _reshape(self,series:pd.Series):
        return series.values.reshape(-1,1)

    def annual_projection(self,year:int)->float:
        """annual emission projection in Ton CO2/MWh"""
        data = self.annual_avg()
        lg = LinearRegression()
        #print("shape ",data.year.shape)
        # print("X => ", self._reshape(data.year))
        # print("y => ", self._reshape(data.emission))

        lg.fit(
            X=self._reshape(data.year),
            y=self._reshape(data.emission)
            )
        prediction = lg.predict([[year]])
        return prediction[0][0]

emission = Emission()
if __name__ == '__main__':
    emission.annual_projection(2024)