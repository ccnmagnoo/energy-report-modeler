from datetime import datetime,date
from enum import Enum
from geometry import GeoPosition
import requests
import json

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

    
    async def fetchData(self,parameters:list[Parameter])->None:
        requestURL = self._generateURL(parameters)
        response = requests.get(requestURL)
        data = json.loads(response.text)
        print('api result',data)
        
    
    def _lastPeriod(self)->dict[str,date]:
        current:datetime = datetime.now()
        previousYear:int = current.date().year-1
        return {'start':date(previousYear,1,1),'end':date(previousYear,12,31)}
    
    def _dateApiFormat(self,date:date)->str:
        return str(date.year) + str(date.month) + str(date.day)
    
        
    def _generateURL(self,parameters:list[Parameter],):
        config = {
            'Time':'LTS',
            'parameters':'parameters'+','.join(map(parameters,lambda param:param.value)),
            'community':'RE',
            'latitude':self.geoPosition.latitude,
            'altitude':self.geoPosition.altitude,
            'start':self._dateApiFormat(self.period['start']),
            'end':self._dateApiFormat(self.period['end']),
            'format':'JSON'
        }
        
        requestComponents:list[str] = []
        for key,value in config.items():
            requestComponents.append(f'{key}={value}')
        requestURL = self.URL+ '&'.join(requestComponents)
        print('api request URL',)
        
        return requestURL
            
        
        

        

        
