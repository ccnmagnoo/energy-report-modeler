"""Datos iniciales: organización, usuario administrador, catálogo y demo."""

from __future__ import annotations

import json
import math

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import hash_password
from app.config import DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD
from app.models import Equipment, Organization, Project, Roof, Site, User
from app.services.geometry import area_m2


def _equipment(
    category: str,
    manufacturer: str,
    model: str,
    price_clp: float,
    power_w: float = 0,
    efficiency: float = 0,
    width_mm: float = 0,
    height_mm: float = 0,
    datasheet_url: str | None = None,
    **specs,
) -> Equipment:
    return Equipment(
        category=category,
        manufacturer=manufacturer,
        model=model,
        price_clp=price_clp,
        power_w=power_w,
        efficiency=efficiency,
        width_mm=width_mm,
        height_mm=height_mm,
        datasheet_url=datasheet_url,
        specs=specs,
    )


def _seed_catalog(db: Session) -> None:
    if (db.scalar(select(func.count(Equipment.id))) or 0) > 0:
        return

    items = [
        # Paneles
        _equipment(
            "Panel",
            "Canadian Solar",
            "CS7N-655",
            208_547,
            655,
            0.212,
            1038,
            2384,
            "https://static.csisolar.com/wp-content/uploads/sites/3/2021/07/28105634/CS-BiHiKu7_CS7N-MB-AG_v1.7_F43M_J1_NA.pdf",
            vmp=38.1,
            imp=17.20,
            voc=45.2,
            isc=18.43,
            temp_coef=-0.35,
            warranty_years=25,
            cell_type="Mono PERC",
        ),
        _equipment(
            "Panel",
            "Risen",
            "RSM132-8-660M",
            242_017,
            660,
            0.212,
            1038,
            2384,
            "https://www.solartex.cl/tienda/wp-content/uploads/2023/03/RSM132-8-660M.pdf",
            vmp=38.12,
            imp=17.32,
            voc=45.75,
            isc=18.33,
            temp_coef=-0.35,
            warranty_years=25,
            cell_type="Mono PERC",
        ),
        _equipment("Panel", "Jinko Solar", "Tiger Neo N-type 585W", 190_000, 585, 0.225, 1134, 2278, vmp=43.5, imp=13.45, voc=51.5, isc=14.2, temp_coef=-0.30, warranty_years=25, cell_type="N-type TOPCon"),
        _equipment("Panel", "Trina Solar", "Vertex S+ 450W", 145_000, 450, 0.225, 1134, 1762, vmp=34.2, imp=13.16, voc=41.0, isc=13.9, temp_coef=-0.34, warranty_years=25, cell_type="N-type TOPCon"),
        _equipment("Panel", "LONGi", "Hi-MO 6 580W", 185_000, 580, 0.225, 1134, 2278, vmp=43.8, imp=13.24, voc=52.1, isc=14.0, temp_coef=-0.29, warranty_years=25, cell_type="HPBC"),
        # Inversores
        _equipment(
            "Inversor",
            "Huawei",
            "SUN2000-2KTL-L1",
            678_809,
            2_000,
            0.98,
            datasheet_url="https://www.dartel.cl/inversor-huawei-on-grid-2kw-hibrido-monofasico-sun2000-2ktl-l1-2088128161-huawei/p",
            max_dc_w=2_600,
            mppt="1/1",
            mppt_min=90,
            mppt_max=560,
            max_voltage=600,
            max_input_current=13,
            mppt_count=1,
            phases="Monofásico",
        ),
        _equipment(
            "Inversor",
            "Solis",
            "Mini 2500 4G",
            557_000,
            2_500,
            0.97,
            max_dc_w=3_250,
            mppt="1/1",
            mppt_min=80,
            mppt_max=500,
            max_voltage=600,
            max_input_current=13,
            mppt_count=1,
            phases="Monofásico",
        ),
        _equipment(
            "Inversor",
            "Huawei",
            "SUN2000-5KTL-L1",
            1_100_000,
            5_000,
            0.98,
            max_dc_w=6_500,
            mppt="2/2",
            mppt_min=90,
            mppt_max=560,
            max_voltage=600,
            max_input_current=26,
            mppt_count=2,
            phases="Monofásico",
        ),
        _equipment(
            "Inversor",
            "Deye",
            "SUN-12K-SG04LP3",
            3_190_000,
            12_000,
            0.97,
            max_dc_w=15_600,
            mppt="2/2",
            mppt_min=150,
            mppt_max=850,
            max_voltage=1_000,
            max_input_current=26,
            mppt_count=2,
            phases="Trifásico",
        ),
        _equipment(
            "Inversor",
            "Canadian Solar",
            "CSI-100K-T400GL02-E",
            8_680_000,
            100_000,
            0.98,
            max_dc_w=130_000,
            mppt="Múltiple",
            mppt_min=200,
            mppt_max=1_000,
            max_voltage=1_100,
            max_input_current=180,
            mppt_count=6,
            phases="Trifásico",
            datasheet_url="https://www.solartex.cl/tienda/wp-content/uploads/2023/05/CANADIAN-SOLAR-CSI-100K-T400GL02-E.pdf",
        ),
        # Estructuras: precio por módulo
        _equipment("Estructura", "Genérica", "Techumbre metálica coplanar", 55_000, specs={"roof_type": "metálica", "mounting": "coplanar"}),
        _equipment("Estructura", "Genérica", "Cubierta zinc", 65_000, specs={"roof_type": "zinc", "mounting": "coplanar"}),
        _equipment("Estructura", "PV4", "Estructura PV4", 75_000, specs={"roof_type": "PV4", "mounting": "coplanar"}),
        _equipment("Estructura", "Genérica", "Hormigón con lastre", 85_000, specs={"roof_type": "hormigón", "mounting": "lastre"}),
        # Baterías
        _equipment("Batería", "BYD", "LVS 4.0", 2_500_000, power_w=4_000, specs={"capacity_kwh": 4.0, "chemistry": "LFP", "voltage": 48}),
        _equipment("Batería", "Huawei", "LUNA2000-5-S0", 3_200_000, power_w=5_000, specs={"capacity_kwh": 5.0, "chemistry": "LFP", "voltage": 48}),
        _equipment("Batería", "Pylontech", "US5000", 2_100_000, power_w=4_800, specs={"capacity_kwh": 4.8, "chemistry": "LFP", "voltage": 48}),
        _equipment("Batería", "Dyness", "Tower T10", 4_500_000, power_w=10_000, specs={"capacity_kwh": 10.0, "chemistry": "LFP", "voltage": 48}),
    ]
    db.add_all(items)
    db.commit()


