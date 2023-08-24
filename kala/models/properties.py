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
    to_dict()
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
    def update(self, *args, **kwargs) -> None:
        """Do an update of the properties according to the class' internal rules."""

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


if __name__ == "__main__":
    sp = SaverProperties(savings=0, income_per_period=1)
    # sp_dict = sp.to_dict() # this wouldn't pass 2nd assert
    sp.update(payoff=1)
    sp.update(payoff=1)
    assert sp.savings == 2

    sp_dict = sp.to_dict()  # NB: dict has copied values, not references
    assert sp_dict["savings"] == sp.savings
