"""cos sin op"""
import math
from datetime import datetime
from sun_position_calculator import SunPositionCalculator
class GeoPosition:
    """
    Geo position class
    ~~~~
    >>> params
        ... latitude: degrees = -33°
        ... longitude: degrees = -71°
        ... altitude: degrees = None
    >>> methods
        ... .sun_position(datetime)->{elevation:degrees°,azimuth:degrees°}
        azimuth = 0° north,
        azimuth = 180° south
    """
    _calculator = SunPositionCalculator()
    def __init__(
        self,
        latitude:float=-31.6322,#default lat
        longitude:float=-71.2987,#default lng
        altitude:float|None = 0
        ) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude

    def sun_position(self,date:datetime)->dict[str,float]:#in degrees
        """elevation and azimuth of the king sun, in degrees"""
        timestamp:float = date.timestamp()*1000
        pos = self._calculator.pos(timestamp,self.latitude,self.longitude)
        return {'azimuth':math.degrees(pos.azimuth),'elevation':math.degrees(pos.altitude)}

    @property
    def gmaps(self)->str:
        """return google maps link"""
        return f'https://www.google.com/maps/@{self.latitude},{self.longitude},200m/data=!3m1!1e3?entry=ttu'

class Orientation:
    "elevation and azimuth in degrees"
    def __init__(self,inclination:float = 33.0,azimuth:float = 0) -> None:
        self.inclination = inclination
        self.normal:float = inclination
        self.azimuth = azimuth

    def cos_phi(self, sun_azimuth:float,sun_elevation:float)->float:
        """cos(Phi), phi: difference between normal and sun position, angles input in degrees"""
        [x_sun,y_sun,z_sun] = [
            math.cos(math.radians(sun_elevation))*math.cos(math.radians(sun_azimuth)),
            math.cos(math.radians(sun_elevation))*math.sin(math.radians(sun_azimuth)),
            math.sin(math.radians(sun_elevation))
            ]

        normal = {'elevation':self.inclination,'azimuth':self.azimuth}
        [x_nor,y_nor,z_nor] = [
            math.sin(math.radians(normal['elevation']))*math.cos(math.radians(normal['azimuth'])),
            math.sin(math.radians(normal['elevation']))*math.sin(math.radians(normal['azimuth'])),
            math.cos(math.radians(normal['elevation']))
            ]
        cos_phi = x_sun*x_nor + y_sun*y_nor + z_sun*z_nor
        return cos_phi if cos_phi>=0 else 0

# Create a datetime object from the string


##use this config
# date = datetime.utcnow()
# ts = date.timestamp()*1000
# calculator = SunPositionCalculator()
# pos = calculator.pos(ts,-33,-71.5)

# print(math.degrees(pos.azimuth),90-math.degrees(pos.altitude))
# geo = GeoPosition()
# dt = datetime.now()
# print(geo.sun_position(dt))