

class GeoPosition:
    def __init__(self,latitude:float,longitude:float,altitude:float|None = 0) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        
class Orientation:
    def __init__(self,inclination:float = 33.0,azimuth:float = 0) -> None:
        self.inclination = inclination
        self.azimuth = azimuth
    
    def angleDifference(self, inclination:float,azimuth:float)->float:
        azimuthDelta:float = self.azimuth - azimuth
        inclinationDelta:float = self.inclination - inclination
        return (azimuthDelta**2 + inclinationDelta**2)**(1/2)
        