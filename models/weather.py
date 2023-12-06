"""date dependency"""
from datetime import datetime,date
import json
from enum import Enum
from geometry import GeoPosition
import requests
import pandas as pd
from pandas import DataFrame

class WeatherParam(Enum):
    """NASA api parameters"""

    ATMOSPHERIC = 'TOA_SW_DWN'
    DIRECT = 'ALLSKY_SFC_SW_DNI'
    DIFFUSE = 'ALLSKY_SFC_SW_DIFF'
    ALBEDO = 'ALLSKY_SRF_ALB'
    TEMPERATURE = 'T2M'
    ZENITH = 'SZA'
    RAIN = 'PRECTOTCORR'
    INSOLATION_INDEX = 'ALLSKY_KT'
    PRESSURE = 'PS'
    WIND_SPEED_10M = 'WS10M'
    WIND_DIR_10M = 'WD10M'



class Weather:
    """store data fetch from api"""

    URL = 'https://power.larc.nasa.gov/api/temporal/hourly/point?'
    _data:DataFrame|None = None
    #https://power.larc.nasa.gov/api/temporal/hourly/point?
    # Time=LST
    # &parameters=SZA,T2M
    # &community=RE
    # &longitude=-71.2987
    # &latitude=-31.6322
    # &start=20210101
    # &end=20210331
    # &format=JSON
    def __init__(self,geo_position:GeoPosition = GeoPosition(),parameters:list[WeatherParam] = [WeatherParam.TEMPERATURE]) -> None:
        self.geo_position = geo_position
        self.period = self._last_period()
        self.parameters = parameters


    def _fetch_data(self)->None:
        request_url = self._generate_url()
        response = requests.get(request_url,timeout=10000)
        result = json.loads(response.text)


        #create a list of data list
        result_df = pd.DataFrame()
        for param,data_by_hour in result['properties']['parameter'].items():
            #data[param] = (hourlyData)
            column = pd.DataFrame(list(data_by_hour.items()),columns=['date',param])
            result_df[['date',param]] = column

        #split 'date' col
        result_df['year'] = result_df['date'].str[:4]
        result_df['month'] = result_df['date'].str[4:6]
        result_df['day'] = result_df['date'].str[6:8]
        result_df['hour'] = result_df['date'].str[-2:]

        #format date str to datetime
        result_df['date'] = result_df['date'].apply(
            lambda datestr: datetime.strptime(datestr,'%Y%m%d%H')
            )

        #remove al inconsistent values
        result_df = result_df.replace(-999.00,None)

        self._data = result_df

    #period 365 days interval corresponding previous year
    def _last_period(self)->dict[str,date]:
        current:datetime = datetime.now()
        last_year:int = current.date().year-1
        return {'start':date(last_year,1,1),'end':date(last_year,1,2)}

    def _date_api_format(self,user_date:date)->str:
        """return str with api YYYYMMDD format"""

        return str(user_date.year) + str(user_date.month) + str(user_date.day)

    def _generate_url(self)->str:
        param_chain = ','.join(map(lambda param:param.value,self.parameters))

        config = {
            'Time':'LST',
            'parameters':param_chain,
            'community':'RE',
            'latitude':self.geo_position.latitude,
            'longitude':self.geo_position.longitude,
            'start':self._date_api_format(self.period['start']),
            'end':self._date_api_format(self.period['end']),
            'format':'JSON'
        }

        request_components:list[str] = []
        
        for key,value in config.items():
            request_components.append(f'{key}={value}')
        request_url = self.URL+ '&'.join(request_components)
        print('api request URL',request_url)
        return request_url

    def get_data(self)->DataFrame:
        """get weather data from api, or one stored in instance"""
        if self._data is None:
            self._fetch_data()

        return self._data