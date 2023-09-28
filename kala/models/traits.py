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
    group: int
    is_saver: bool
    min_consumption: float
    min_specialization: float
    updates_from_n_last_games: int
    memory: deque | None
    """

    group: int
    is_saver: bool
    min_consumption: float
    min_specialization: float
    updates_from_n_last_games: int
    memory: deque | None = None
    # TODO: we should move 'memory' to properties bcs we shouldn't really have
    # the 'update' and 'reset' methods below

    def __post_init__(self):
        if not 0 <= self.min_specialization <= 1:
            raise ValueError("expected number between [0, 1] (inclusive) for 'min_specialization'")

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

        memory: deque = self.memory  # type: ignore[assignment]
        memory.append(successful_round)
        n = memory.maxlen  # pylint: disable=invalid-name, type: ignore[override]

        if len(memory) == n and sum(memory) < n / 2:
            # TODO: for debug, get rid of print below
            # print(f"user is flipping: {self.is_saver}->{not self.is_saver}")
            self.is_saver = not self.is_saver
            self.memory = deque([], maxlen=self.updates_from_n_last_games)

    def reset(self) -> None:
        """Reset the agent memory."""
        if self.memory is not None:
            self.memory = deque([], maxlen=self.updates_from_n_last_games)


if __name__ == "__main__":
    st = SaverTraits(
        group=0,
        is_saver=True,
        min_consumption=1,
        min_specialization=0.1,
        updates_from_n_last_games=2,
    )
    st_dict = st.to_dict()
    assert st.group == 0
    assert st_dict["group"] == st.group
    assert st.is_saver
    assert st_dict["is_saver"] == st.is_saver
    assert st.min_consumption == 1
    assert st_dict["min_consumption"] == st.min_consumption
    assert st.min_specialization == 0.1
    assert st_dict["min_specialization"] == st.min_specialization

    st.update(successful_round=1)
    st.update(successful_round=2)
    st.update(successful_round=3)  # this should push out the first value
    assert list(st.memory) == [2, 3]  # type: ignore
