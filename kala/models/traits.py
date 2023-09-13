"""Module defining agent traits"""
from abc import ABC
from dataclasses import asdict, dataclass, field
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
    memory: list[bool]
    """

    group: int
    is_saver: bool
    min_consumption: float
    min_specialization: float
    updates_from_n_last_games: int
    memory: list[bool] = field(default_factory=list)

    def __post_init__(self):
        if not 0 <= self.min_specialization <= 1:
            raise ValueError("expected number between [0, 1] (inclusive) for 'min_specialization'")

        if self.updates_from_n_last_games < 0:
            raise ValueError("expected positive number (integer)")

    def update(self, did_i_win: bool, *args, **kwargs) -> None:
        if len(self.memory) > self.updates_from_n_last_games:
            self.memory.pop(0)
        self.memory.append(did_i_win)

        if len(self.memory) == self.updates_from_n_last_games:
            if sum(self.memory) < self.updates_from_n_last_games / 2:
                new_status = not self.is_saver
                self.is_saver = new_status


if __name__ == "__main__":
    st = SaverTraits(
        group=0,
        is_saver=True,
        min_consumption=1,
        min_specialization=0.1,
        updates_from_n_last_games=0,
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
