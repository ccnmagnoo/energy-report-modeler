"""Indicadores económicos del proyecto fotovoltaico."""

from __future__ import annotations

from typing import Iterable


def npv(rate: float, cashflows: Iterable[float]) -> float:
    return sum(value / ((1 + rate) ** period) for period, value in enumerate(cashflows))


def irr(cashflows: list[float]) -> float | None:
    """TIR por bisección; devuelve None si no hay cambio de signo."""

    if not cashflows or all(value >= 0 for value in cashflows) or all(value <= 0 for value in cashflows):
        return None

    low, high = -0.99, 10.0
    f_low = npv(low, cashflows)
    f_high = npv(high, cashflows)
    if f_low * f_high > 0:
        return None

    for _ in range(200):
        mid = (low + high) / 2
        f_mid = npv(mid, cashflows)
        if abs(f_mid) < 0.01:
            return mid
        if f_low * f_mid <= 0:
            high = mid
            f_high = f_mid
        else:
            low = mid
            f_low = f_mid
    return (low + high) / 2


def annual_savings(
    annual_kwh: float,
    annual_consumption_kwh: float,
    tariff_clp_kwh: float,
    surplus_factor: float = 0.5,
) -> float:
    """Ahorro anual simplificado con autoconsumo y excedentes.

    Si no se informa consumo, se asume que toda la generación sustituye compra
    de energía. Si hay consumo, el excedente se valoriza a ``surplus_factor``.
    """

    if annual_kwh <= 0 or tariff_clp_kwh <= 0:
        return 0.0
    if annual_consumption_kwh <= 0:
        return annual_kwh * tariff_clp_kwh

    self_consumed = min(annual_kwh, annual_consumption_kwh)
    surplus = max(0.0, annual_kwh - annual_consumption_kwh)
    return self_consumed * tariff_clp_kwh + surplus * tariff_clp_kwh * surplus_factor


def analyze(
    capex_clp: float,
    annual_savings_clp: float,
    annual_opex_clp: float,
    annual_kwh: float,
    years: int = 25,
    discount_rate: float = 0.08,
) -> dict:
    if years <= 0:
        raise ValueError("El horizonte de análisis debe ser positivo")
    if discount_rate <= -1:
        raise ValueError("La tasa de descuento no es válida")

    annual_net = annual_savings_clp - annual_opex_clp
    cashflows = [-capex_clp] + [annual_net] * years
    result_npv = npv(discount_rate, cashflows)
    result_irr = irr(cashflows)
    payback = capex_clp / annual_net if annual_net > 0 else None

    discounted_energy = sum(
        annual_kwh / ((1 + discount_rate) ** period) for period in range(1, years + 1)
    )
    discounted_costs = capex_clp + sum(
        annual_opex_clp / ((1 + discount_rate) ** period)
        for period in range(1, years + 1)
    )
    lcoe = discounted_costs / discounted_energy if discounted_energy > 0 else None

    return {
        "capex_clp": round(capex_clp, 2),
        "annual_savings_clp": round(annual_savings_clp, 2),
        "annual_opex_clp": round(annual_opex_clp, 2),
        "annual_net_clp": round(annual_net, 2),
        "npv_clp": round(result_npv, 2),
        "irr": round(result_irr, 6) if result_irr is not None else None,
        "payback_years": round(payback, 2) if payback is not None else None,
        "lcoe_clp_kwh": round(lcoe, 2) if lcoe is not None else None,
        "cashflows": [round(value, 2) for value in cashflows],
        "years": years,
        "discount_rate": discount_rate,
    }
