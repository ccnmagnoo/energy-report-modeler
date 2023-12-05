from datetime import datetime,date
from enum import Enum
import pprint
from geometry import GeoPosition
import requests
import json
import pandas as pd
from pandas import DataFrame

class WeatherParam(Enum):
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
    
    def __init__(self,geoPosition:GeoPosition = GeoPosition(),parameters:list[WeatherParam] = [WeatherParam.TEMPERATURE]) -> None:
        self.geoPosition = geoPosition
        self.period = self._lastPeriod()
        self.parameters = parameters

    
    def _fetchData(self)->None:
        requestURL = self._generateURL()
        response = requests.get(requestURL)
        result = json.loads(response.text)
        
        data:dict[str,list[dict[str,float]]] = {}
        
        #create a list of data list
        resultDf = pd.DataFrame()
        for param,hourlyData in result['properties']['parameter'].items():
            #data[param] = (hourlyData)
            colData = pd.DataFrame(list(hourlyData.items()),columns=['date',param])
            resultDf[['date',param]] = colData
          
        #split 'date' col
        resultDf['year'] = resultDf['date'].str[:4]
        resultDf['month'] = resultDf['date'].str[4:6]
        resultDf['day'] = resultDf['date'].str[6:8]
        resultDf['hour'] = resultDf['date'].str[-2:]
        #format date str to datetime
        resultDf['date'] = resultDf['date'].apply(lambda datestr: datetime.strptime(datestr,'%Y%m%d%H'))
        #remove al inconsistent values
        resultDf = resultDf.replace(-999.00,None)
               
        self._data = resultDf
        
    #period 365 days interval corresponding previous year
    def _lastPeriod(self)->dict[str,date]:
        current:datetime = datetime.now()
        previousYear:int = current.date().year-1
        return {'start':date(previousYear,1,1),'end':date(previousYear,1,2)}
    
    #return YYYYMMDD
    def _dateApiFormat(self,date:date)->str:
        return str(date.year) + str(date.month) + str(date.day)
    
        
    def _generateURL(self):
        paramChain = ','.join(map(lambda param:param.value,self.parameters))
        
        config = {
            'Time':'LST',
            'parameters':paramChain,
            'community':'RE',
            'latitude':self.geoPosition.latitude,
            'longitude':self.geoPosition.longitude,
            'start':self._dateApiFormat(self.period['start']),
            'end':self._dateApiFormat(self.period['end']),
            'format':'JSON'
        }
        
        requestComponents:list[str] = []
        for key,value in config.items():
            requestComponents.append(f'{key}={value}')
        requestURL = self.URL+ '&'.join(requestComponents)
        print('api request URL',requestURL)
        
        return requestURL
    
    def getData(self)->DataFrame:
        if self._data == None:
             self._fetchData()
             return self._data
        return self._data

          
test =Weather()
data = test.getData()

print(data)
        

        
