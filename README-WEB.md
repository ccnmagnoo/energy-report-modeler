# Modelador de Reportes FV — MVP web local

Aplicación local para crear estudios fotovoltaicos, dibujar techumbres, calcular
producción, evaluar la economía y generar memorias en DOCX, PDF y TOML.

## Requisitos

- Python 3.12 o superior.
- Internet para NASA POWER, teselas OpenStreetMap/Esri/OpenTopoMap y geocodificación.
- LibreOffice no es obligatorio: el PDF se genera con ReportLab.
- `truststore` permite confiar en la CA corporativa del organismo sin desactivar SSL.
- Revisa los términos de uso de cada proveedor de teselas antes de un despliegue institucional.

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-web.txt
```

## Ejecución

```powershell
.\run.ps1
```

Luego abre <http://127.0.0.1:8000>.

Credenciales iniciales:

- Usuario: `admin@local`
- Contraseña: `admin123`

Cámbialas con `FV_ADMIN_EMAIL` y `FV_ADMIN_PASSWORD` antes de usar la aplicación
con datos reales.

## Flujo de uso

1. **Proyecto:** crea el expediente con cliente, consumo, tarifa y parámetros económicos.
2. **Emplazamiento:** busca una dirección, ajusta coordenadas, dibuja la techumbre y edita sus vértices arrastrando los nodos. También puedes editar o eliminar obstáculos. El mapa base se puede cambiar entre Calles, Satélite, Híbrido y Topográfico; la preferencia se recuerda y el valor inicial es Híbrido.
3. **Diseño:** elige panel e inversor; el sistema distribuye módulos y calcula el BOM.
4. **Simulación:** consulta NASA POWER y calcula producción anual y mensual.
5. **Economía:** calcula CAPEX, ahorro, VAN, TIR, payback y LCOE.
6. **Documentos:** genera dos entregables usando las plantillas originales:
   - **Memoria de cálculo:** `templates/memory_template.docx`, con tablas nativas, gráficos y mapa.
   - **Pliego de licitación:** `templates/bidding_template.docx`, conservando el texto legal y técnico.

Cada documento se guarda en `data/projects/{project_id}/documents/...` en DOCX,
PDF y TOML. El PDF se convierte con Word cuando está disponible; si no, se usa
ReportLab como respaldo. Controla el comportamiento con `FV_PDF_CONVERTER`.

Si editas los vértices de la techumbre o de un obstáculo después de crear un
diseño, el diseño queda como `desactualizado`. Vuelve al diseño y pulsa
**Recalcular distribución** antes de simular o generar documentos.

## Datos y configuración

El MVP no incluye migraciones Alembic. Si cambias el esquema de `app/models.py`,
detén el servidor, borra `data/app.db` y vuelve a iniciar para recrear las tablas
y los datos iniciales.

Esta versión está pensada para ejecutarse en `localhost`. No la expongas a
Internet sin agregar CSRF, HTTPS, gestión de secretos y un endurecimiento de
seguridad adicional.


| Variable | Uso |
|---|---|
| `FV_DATA_DIR` | Carpeta de datos, por defecto `data/` |
| `FV_DATABASE_URL` | URL SQLAlchemy; por defecto SQLite en `data/app.db` |
| `FV_SECRET_KEY` | Clave de sesión; cámbiala en producción |
| `FV_ADMIN_EMAIL` / `FV_ADMIN_PASSWORD` | Credenciales iniciales |
| `FV_WEATHER_OFFLINE=1` | Fuerza clima sintético para pruebas |
| `FV_WEATHER_YEAR_OFFSET` | Años hacia atrás para NASA POWER; por defecto 2 |
| `FV_PDF_CONVERTER` | `auto`, `word`, `reportlab` o `none`; por defecto `auto` |

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Alcance del MVP

Incluye GIS 2D, techumbre, obstáculos, layout automático, catálogo, simulación
pvlib, finanzas, checklist SEC básico y documentos. No incluye 3D, segmentación
de techos por IA, integración Catastro/IDE Chile ni multi-tenant cloud; la
estructura de datos y servicios deja preparadas esas extensiones.
