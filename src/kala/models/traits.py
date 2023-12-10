"""Module defining agent traits"""

from abc import ABC
from collections import deque
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
    is_saver: bool
    group: int | None
    min_consumption: float
    min_specialization: float
    homophily: float | None
    updates_from_n_last_games: int
    memory: deque | None
    """

    is_saver: bool
    group: int | None
    min_consumption: float
    min_specialization: float
    homophily: float | None = None
    updates_from_n_last_games: int = 0
    memory: deque | None = None
    # TODO: move 'memory' to properties bcs we shouldn't really have 'update' and 'reset' methods

    def __post_init__(self):
        # First we deal with simple checks
        if not 0 <= self.min_specialization <= 1:
            raise ValueError("expected number between [0, 1] (inclusive) for 'min_specialization'")

        if self.homophily is not None and (not 0 <= self.homophily <= 1):
            raise ValueError("expected number between [0, 1] (inclusive) for 'homophily'")

        # Memory related stuff
        if self.updates_from_n_last_games < 0 or not isinstance(
            self.updates_from_n_last_games, int
        ):
            raise ValueError("expected non-negative integer for 'updates_from_n_last_games'")

        # initialise memory
        if self.memory is None and self.updates_from_n_last_games > 0:
            self.memory = deque([], maxlen=self.updates_from_n_last_games)

    # pylint: disable=unused-argument
    def update(self, *args, **kwargs) -> None:
        """Update the is_saver attribute depending on updating rule and memory."""
        if self.updates_from_n_last_games == 0:
            return

        if (successful_round := kwargs.get("successful_round", None)) is None:
            raise ValueError("expected 'successful_round' keyword argument")

        if (update_rule := kwargs.get("update_rule", None)) is None:
            raise ValueError("expected 'update_rule' keyword argument")

        memory: deque = self.memory  # type: ignore
        memory.append(successful_round)

        if update_rule.should_update(memory):
            # print below is useful for debugging
            # print(f"user is flipping: {self.is_saver}->{not self.is_saver}")
            self.flip_saver_trait()
            self.memory = deque([], maxlen=self.updates_from_n_last_games)

    def flip_saver_trait(self) -> None:
        """Flip the is_saver trait."""
        self.is_saver = not self.is_saver

    def change_memory_length(self, new_memory_length: int) -> None:
        "Change the memory length of an agent."
        self.updates_from_n_last_games = new_memory_length

    def reset(self) -> None:
        """Reset the agent memory."""
        if self.memory is not None:
            self.memory = deque([], maxlen=self.updates_from_n_last_games)
