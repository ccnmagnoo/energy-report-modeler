"""Adaptador entre el modelo SQLite y el contexto de las plantillas Word."""

from __future__ import annotations

from datetime import datetime

from app.services.docx_tables import TableData
from app.services.emission import annual_projection, historic, reduction_kg

TABLE_BASE = "@@TABLE_BASE_CONSUMPTIONS@@"
TABLE_FORECAST = "@@TABLE_FORECAST_CONSUMPTIONS@@"
TABLE_COMPONENTS = "@@TABLE_COMPONENTS@@"
TABLE_ENERGY_COMPONENTS = "@@TABLE_ENERGY_COMPONENTS@@"
TABLE_PRODUCTION_ARRAY = "@@TABLE_PRODUCTION_ARRAY@@"
TABLE_PRODUCTION_PERFORMANCE = "@@TABLE_PRODUCTION_PERFORMANCE@@"
TABLE_EMISSION_HISTORIC = "@@TABLE_EMISSION_HISTORIC@@"
TABLE_EMISSION_REDUCTION = "@@TABLE_EMISSION_REDUCTION@@"


def _num(value: float | int | None, decimals: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _clp(value: float | int | None) -> str:
    if value is None:
        return "—"
    return "CLP $ " + f"{value:,.0f}".replace(",", ".")


def _money(value: float | int | None) -> str:
    if value is None:
        return "—"
    return "$ " + f"{value:,.0f}".replace(",", ".")


def _pct(value: float | None, decimals: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value * 100:,.{decimals}f}%".replace(",", "X").replace(".", ",").replace("X", ".")


def _connection_local(connection_type: str) -> str:
    return {
        "offgrid": "Off-grid",
        "netbilling": "Net-billing",
        "hybrid": "Híbrido",
        "ongrid": "Net-billing",
    }.get(connection_type, connection_type)


def _monthly_value(total: float) -> float:
    return round(total / 12, 2) if total else 0.0


def _generation_monthly(simulation) -> list[float]:
    if simulation is None:
        return [0.0] * 12
    values = {int(item.get("month", 0)): float(item.get("kwh", 0)) for item in simulation.result_json.get("monthly", [])}
    return [round(values.get(month, 0.0), 2) for month in range(1, 13)]


def build_context(
    project,
    site,
    roof,
    design,
    simulation,
    financial,
    bom_items: list,
    version: int = 1,
) -> tuple[dict, dict[str, TableData]]:
    annual_kwh = float(simulation.annual_kwh) if simulation else 0.0
    annual_consumption = float(project.annual_consumption_kwh or 0.0)
    forecast_consumption = annual_consumption or annual_kwh
    savings_kwh = min(annual_kwh, forecast_consumption) if forecast_consumption else annual_kwh
    netbilling_kwh = max(0.0, annual_kwh - forecast_consumption) if forecast_consumption else 0.0
    tariff = float(project.tariff_clp_kwh or 0.0)
    increment = float(getattr(project, "energy_price_increment", 0.0) or 0.0)
    total_cost = sum(float(item.total_clp) for item in bom_items)
    annual_savings = (
        float(financial.annual_savings_clp)
        if financial is not None
        else savings_kwh * tariff + netbilling_kwh * tariff * 0.5
    )

    factor = annual_projection(datetime.now().year + 1)
    emission_kg = reduction_kg(annual_kwh, factor)
    generation = _generation_monthly(simulation)
    monthly_demand = _monthly_value(forecast_consumption)

    panel_area = 0.0
    if design.panel:
        panel_area = (
            design.panel_count
            * (design.panel.width_mm / 1000)
            * (design.panel.height_mm / 1000)
        )
    project_area = panel_area or (roof.area_m2 if roof else 0.0)

    connection_local = _connection_local(project.connection_type)
    city = (site.comuna if site else None) or (site.region if site else None) or "—"
    address = site.address if site else "—"
    latitude = site.latitude if site else -33.45
    longitude = site.longitude if site else -70.67

    project_ctx = {
        "title": f"{project.name} {connection_local}".strip(),
        "area": _num(project_area, 1),
        "connection_type": project.connection_type,
        "connection_type_local": connection_local,
        "building": {
            "name": project.name,
            "address": address,
            "city": city,
            "geolocation": {
                "latitude": f"{latitude:.6f}",
                "longitude": f"{longitude:.6f}",
                "altitude": "0",
            },
        },
    }

    eco = {
        "rate": _pct(project.discount_rate),
        "years": project.analysis_years,
        "currency": "CLP",
        "investment": f"{_money(financial.capex_clp if financial else total_cost)} . -",
        "npv": f"{_money(financial.npv_clp if financial else 0)}. -",
        "irr": _pct(financial.irr if financial and financial.irr is not None else 0, 2),
        "return": _num(financial.payback_years if financial else None, 2),
    }
    eco_num = {
        "npv": float(financial.npv_clp) if financial else 0.0,
        "irr": float(financial.irr) if financial and financial.irr is not None else 0.0,
        "return": float(financial.payback_years) if financial and financial.payback_years else 0.0,
        "npv_bool": bool(financial and financial.npv_clp > 0),
        "irr_bool": bool(
            financial
            and financial.irr is not None
            and financial.irr > project.discount_rate
        ),
    }

    context = {
        "project": project_ctx,
        "project_size": f"{design.dc_kw:.2f} kWp",
        "project_type": "fotovoltaico",
        "proyect_type": "fotovoltaico",
        "total_cost": _clp(total_cost),
        "forecast_consumption": f"{_num(forecast_consumption, 0)} kWh/año",
        "energy_production": f"{_num(annual_kwh, 0)} kWh/año",
        "energy_savings": f"{_num(savings_kwh, 0)} kWh/año",
        "energy_netbilling": f"{_num(netbilling_kwh, 0)} kWh/año",
        "annual_benefits": _clp(annual_savings),
        "cost_increment": f"{_num(increment * 100, 1)}%",
        "emission_reduction": f"{_num(emission_kg, 2)} kg CO2",
        "emission_forecast": f"{_num(factor, 4)} Ton CO2/MWh",
        "eco": eco,
        "eco_num": eco_num,
        "storage_existance": False,
        "storage_capacity": {
            "specification": "No aplica",
            "energy_storage_kwh": "0",
            "hours_autonomy": "0",
            "units": "0",
            "avg_demand_per_hour": "0",
        },
        "report_date": datetime.now().strftime("%d-%m-%Y"),
        "report_version": f"v{version}",
        "table_base_consumptions": TABLE_BASE,
        "table_forecast_consumptions": TABLE_FORECAST,
        "table_components": TABLE_COMPONENTS,
        "table_energy_components": TABLE_ENERGY_COMPONENTS,
        "table_production_array": TABLE_PRODUCTION_ARRAY,
        "table_production_performance": TABLE_PRODUCTION_PERFORMANCE,
        "table_emission_historic": TABLE_EMISSION_HISTORIC,
        "table_emission_reduction": TABLE_EMISSION_REDUCTION,
    }

    base_rows = []
    forecast_rows = []
    for month in range(1, 13):
        unit_cost = tariff
        forecast_cost = tariff * (1 + increment)
        base_rows.append(
            [
                str(month),
                _num(monthly_demand, 0),
                _num(unit_cost, 0),
                _clp(monthly_demand * unit_cost),
            ]
        )
        forecast_rows.append(
            [
                str(month),
                _num(monthly_demand, 0),
                _num(forecast_cost, 0),
                _clp(monthly_demand * forecast_cost),
            ]
        )

    performance_rows = []
    emission_rows = []
    for month in range(1, 13):
        generation_month = generation[month - 1]
        savings_month = min(generation_month, monthly_demand) if monthly_demand else generation_month
        surplus_month = max(0.0, generation_month - monthly_demand) if monthly_demand else 0.0
        performance_rows.append(
            [
                str(month),
                _num(monthly_demand, 0),
                _num(generation_month, 0),
                _num(savings_month, 0),
                _num(surplus_month, 0),
            ]
        )
        emission_rows.append(
            [
                str(month),
                _num(generation_month, 0),
                _num(reduction_kg(generation_month, factor), 2),
            ]
        )

    component_rows = [
        [
            item.role,
            item.description,
            _num(item.quantity, 0),
            _clp(item.unit_price_clp),
            _clp(item.total_clp),
        ]
        for item in bom_items
    ]
    energy_rows = [
        row
        for row in component_rows
        if row[0] in {"panel", "inversor", "estructura", "batería", "bateria"}
    ]

    tables = {
        TABLE_BASE: TableData(
            ["Mes", "Consumo kWh", "Costo unitario CLP/kWh", "Total CLP"],
            base_rows,
        ),
        TABLE_FORECAST: TableData(
            ["Mes", "Consumo kWh", "Costo unitario CLP/kWh", "Total CLP"],
            forecast_rows,
        ),
        TABLE_COMPONENTS: TableData(
            ["Glosa", "Descripción", "Cantidad", "Unitario", "Total"],
            component_rows,
        ),
        TABLE_ENERGY_COMPONENTS: TableData(
            ["Glosa", "Descripción", "Cantidad", "Unitario", "Total"],
            energy_rows,
        ),
        TABLE_PRODUCTION_ARRAY: TableData(
            ["Unidad", "Potencia kWp", "Producción kWh/año"],
            [[design.name, _num(design.dc_kw, 2), _num(annual_kwh, 0)]],
        ),
        TABLE_PRODUCTION_PERFORMANCE: TableData(
            ["Mes", "Demanda kWh", "Generación kWh", "Ahorro kWh", "Excedentes kWh"],
            performance_rows,
        ),
        TABLE_EMISSION_HISTORIC: TableData(
            ["Año", "Factor Ton CO2/MWh"],
            [[str(row["year"]), _num(row["factor_ton_mwh"], 4)] for row in historic()],
        ),
        TABLE_EMISSION_REDUCTION: TableData(
            ["Mes", "Generación kWh", "Reducción kg CO2"],
            emission_rows,
        ),
    }
    return context, tables
