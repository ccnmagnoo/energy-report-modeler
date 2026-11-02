"""Modelador de Reportes FV - aplicación web local."""

__version__ = "0.1.0"

# En redes corporativas de organismos públicos es común que el proxy use una CA
# interna. truststore hace que requests/urllib3 confíen en el almacén de
# certificados del sistema (Windows/macOS/Linux) además de certifi.
try:
    import truststore

    truststore.inject_into_ssl()
except ImportError:  # pragma: no cover - dependencia opcional en despliegues mínimos
    pass
