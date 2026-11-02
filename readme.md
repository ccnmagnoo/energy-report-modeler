# Modelador de Reportes FV

Aplicación para generar estudios, memorias de cálculo, especificaciones y
documentos de proyectos fotovoltaicos. El repositorio contiene dos etapas:

- **MVP web local (`app/`):** FastAPI + Jinja2 + HTMX + MapLibre, catálogo de
  equipos, editor GIS, layout automático, simulación pvlib, finanzas y salida
  DOCX/PDF/TOML.
- **Generador legacy (`main_builder.ipynb`):** notebook original basado en
  docxtpl y plantillas Word.

## Inicio rápido web

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-web.txt
.\run.ps1
```

Abre <http://127.0.0.1:8000>. Credenciales iniciales: `admin@local` / `admin123`.

Flujo: crear proyecto → geocodificar y dibujar techumbre → seleccionar panel e
inversor → simular producción → evaluar economía → generar **memoria de cálculo**
y **pliego de licitación** en DOCX/PDF/TOML.

La app usa internet para NASA POWER, teselas OpenStreetMap y geocodificación
Nominatim. Si la red corporativa usa una CA interna, `truststore` permite
confiar en el almacén de certificados del sistema.

Documentación detallada: [README-WEB.md](README-WEB.md).

## Notebook legacy

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Abre `main_builder.ipynb` y ejecútalo de arriba hacia abajo. Requiere
`.env.local` para las tasas de cambio. Los resultados se guardan en `build/`.

## Referencias de cálculo

- [Explorador Solar Minenergía](https://solar.minenergia.cl/inicio)
- [Modelo fotovoltaico](https://solar.minenergia.cl/downloads/fotovoltaico.pdf)
- [Modelo de radiación](https://solar.minenergia.cl/downloads/radiacion.pdf)
- [NASA POWER](https://power.larc.nasa.gov/data-access-viewer/)

## Licencia

MIT.
