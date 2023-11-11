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

    Methods
    -------
    to_dict()
        Return the properties as a dictionary.
    update()
        Do an update of the properties.
    reset()
        Reset the properties to starting values.

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
    def update(self, *args, **kwargs) -> None:
        """Do an update of the properties according to the class' internal rules."""

    @abstractmethod
    def reset(self) -> None:
        """Reset the properties to starting values."""

    # going forward we can add other methods that are common to all Properties


PropertiesT = TypeVar("PropertiesT", bound=BaseProperties)
"""Used to refer to BaseProperties as well as its subclasses."""


@dataclass
class SaverProperties(BaseProperties):
    """
    Saver properties.

    Attributes
    ----------
    income_per_period : float
    savings : float

    """

    savings: float
    income_per_period: float

    def update(self, *args, payoff: float = 1.0, **kwargs) -> None:
        self.savings += self.income_per_period * payoff

    def reset(self) -> None:
        self.savings = 0.0
