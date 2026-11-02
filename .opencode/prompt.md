Actúa como un Arquitecto de Software Senior, especialista en energía fotovoltaica, licitaciones públicas chilenas y desarrollo de aplicaciones GIS.

Tengo un proyecto desarrollado actualmente en Python/Jupyter Notebook que genera automáticamente:

- Estudios técnicos de sistemas fotovoltaicos sobre techumbre.
- Pliegos de licitación para organismos públicos.
- Especificaciones técnicas.
- Memorias de cálculo.
- Informes de prefactibilidad.
- Listado de equipamientos.

## El sistema recibe como entradas:

- Superficie disponible de techumbre (m²)
- Inclinación (°)
- Azimut (°)
- Ubicación geográfica
- Consumo eléctrico
- Tipo de cliente
- Parámetros económicos

## Actualmente utiliza:

- API POWER de NASA para irradiancia solar.
- APIs de conversión de divisas.
- Templates Word (.docx) para generación automática de documentos, alojados en la carpeta templates
- Librerías Python para cálculos fotovoltaicos.

Necesito rediseñar completamente la solución y transformarla en una aplicación web moderna, escalable y orientada al sector público.

OBJETIVOS PRINCIPALES

1. Generar automáticamente:
   - Estudios técnicos.
   - Bases de licitación.
   - Especificaciones técnicas.
   - TDR.
   - Informes de rentabilidad.
   - Memorias de cálculo.
   - Informes SEC.
   - Reportes PDF y Word.

2. Permitir diseño gráfico interactivo de sistemas fotovoltaicos.

3. Incorporar información geoespacial mediante mapas.

4. Integrar una biblioteca de equipos comerciales.

5. Automatizar la selección óptima de equipos.

6. Incorporar inteligencia artificial para asistencia en el diseño.

------------------------------------------------
# MÓDULO GIS Y MAPAS
------------------------------------------------

Incorporar:

- Google Maps API
- Mapbox
- OpenStreetMap

Funcionalidades:

- Búsqueda por dirección.
- Geocodificación.
- Selección de techumbre directamente en mapa.
- Cálculo automático de superficie.
- Dibujo de polígonos.
- Medición de áreas.
- Visualización satelital.
- Visualización 3D.
- Exportación GeoJSON.

Opcional:

- Integración con Catastro Público.
- Integración con Infraestructura de Datos Geoespaciales de Chile (IDE Chile).

------------------------------------------------
# MÓDULO DE DISEÑO FOTOVOLTAICO
------------------------------------------------

Desarrollar herramienta gráfica tipo CAD simplificado.

Permitir:

- Dibujar techumbres.
- Importar imágenes satelitales.
- Delimitar obstáculos.
- Identificar sombras.
- Definir orientación de paneles.
- Definir inclinación.
- Distribución automática de módulos.

Mostrar:

- Cantidad de módulos.
- Potencia instalada.
- Factor de ocupación.
- Producción energética estimada.

Agregar:

- Detección automática de superficies mediante IA.
- Segmentación de techos usando visión computacional.

------------------------------------------------
# BIBLIOTECA DE EQUIPOS
------------------------------------------------

Diseñar una base de datos extensible.

TABLA PANELES

Campos:

- Fabricante
- Modelo
- Potencia Wp
- Eficiencia
- Dimensiones
- Peso
- Garantía
- Precio
- Distribuidor
- Ficha técnica PDF

Ejemplos iniciales:

Jinko Solar
Trina Solar
LONGi
JA Solar
Canadian Solar
Risen
Astronergy

TABLA INVERSORES

Huawei
Sungrow
SMA
Fronius
GoodWe
Solis
Growatt

Campos:

- Potencia
- MPPT
- Tensión máxima
- Eficiencia
- Precio

TABLA ESTRUCTURAS

- Techumbre metálica
- Zinc
- PV4
- Sandwich
- Hormigón

TABLA BATERÍAS

- BYD
- Huawei Luna
- Pylontech
- Dyness

------------------------------------------------
# MOTOR DE OPTIMIZACIÓN
------------------------------------------------

Desarrollar algoritmo que determine:

- Mejor combinación de paneles.
- Mejor combinación de inversor.
- Relación DC/AC.
- Cumplimiento SEC.
- Cumplimiento NCh.
- Menor LCOE.
- Mayor VAN.
- Mejor TIR.

Variables objetivo:

- CAPEX
- OPEX
- Producción anual
- Payback
- VAN
- TIR
- Costo nivelado de energía

------------------------------------------------
# MÓDULO DE DOCUMENTOS
------------------------------------------------

Permitir generar automáticamente:

1. Bases de Licitación.
2. Especificaciones Técnicas.
3. Términos de Referencia.
4. Informe Técnico.
5. Memoria de Cálculo.
6. Informe de Evaluación Económica.
7. Informe Ejecutivo.

Mantener compatibilidad con:

- Word DOCX
- PDF
- Alamacenamiento en TOML de resultados

Utilizar plantillas parametrizables.

------------------------------------------------
# ARQUITECTURA RECOMENDADA
------------------------------------------------

Frontend:

- Next.js
- React
- TypeScript
- Tailwind
- Mapbox GL

Backend:

- FastAPI

Procesamiento:

- Python
- pvlib
- pandas
- numpy
- geopandas
- rasterio
- shapely

Base de datos:

- PostgreSQL
- PostGIS

Documentos:

- python-docx
- Jinja2
- WeasyPrint

Autenticación:

- Azure AD
- Entra ID

Despliegue:

- Azure App Service
- Azure Container Apps
- Azure PostgreSQL

------------------------------------------------
# ENTREGABLES ESPERADOS
------------------------------------------------

Genera:

1. Arquitectura completa del sistema.
2. Modelo entidad-relación.
3. Estructura de carpetas.
4. Diseño de base de datos.
5. APIs REST.
6. Diseño UX/UI.
7. Wireframes.
8. Roadmap de desarrollo.
9. Backlog Agile.
10. Plan de migración desde Jupyter Notebook.
11. Estrategia de integración de APIs externas.
12. Diseño de biblioteca de equipos expandible.
13. Ejemplos de consultas y casos de uso.
14. Código base inicial para MVP.
15. Recomendaciones específicas para organismos públicos en Chile y cumplimiento normativo SEC.

El resultado debe diseñarse como un producto SaaS denominado:

"Modelador de Reportes FV"

orientado servicios públicos.
el stack es html pythom, css.