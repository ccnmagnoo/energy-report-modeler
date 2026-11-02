"""Gráficos e imágenes requeridos por memory_template.docx."""

from __future__ import annotations

import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from app.services.weather import get_weather

TEMPLATE_DIR = Path(__file__).resolve().parents[2] / "templates"


def _monthly_generation(simulation) -> list[float]:
    if simulation is None:
        return [0.0] * 12
    values = {
        int(item.get("month", 0)): float(item.get("kwh", 0))
        for item in simulation.result_json.get("monthly", [])
    }
    return [values.get(month, 0.0) for month in range(1, 13)]


def _save(fig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _weather(site, year: int):
    return get_weather(
        site.latitude,
        site.longitude,
        year=year,
        allow_network=False,
    )["dataframe"]


def plot_consumption_forecast(project, path: Path) -> Path:
    monthly = float(project.annual_consumption_kwh or 0) / 12
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.plot(range(1, 13), [monthly] * 12, marker="o", linewidth=2, color="#0f766e")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Consumo estimado [kWh]")
    ax.set_xticks(range(1, 13))
    ax.grid(alpha=0.25)
    return _save(fig, path)


def plot_irradiance(weather, path: Path) -> Path:
    daily = (
        weather[["ghi", "dni", "dhi"]]
        .groupby([weather.index.month, weather.index.day])
        .mean()
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.plot(range(len(daily)), daily["dni"], label="Directa", linewidth=1, color="#d97706")
    ax.plot(range(len(daily)), daily["dhi"], label="Difusa", linewidth=1, color="#0f766e")
    ax.set_xlabel("Día del año")
    ax.set_ylabel("Irradiancia media [W/m²]")
    ax.legend()
    ax.grid(alpha=0.25)
    return _save(fig, path)


def plot_temperature(weather, path: Path) -> Path:
    grouped = weather["temp_air"].groupby([weather.index.month, weather.index.day])
    mean = grouped.mean().reset_index(drop=True)
    maximum = grouped.max().reset_index(drop=True)
    minimum = grouped.min().reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10, 3.8))
    x = range(len(mean))
    ax.plot(x, mean, label="Media", linewidth=1, color="#0f766e")
    ax.fill_between(x, minimum, maximum, alpha=0.25, color="#f59e0b", label="Máx/Mín")
    ax.set_xlabel("Día del año")
    ax.set_ylabel("Temperatura [°C]")
    ax.legend()
    ax.grid(alpha=0.25)
    return _save(fig, path)


def plot_components(bom_items: list, path: Path) -> Path:
    labels = [item.description[:32] for item in bom_items]
    values = [max(0.0, float(item.total_clp)) for item in bom_items]
    if not any(values):
        values = [1.0 for _ in values]
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = plt.get_cmap("Blues")(np.linspace(0.25, 0.75, len(values)))
    ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        pctdistance=0.8,
        startangle=45,
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    return _save(fig, path)


def _matrix(simulation) -> np.ndarray:
    matrix = None
    if simulation is not None:
        matrix = simulation.result_json.get("month_hour_matrix")
    if not matrix:
        matrix = [[0.0] * 24 for _ in range(12)]
    array = np.asarray(matrix, dtype=float)
    if array.shape != (12, 24):
        array = np.zeros((12, 24))
    return array


def plot_components_irr(simulation, path: Path) -> Path:
    matrix = _matrix(simulation)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    image = ax.imshow(matrix, aspect="auto", cmap="plasma", origin="lower")
    ax.set_xlabel("Hora")
    ax.set_ylabel("Mes")
    ax.set_xticks(range(0, 24, 2))
    ax.set_yticks(range(12))
    ax.set_yticklabels(range(1, 13))
    fig.colorbar(image, ax=ax, label="Potencia media [kW]")
    return _save(fig, path)


def plot_components_production(simulation, path: Path) -> Path:
    monthly = _monthly_generation(simulation)
    fig, ax = plt.subplots(figsize=(9, 3.8))
    bars = ax.bar(range(1, 13), monthly, color="#0f766e", alpha=0.85)
    ax.bar_label(bars, fmt="%.0f", fontsize=8)
    ax.set_xlabel("Mes")
    ax.set_ylabel("Generación [kWh]")
    ax.set_xticks(range(1, 13))
    ax.grid(axis="y", alpha=0.25)
    return _save(fig, path)


