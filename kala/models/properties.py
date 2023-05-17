"""Module defining agent (and possibly other types of actors) properties"""
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, TypeVar


@dataclass
class BaseProperties(ABC):
    """
    Base property intended to be subclassed.

    Properties are similar to traits but they refer to attributes that are normally
    changing in time.

    Attributes
    ----------

    Methods
    -------
    as_dict()
        Return the properties as a dictionary.
    update()
        Do an update of the properties.

    """

    def to_dict(self) -> dict[str, Any]:
        """
        Return the properties as a dictionary.

        Returns
        -------
        dict[str, Any]
        """
        return asdict(self)

    @abstractmethod
    def update(self) -> None:
        """Do an update of the properties according to the class' internal rules."""

    # going forward we can add other methods that are common to all Properties


# pylint: disable=invalid-name
PropertiesType = TypeVar("PropertiesType", bound=BaseProperties)
"""Used to refer to BaseProperties as well as its subclasses."""


@dataclass
class SaverProperties(BaseProperties):
    """
    Saver properties.

    Attributes
    ----------
    total_savings : float
    income_per_period : float
    specialization_degree : float
        A number between [0, 1].
    """

    total_savings: float
    income_per_period: float
    specialization_degree: float

    def update(self) -> None:
        self.total_savings += self.income_per_period
        # TODO: - inversion + payoff


if __name__ == "__main__":
    sp = SaverProperties(0, 1, 0.5)
    sp.update()
    sp.update()
    assert sp.total_savings == 2
    assert sp.to_dict()["total_savings"] == 2