def _seed_demo_project(db: Session, org: Organization) -> None:
    if (db.scalar(select(func.count(Project.id))) or 0) > 0:
        return

    latitude, longitude = -33.314975, -71.414803
    delta_lat = 15 / 111_320
    delta_lon = 20 / (111_320 * math.cos(math.radians(latitude)))
    coordinates = [
        [longitude, latitude],
        [longitude + delta_lon, latitude],
        [longitude + delta_lon, latitude + delta_lat],
        [longitude, latitude + delta_lat],
        [longitude, latitude],
    ]
    geojson = {"type": "Polygon", "coordinates": [coordinates]}

    project = Project(
        org_id=org.id,
        name="Hospital San José - demo",
        code="FV-DEMO-001",
        client_name="Servicio de Salud Metropolitano",
        client_rut="61.000.000-0",
        connection_type="netbilling",
        annual_consumption_kwh=220_000,
        tariff_clp_kwh=165,
        discount_rate=0.08,
        analysis_years=25,
        opex_pct=0.01,
        energy_price_increment=0.03,
    )
    db.add(project)
    db.flush()

    site = Site(
        project_id=project.id,
        address="Juan Verdaguer 122",
        comuna="Casablanca",
        region="Valparaíso",
        latitude=latitude,
        longitude=longitude,
    )
    db.add(site)
    db.flush()

    roof = Roof(
        site_id=site.id,
        name="Techumbre principal",
        geom_geojson=json.dumps(geojson),
        area_m2=area_m2(geojson, latitude, longitude),
        tilt_deg=20,
        azimuth_deg=180,
        material="Techumbre metálica",
        usable_factor=0.9,
    )
    db.add(roof)
    db.commit()


def ensure_seed(db: Session) -> None:
    org = db.scalar(select(Organization).limit(1))
    if org is None:
        org = Organization(name="Organización local", rut="")
        db.add(org)
        db.flush()

    user = db.scalar(select(User).where(User.email == DEFAULT_ADMIN_EMAIL.lower()))
    if user is None:
        db.add(
            User(
                org_id=org.id,
                email=DEFAULT_ADMIN_EMAIL.lower(),
                name="Administrador local",
                password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
                role="admin",
            )
        )
    db.commit()

    _seed_catalog(db)
    _seed_demo_project(db, org)
