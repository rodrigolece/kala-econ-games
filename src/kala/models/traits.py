"""Module defining agent traits"""

from abc import ABC
from dataclasses import asdict, dataclass
from typing import Any, TypeVar


@dataclass
class BaseAgentTraits(ABC):
    """
    Base agent trait intended to be subclassed.

    Traits are similar to properties but conceptually they remain fixed.

    Methods
    -------
    to_dict()
        Return the traits as a dictionary.
    """

    def to_dict(self) -> dict[str, Any]:
        """
        Return the traits as a dictionary.

        Returns
        -------
        dict[str, Any]
        """
        return asdict(self)

    # going forward we can add other methods that are common to all Traits


TraitsT = TypeVar("TraitsT", bound=BaseAgentTraits)
"""Used to refer to BaseAgentTraits as well as its subclasses."""


@dataclass
class SaverTraits(BaseAgentTraits):
    """
    Saver traits.

    Attributes
    ----------
    group: int | None
    min_consumption: float
    min_specialization: float
    homophily: float | None

    """

    group: int | None
    min_consumption: float
    min_specialization: float
    homophily: float | None = None

    def __post_init__(self):
        # We deal with simple checks
        if not 0 <= self.min_specialization <= 1:
            raise ValueError("expected number between [0, 1] (inclusive) for 'min_specialization'")

        if self.homophily is not None and (not 0 <= self.homophily <= 1):
            raise ValueError("expected number between [0, 1] (inclusive) for 'homophily'")
