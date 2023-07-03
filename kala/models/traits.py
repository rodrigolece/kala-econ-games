"""Module defining agent traits"""
from abc import ABC
from dataclasses import asdict, dataclass
from typing import Any, TypeVar


@dataclass
class BaseAgentTraits(ABC):
    """
    Base agent trait intended to be subclassed.

    Traits are similar to properties but conceptually they remain fixed.

    Attributes
    ----------

    Methods
    -------
    as_dict()
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


# pylint: disable=invalid-name
TraitsType = TypeVar("TraitsType", bound=BaseAgentTraits)
"""Used to refer to BaseAgentTraits as well as its subclasses."""


@dataclass
class SaverTraits(BaseAgentTraits):
    """
    Saving trait.

    Attributes
    ----------
    group: int
    savings_share: float
    min_consumption: float
    min_specialization: float
    """

    group: int
    savings_share: float
    min_consumption: float
    min_specialization: float

    def __post_init__(self):
        if self.savings_share < 0 or self.savings_share > 1:
            raise ValueError("expected number between [0, 1] (inclusive) for savings_share")
        if self.min_specialization < 0 or self.min_specialization > 1:
            raise ValueError("expected number between [0, 1] (inclusive) for min_specialization")


if __name__ == "__main__":
    st = SaverTraits(group=0, savings_share=0.1, min_consumption=1, min_specialization=0.1)
    assert st.group == 0
    assert st.to_dict()["group"] == 0
    assert st.savings_share == 0.1
    assert st.to_dict()["savings_share"] == 0.1
    assert st.min_consumption == 1
    assert st.to_dict()["min_consumption"] == 1
    assert st.min_specialization == 0.1
    assert st.to_dict()["min_specialization"] == 0.1
