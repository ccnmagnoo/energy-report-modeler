"""Modelo de datos del MVP local.

Se usa SQLite para que la aplicación no dependa de Docker ni de PostgreSQL.
Las geometrías se guardan como GeoJSON/WKT en texto y se procesan con shapely.
El campo ``org_id`` queda desde el inicio para facilitar una futura versión
multi-tenant sobre PostgreSQL/PostGIS.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(180))
    rut: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    users: Mapped[list["User"]] = relationship(back_populates="organization")
    projects: Mapped[list["Project"]] = relationship(back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(180))
    password_hash: Mapped[str] = mapped_column(String(300))
    role: Mapped[str] = mapped_column(String(30), default="analista")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    organization: Mapped[Organization | None] = relationship(back_populates="users")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(180))
    code: Mapped[str | None] = mapped_column(String(60), nullable=True)
    client_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    client_rut: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="borrador")
    connection_type: Mapped[str] = mapped_column(String(30), default="netbilling")
    annual_consumption_kwh: Mapped[float] = mapped_column(Float, default=0.0)
    tariff_clp_kwh: Mapped[float] = mapped_column(Float, default=150.0)
    discount_rate: Mapped[float] = mapped_column(Float, default=0.08)
    analysis_years: Mapped[int] = mapped_column(Integer, default=25)
    opex_pct: Mapped[float] = mapped_column(Float, default=0.01)
    energy_price_increment: Mapped[float] = mapped_column(Float, default=0.03)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    organization: Mapped[Organization | None] = relationship(back_populates="projects")
    site: Mapped["Site | None"] = relationship(
        back_populates="project", uselist=False, cascade="all, delete-orphan"
    )
    designs: Mapped[list["Design"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), unique=True)
    address: Mapped[str] = mapped_column(String(250), default="")
    comuna: Mapped[str | None] = mapped_column(String(120), nullable=True)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, default=-33.45)
    longitude: Mapped[float] = mapped_column(Float, default=-70.67)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    project: Mapped[Project] = relationship(back_populates="site")
    roofs: Mapped[list["Roof"]] = relationship(
        back_populates="site", cascade="all, delete-orphan"
    )


class Roof(Base):
    __tablename__ = "roofs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id"))
    name: Mapped[str] = mapped_column(String(120), default="Techumbre principal")
    geom_geojson: Mapped[str] = mapped_column(Text)
    area_m2: Mapped[float] = mapped_column(Float, default=0.0)
    tilt_deg: Mapped[float] = mapped_column(Float, default=20.0)
    azimuth_deg: Mapped[float] = mapped_column(Float, default=180.0)
    material: Mapped[str] = mapped_column(String(80), default="Techumbre metálica")
    usable_factor: Mapped[float] = mapped_column(Float, default=0.9)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    site: Mapped[Site] = relationship(back_populates="roofs")
    obstacles: Mapped[list["Obstacle"]] = relationship(
        back_populates="roof", cascade="all, delete-orphan"
    )
    designs: Mapped[list["Design"]] = relationship(back_populates="roof")


class Obstacle(Base):
    __tablename__ = "obstacles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    roof_id: Mapped[int] = mapped_column(ForeignKey("roofs.id"))
    name: Mapped[str] = mapped_column(String(120), default="Obstáculo")
    geom_geojson: Mapped[str] = mapped_column(Text)
    height_m: Mapped[float] = mapped_column(Float, default=1.0)
    kind: Mapped[str] = mapped_column(String(60), default="otro")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    roof: Mapped[Roof] = relationship(back_populates="obstacles")


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(40), index=True)
    manufacturer: Mapped[str] = mapped_column(String(120))
    model: Mapped[str] = mapped_column(String(160))
    power_w: Mapped[float] = mapped_column(Float, default=0.0)
    efficiency: Mapped[float] = mapped_column(Float, default=0.0)
    width_mm: Mapped[float] = mapped_column(Float, default=0.0)
    height_mm: Mapped[float] = mapped_column(Float, default=0.0)
    price_clp: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="CLP")
    datasheet_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    specs: Mapped[dict] = mapped_column(JSON, default=dict)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    @property
    def label(self) -> str:
        return f"{self.manufacturer} {self.model}"


class Design(Base):
    __tablename__ = "designs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    roof_id: Mapped[int] = mapped_column(ForeignKey("roofs.id"))
    panel_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"))
    inverter_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"))
    name: Mapped[str] = mapped_column(String(120), default="Diseño FV")
    status: Mapped[str] = mapped_column(String(30), default="borrador")
    panel_count: Mapped[int] = mapped_column(Integer, default=0)
    dc_kw: Mapped[float] = mapped_column(Float, default=0.0)
    ac_kw: Mapped[float] = mapped_column(Float, default=0.0)
    occupancy: Mapped[float] = mapped_column(Float, default=0.0)
    tilt_deg: Mapped[float] = mapped_column(Float, default=20.0)
    azimuth_deg: Mapped[float] = mapped_column(Float, default=180.0)
    layout_geojson: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    project: Mapped[Project] = relationship(back_populates="designs")
    roof: Mapped[Roof] = relationship(back_populates="designs")
    panel: Mapped[Equipment] = relationship(foreign_keys=[panel_id])
    inverter: Mapped[Equipment] = relationship(foreign_keys=[inverter_id])
    bom_items: Mapped[list["BOMItem"]] = relationship(
        back_populates="design", cascade="all, delete-orphan"
    )
    simulations: Mapped[list["Simulation"]] = relationship(
        back_populates="design", cascade="all, delete-orphan"
    )
    financial_runs: Mapped[list["FinancialRun"]] = relationship(
        back_populates="design", cascade="all, delete-orphan"
    )
    compliance_checks: Mapped[list["ComplianceCheck"]] = relationship(
        back_populates="design", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(back_populates="design")


class BOMItem(Base):
    __tablename__ = "bom_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    design_id: Mapped[int] = mapped_column(ForeignKey("designs.id"))
    equipment_id: Mapped[int | None] = mapped_column(
        ForeignKey("equipment.id"), nullable=True
    )
    role: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(String(250))
    quantity: Mapped[float] = mapped_column(Float, default=1.0)
    unit_price_clp: Mapped[float] = mapped_column(Float, default=0.0)

    design: Mapped[Design] = relationship(back_populates="bom_items")
    equipment: Mapped[Equipment | None] = relationship()

    @property
    def total_clp(self) -> float:
        return round(self.quantity * self.unit_price_clp, 2)


class Simulation(Base):
    __tablename__ = "simulations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    design_id: Mapped[int] = mapped_column(ForeignKey("designs.id"))
    status: Mapped[str] = mapped_column(String(30), default="ok")
    annual_kwh: Mapped[float] = mapped_column(Float, default=0.0)
    specific_yield: Mapped[float] = mapped_column(Float, default=0.0)
    performance_ratio: Mapped[float] = mapped_column(Float, default=0.0)
    weather_source: Mapped[str] = mapped_column(String(80), default="NASA POWER")
    weather_year: Mapped[int] = mapped_column(Integer, default=0)
    result_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    design: Mapped[Design] = relationship(back_populates="simulations")


class FinancialRun(Base):
    __tablename__ = "financial_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    design_id: Mapped[int] = mapped_column(ForeignKey("designs.id"))
    capex_clp: Mapped[float] = mapped_column(Float, default=0.0)
    annual_savings_clp: Mapped[float] = mapped_column(Float, default=0.0)
    lcoe_clp_kwh: Mapped[float] = mapped_column(Float, default=0.0)
    npv_clp: Mapped[float] = mapped_column(Float, default=0.0)
    irr: Mapped[float | None] = mapped_column(Float, nullable=True)
    payback_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    assumptions_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    design: Mapped[Design] = relationship(back_populates="financial_runs")


class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    design_id: Mapped[int] = mapped_column(ForeignKey("designs.id"))
    rule: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(20), default="ok")
    message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    design: Mapped[Design] = relationship(back_populates="compliance_checks")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    design_id: Mapped[int | None] = mapped_column(
        ForeignKey("designs.id"), nullable=True
    )
    kind: Mapped[str] = mapped_column(String(60), default="memoria_calculo")
    version: Mapped[int] = mapped_column(Integer, default=1)
    docx_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    toml_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    project: Mapped[Project] = relationship(back_populates="documents")
    design: Mapped[Design | None] = relationship(back_populates="documents")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    entity: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    action: Mapped[str] = mapped_column(String(80))
    details_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
