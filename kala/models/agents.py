"""Module defining different types of agents"""
from abc import ABC, abstractmethod
from typing import Any, TypeVar

from models.properties import PropertiesType, SaverProperties

# from .strategies import BaseStrategy
from models.traits import SaverTraits, TraitsType

from utils.misc import uuid


class BaseAgent(ABC):
    """
    Base agent (protocol) meant to be subclassed.

    Attributes
    ----------

    Methods
    -------
    play_strategy()

    """

    # strategy: TODO
    _traits: TraitsType
    _properties: PropertiesType
    uuid: str

    def __init__(self, traits: TraitsType, properties: PropertiesType) -> None:
        self._traits = traits
        self._properties = properties
        self.uuid = uuid()

        # NB: the idea below isn't super useful bcs it doesn't copy using pointers
        # possible to fix?
        # for key, val in traits.to_dict().items():
        #     setattr(self, f"_trait_{key}", val)

        # for key, val in properties.to_dict().items():
        #     setattr(self, f"_property_{key}", val)

    # pylint: disable=protected-access
    def get_property(self, property_name: str) -> Any:
        """
        Get a property value (returns None for an invalid name).

        Parameters
        ----------
        property_name : str
            The name of the property.

        Returns
        -------
        Any

        """
        return getattr(self._properties, property_name)

    # pylint: disable=protected-access
    def get_trait(self, trait_name: str) -> Any:
        """
        Get a trait value (returns None for an invalid name).

        Parameters
        ----------
        trait_name : str
            The name of the trait.

        Returns
        -------
        Any

        """
        return getattr(self._traits, trait_name)

    @abstractmethod
    def play_strategy(self, *args, **kwargs) -> None:
        """Play one round of the game."""


# pylint: disable=invalid-name
AgentType = TypeVar("AgentType", bound=BaseAgent)
"""Used to refer to BaseAgent as well as its subclasses."""


class InvestorAgent(BaseAgent):
    def __init__(
        self,
        is_saver: bool,
        group: int,
        income_per_period: float = 1.0,
        specialization_degree: float = 0.0,
    ):
        """Investor agent.

        Parameters
        ----------
        is_saver : bool
            _description_
        group : int
            _description_
        income_per_period : float
            _description_ (default is 1.0).
        specialization_degree : float
            _description_ (default is 0.0).
        """
        # Checks
        if group not in [0, 1]:
            raise ValueError("the agent group must be 0 or 1")
        traits = SaverTraits(is_saver, group)

        if specialization_degree < 0 or specialization_degree > 1:
            raise ValueError("expected number between [0, 1] (inclusive)")
        props = SaverProperties(
            total_savings=0,
            income_per_period=income_per_period,
            specialization_degree=specialization_degree,
        )

        super().__init__(traits=traits, properties=props)

    def play_strategy(self, *args, **kwargs) -> None:
        self._properties.update()


if __name__ == "__main__":
    agent = InvestorAgent(is_saver=True, group=0)
    print(f"Hello from agent {agent.uuid}!")
    assert agent.get_trait("is_saver")
    agent.play_strategy()
    agent.play_strategy()
    assert agent.get_property("total_savings") == 2
