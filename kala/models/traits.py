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
    group: int
    is_saver: bool
    min_consumption: float
    min_specialization: float
    """

    group: int
    is_saver: bool
    min_consumption: float
    min_specialization: float

    def __post_init__(self):
        if not 0 <= self.min_specialization <= 1:
            raise ValueError("expected number between [0, 1] (inclusive) for 'min_specialization'")


if __name__ == "__main__":
    st = SaverTraits(group=0, is_saver=True, min_consumption=1, min_specialization=0.1)
    st_dict = st.to_dict()
    assert st.group == 0
    assert st_dict["group"] == st.group
    assert st.is_saver
    assert st_dict["is_saver"] == st.is_saver
    assert st.min_consumption == 1
    assert st_dict["min_consumption"] == st.min_consumption
    assert st.min_specialization == 0.1
    assert st_dict["min_specialization"] == st.min_specialization
