import math
from sun_position_calculator import SunPositionCalculator
from datetime import datetime
class GeoPosition:
    _calculator = SunPositionCalculator()
    def __init__(
        self,
        latitude:float=-31.6322,#viña del mar office lat
        longitude:float=-71.2987,#viña del mar office lng
        altitude:float|None = 0
        ) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
    
    def sunPosition(self,date:datetime)->dict[str,float]:#in degrees
        timestamp:float = date.timestamp()*1000
        pos = self._calculator.pos(timestamp,self.latitude,self.longitude)
        return {'azimuth':math.degrees(pos.azimuth),'elevation':math.degrees(pos.altitude)}
        
        
class Orientation:
    def __init__(self,inclination:float = 33.0,azimuth:float = 0) -> None:
        self.inclination = inclination
        self.normal:float = 90 - inclination
        self.azimuth = azimuth
    
    def angleDifference(self, inclination:float,azimuth:float)->float:
        azimuthDelta:float = self.azimuth - azimuth
        inclinationDelta:float = self.inclination - inclination
        return (azimuthDelta**2 + inclinationDelta**2)**(1/2)


# Create a datetime object from the string


##use this config
# date = datetime.utcnow()
# ts = date.timestamp()*1000
# calculator = SunPositionCalculator()
# pos = calculator.pos(ts,-33,-71.5)

# print(math.degrees(pos.azimuth),90-math.degrees(pos.altitude))
geo = GeoPosition()
dt = datetime.now()
print(geo.sunPosition(dt))