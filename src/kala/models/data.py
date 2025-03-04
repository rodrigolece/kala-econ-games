"""Module defining data containers."""

from typing import TypeVar

from pydantic import BaseModel

Traits = TypeVar("Traits", bound=BaseModel)
Properties = TypeVar("Properties", bound=BaseModel)


class SaverTraits(BaseModel):
    """
    Saver traits.

    Attributes
    ----------
    group: int | None
    min_specialization: float
    income_per_period: float
    homophily: float | None

    """

    group: int | None
    min_specialization: float
    income_per_period: float
    homophily: float | None = None


class SaverProperties(BaseModel):
    """
    Saver properties.

    Attributes
    ----------
    is_saver: bool

    """

    is_saver: bool
