from models.components import Component
from models.econometrics import Cost


class EnergyStorage(Component):
    """Any energy storage component as batteries"""
    def __init__(self,
                description: str,
                model: str = 'generic',
                specification: str | None = None,
                reference: str | None = None,
                cost_per_unit: Cost = ...,
                quantity: int = 1) -> None:
        super().__init__(
            description,
            model,
            specification,
            reference,
            cost_per_unit,
            quantity)