"""Module defining agent (and possibly other types of actors) properties"""

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import asdict, dataclass
from typing import Any, TypeVar

from kala.utils.config import DEBUG


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
    is_saver: bool
    income_per_period : float
    savings : float
    memory: deque | None

    """

    is_saver: bool
    savings: float
    income_per_period: float
    memory: deque | None = None

    # pylint: disable=unused-argument
    def update(self, *args, **kwargs) -> None:
        """Update the savings and the is_saver attribute depending on the update_rule and memory."""

        # Update the savings
        payoff = kwargs.get("payoff", 0.0)
        self.savings += self.income_per_period * payoff

        if self.memory is None:
            return

        # Check if the update_rule for the memory holds
        if (successful_round := kwargs.get("successful_round", None)) is None:
            raise ValueError("expected 'successful_round' keyword argument")

        if (update_rule := kwargs.get("update_rule", None)) is None:
            raise ValueError("expected 'update_rule' keyword argument")

        memory: deque = self.memory  # type: ignore
        memory.append(successful_round)

        if update_rule.should_update(memory):
            if DEBUG:
                user_str = f"{uuid} " if (uuid := kwargs.get("uuid", None)) else ""
                print(f"{user_str}is flipping: {self.is_saver}->{not self.is_saver}")

            self.flip_saver_property()
            self.memory = deque([], maxlen=memory.maxlen)

    def flip_saver_property(self) -> None:
        """Flip the is_saver property."""
        self.is_saver = not self.is_saver

    def reset(self) -> None:
        """Reset the SaverProperties to their initial values"""
        self.savings = 0.0

        if self.memory is not None:
            self.memory = deque([], maxlen=self.memory.maxlen)
