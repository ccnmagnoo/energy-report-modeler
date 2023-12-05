from sun_position_calculator import SunPositionCalculator
from datetime import datetime
import math
class GeoPosition:
    def __init__(
        self,
        latitude:float=-31.6322,#seremi office lat
        longitude:float=-71.2987,#seremi office lng
        altitude:float|None = 0
        ) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        
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
# ts = date.timestamp()*100
# calculator = SunPositionCalculator()
# pos = calculator.pos(ts,-33,-71.5)

# print(math.degrees(pos.azimuth),90-math.degrees(pos.altitude))
