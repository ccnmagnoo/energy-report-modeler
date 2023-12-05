from datetime import datetime,date
from enum import Enum
import pprint
from geometry import GeoPosition
import requests
import json
import pandas as pd
from pandas import DataFrame

class Parameter(Enum):
    DIRECT = 'ALLSKY_SFC_SW_DNI'
    DIFFUSE = 'ALLSKY_SFC_SW_DIFF'
    ALBEDO = 'ALLSKY_SRF_ALB'
    TEMPERATURE = 'T2M'
    ZENITH = 'SZA'



class Weather:
    URL = 'https://power.larc.nasa.gov/api/temporal/hourly/point?'
    #https://power.larc.nasa.gov/api/temporal/hourly/point?
    # Time=LST
    # &parameters=SZA,T2M
    # &community=RE
    # &longitude=-71.2987
    # &latitude=-31.6322
    # &start=20210101
    # &end=20210331
    # &format=JSON
    
    def __init__(self,geoPosition:GeoPosition) -> None:
        self.geoPosition = geoPosition
        self.period = self._lastPeriod()

    
    def fetchData(self,parameters:list[Parameter])->DataFrame:
        requestURL = self._generateURL(parameters)
        response = requests.get(requestURL)
        result = json.loads(response.text)
        
        data:dict[str,list[dict[str,float]]] = {}
        
        #create a list of data list
        resultDataFrame = pd.DataFrame()
        for param,hourlyData in result['properties']['parameter'].items():
            #data[param] = (hourlyData)
            colData = pd.DataFrame(list(hourlyData.items()),columns=['date',param])
            resultDataFrame[['date',param]] = colData
          
        #loop for left right merge
               
        return resultDataFrame
        
    #period 365 days interval corresponding previous year
    def _lastPeriod(self)->dict[str,date]:
        current:datetime = datetime.now()
        previousYear:int = current.date().year-1
        return {'start':date(previousYear,1,1),'end':date(previousYear,1,2)}
    
    #return YYYYMMDD
    def _dateApiFormat(self,date:date)->str:
        return str(date.year) + str(date.month) + str(date.day)
    
        
    def _generateURL(self,parameters:list[Parameter],):
        paramChain = ','.join(map(lambda param:param.value,parameters))
        
        config = {
            'Time':'LTS',
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
            
test =Weather(GeoPosition(latitude=-33,longitude=-71))
data = test.fetchData([Parameter.TEMPERATURE,Parameter.ALBEDO])

print(data)
        

        