def plot_production_performance(project, simulation, path: Path) -> Path:
    generation = _monthly_generation(simulation)
    demand = [float(project.annual_consumption_kwh or 0) / 12] * 12
    savings = [min(g, d) for g, d in zip(generation, demand)]
    surplus = [max(0.0, g - d) for g, d in zip(generation, demand)]
    fig, ax = plt.subplots(figsize=(10, 4.2))
    x = range(1, 13)
    ax.plot(x, demand, "o--", label="Demanda", color="#64748b")
    ax.plot(x, generation, marker="o", linewidth=2, label="Generación", color="#0f766e")
    ax.bar(x, savings, width=0.45, label="Ahorro", color="#0d9488", alpha=0.75)
    ax.bar(x, surplus, width=0.35, label="Excedentes", color="#f59e0b", alpha=0.85)
    ax.set_xlabel("Mes")
    ax.set_ylabel("Energía [kWh]")
    ax.set_xticks(range(1, 13))
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    return _save(fig, path)


def plot_performance_frequency(simulation, path: Path) -> Path:
    matrix = _matrix(simulation)
    hours = np.tile(np.arange(24), 12)
    power = matrix.flatten()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if np.any(power > 0):
        hb = ax.hexbin(hours, power, gridsize=12, cmap="plasma", mincnt=1)
        fig.colorbar(hb, ax=ax, label="Frecuencia")
    else:
        ax.text(0.5, 0.5, "Sin datos de simulación", ha="center", va="center")
    ax.set_xlabel("Hora")
    ax.set_ylabel("Potencia [kW]")
    ax.set_xticks(range(0, 24, 2))
    return _save(fig, path)


def plot_flux(financial, project, path: Path) -> Path:
    if financial is not None:
        cashflows = financial.assumptions_json.get("cashflows")
    else:
        cashflows = None
    if not cashflows:
        capex = float(financial.capex_clp) if financial else 0.0
        annual_net = (
            float(financial.annual_savings_clp) - float(financial.capex_clp) * project.opex_pct
            if financial
            else 0.0
        )
        cashflows = [-capex] + [annual_net] * project.analysis_years
    cashflows = [float(value) for value in cashflows]
    accumulated = np.cumsum(cashflows)
    fig, ax = plt.subplots(figsize=(10, 4))
    x = range(len(cashflows))
    bars = ax.bar(x, np.asarray(cashflows) / 1000, color="#94a3b8", label="Flujo")
    ax.plot(x, accumulated / 1000, color="#d97706", marker="o", linewidth=2, label="Acumulado")
    ax.bar_label(bars, fmt="%.0f", fontsize=7)
    ax.set_xlabel("Año")
    ax.set_ylabel("Miles CLP")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    return _save(fig, path)


def map_location(site, path: Path) -> Path:
    try:
        from staticmap import CircleMarker, StaticMap

        static = StaticMap(
            640,
            480,
            url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        )
        static.add_marker(
            CircleMarker((site.longitude, site.latitude), "red", 14)
        )
        image = static.render()
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)
        return path
    except Exception:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.set_facecolor("#e8eef6")
        ax.scatter([site.longitude], [site.latitude], s=120, color="#b42318", zorder=3)
        ax.set_title("Ubicación del proyecto")
        ax.set_xlabel("Longitud")
        ax.set_ylabel("Latitud")
        ax.grid(alpha=0.3)
        return _save(fig, path)


def connection_diagram(connection_type: str, output_dir: Path) -> Path:
    source = TEMPLATE_DIR / f"diagram_{connection_type}.png"
    if not source.exists():
        source = TEMPLATE_DIR / "diagram_netbilling.png"
    target = output_dir / "connection_diagram.png"
    shutil.copyfile(source, target)
    return target


def generate_plots(
    project,
    site,
    design,
    simulation,
    financial,
    bom_items: list,
    output_dir: Path,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    weather = _weather(site, simulation.weather_year if simulation else 2024)
    return {
        "plot_consumption_forecast": plot_consumption_forecast(
            project, output_dir / "plot_consumption_forecast.png"
        ),
        "plot_irradiance": plot_irradiance(
            weather, output_dir / "plot_irradiance.png"
        ),
        "plot_temperature": plot_temperature(
            weather, output_dir / "plot_temperature.png"
        ),
        "plot_components": plot_components(
            bom_items, output_dir / "plot_components.png"
        ),
        "plot_components_irr": plot_components_irr(
            simulation, output_dir / "plot_components_irr.png"
        ),
        "plot_components_production": plot_components_production(
            simulation, output_dir / "plot_components_production.png"
        ),
        "plot_production_performance": plot_production_performance(
            project, simulation, output_dir / "plot_production_performance.png"
        ),
        "plot_performance_frequency": plot_performance_frequency(
            simulation, output_dir / "plot_performance_frequency.png"
        ),
        "plot_flux": plot_flux(
            financial, project, output_dir / "plot_flux.png"
        ),
        "map_location": map_location(site, output_dir / "map_location.png"),
        "connection_diagram": connection_diagram(
            project.connection_type, output_dir
        ),
    }
