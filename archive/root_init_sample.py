#cspell:disable
"""Muestra conservada del antiguo __init__.py de la raíz.

No importar este archivo: crea un Project y consulta NASA POWER al ejecutarse.
Se conserva únicamente como referencia del flujo original del notebook.
"""

from models.components import Tech
from models.geometry import GeoPosition
from models.inventory import Building, Project

project: Project = Project(
    building=Building(
        geolocation=GeoPosition(latitude=-33, longitude=-70),
        name="Cesfam Pimpim",
        address="calle falsa 123",
        city="Valparaíso",
    ),
    technology=[Tech.PHOTOVOLTAIC],
)

sample = project.weather.get_data().sample(5)
print(sample)
