

class GeoPosition:
    def __init__(self,latitude:float,longitude:float,altitude:float|None = 0) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        
class Orientation:
    def __init__(self,inclination:float = 33.0,azimuth:float = 0) -> None:
        self.inclination = inclination,
        self.azimuth = azimuth;