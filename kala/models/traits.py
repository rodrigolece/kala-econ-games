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
    is_saver : bool
    """

    is_saver: bool
    group: int


if __name__ == "__main__":
    st = SaverTraits(is_saver=True, group=0)
    assert st.is_saver
    assert st.to_dict()["is_saver"]
