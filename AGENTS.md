# AGENTS.md

## Entry points

- **Web MVP (new):** `app/` is a local FastAPI + Jinja2 + HTMX + MapLibre application. Start it with `.\run.ps1` or `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.
- **Legacy notebook:** `main_builder.ipynb` remains the original report generator. It is not the web app entry point.
- Web dependencies are in `requirements-web.txt`; legacy notebook dependencies are in `requirements.txt`. Do not conflate them.
- Web tests: `.\.venv\Scripts\python.exe -m pytest -q`. Tests use a temporary SQLite database and synthetic weather; they do not hit the network.
- Default local login: `admin@local` / `admin123`, configurable with `FV_ADMIN_EMAIL` and `FV_ADMIN_PASSWORD`.
- Web data lives in ignored `data/` (`app.db`, `cache/`, `projects/`). Never commit it or treat generated files as source.

## Web app conventions

- Run from the repo root: `.env.local`, `data/`, and all imports are resolved relative to the cwd.
- `app/main.py` creates tables and seeds the demo project, catalog, and admin on startup. There are no migrations yet: after changing `app/models.py`, delete `data/app.db` and restart.
- `app/models.py` is SQLite-first. Geometries are GeoJSON text; UTM projection is done in `app/services/geometry.py` and `app/services/layout.py`. Never buffer polygons in degrees.
- `app/services/layout.py` picks portrait/landscape by panel count, insets the roof by 25 cm, and returns WGS84 panel polygons.
- `app/services/weather.py` uses NASA POWER for `current_year - 2`, caches raw JSON under `data/cache/weather/`, and falls back to synthetic weather on failure. `FV_WEATHER_OFFLINE=1` forces synthetic.
- `app/services/pv.py` uses pvlib and stores a 12×24 `month_hour_matrix` in `Simulation.result_json`. `app/services/finance.py` computes NPV/IRR/payback/LCOE and stores cashflows in `FinancialRun.assumptions_json`.
- The document engine is template-based: `app/services/docx_templates.py` sanitizes smart quotes/split Jinja tags at runtime into `data/cache/templates/`; `docx_context.py` maps SQLite data to the legacy placeholders; `docx_tables.py` replaces `table_*` tokens with native Word tables; `docx_plots.py` builds the 11 memory images; `pdf.py` converts DOCX to PDF with Word (`docx2pdf`) and falls back to ReportLab.
- `Document.kind` is `memoria_calculo` or `pliego_licitacion`. Routes are `/designs/{id}/documents/memory` and `/designs/{id}/documents/bidding`. Memory requires simulation + financial; bidding requires simulation.
- `FV_PDF_CONVERTER` accepts `auto` (Word then ReportLab), `word`, `reportlab`, or `none`. Tests set `reportlab` to avoid opening Word.
- Roof and obstacle geometry live-edit in `app/static/js/site-map.js` via draggable vertex handles. `POST /api/geometry/area` recalculates live area; `PUT /api/roofs/{id}` and `PUT/DELETE /api/obstacles/{id}` persist edits. Any geometry change marks dependent designs `desactualizado`; simulation/financial/document routes block until the layout is recalculated.
- `app/__init__.py` injects `truststore` so HTTPS works behind public-sector corporate proxies with internal CAs. Keep it.
- HTML templates are in `app/templates/`; static assets in `app/static/`. Word source templates are in `templates/`; runtime-sanitized copies go to `data/cache/templates/` and must not be edited by hand.
- MapLibre and OSM tiles load from the internet at runtime. `staticmap` also fetches OSM tiles for the memory map; if that fails, a coordinate placeholder is embedded instead.
- The MVP is intentionally single-tenant. `org_id` and `AuditEvent` are already present for a future PostGIS/SaaS migration.

## Legacy notebook

- `main_builder.ipynb` imports exactly one module from `source/` (currently `source.cbl_hsanjose`) and applies its `data` dict manually: `data['project']` to `Project`, `data['consumptions']` to `Building.add_consumptions`, and `data['components']` to `add_generator` / `add_component` / `add_storage`.
- To generate another legacy site, copy a `source/` module and change the import in notebook cell 3. Bills use `DD-MM-YYYY` strings.
- `Project(...)` performs network calls at construction: NASA POWER weather plus exchange rates from `mindicador.cl` and `freecurrencyapi.com`.
- `.env.local` is ignored and contains live keys. Only `CURRENCY_API_KEY` is read by legacy code; OpenWeather/Google keys there are unused.
- `models.plotter.generate_docs` writes to `build/r_<city[:3]>_<building.name>/`; `build/` is ignored.
- Legacy mutable state is class-level in `Project.components`, `Project.bucket`/`Bucket.items`, and `Building.consumptions`. Restart the kernel between full runs.
- `archive/*.ipynb` reference removed symbols (`libs.repository.repo`, `repoEquipment`); use only `warehouse`/`panelRepo`.
- `class_models.md` is a design diagram, not the implemented API. `models/financial.py` is empty; `production.py` and `consumption_integrated.py` are unreferenced.
- The root `__init__.py` was made side-effect-free; the old sample that created a project on import is preserved in `archive/root_init_sample.py`.
