"""Module defining different types of agents"""
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from kala.models.properties import PropertiesT, SaverProperties

# from .strategies import BaseStrategy
from kala.models.traits import SaverTraits, TraitsT
from kala.utils.misc import universally_unique_identifier

# class NeighbourhoodMixin:
#     def __init__(self, graph: GraphT, node: int | str, *args, **kwargs):
#         self._graph = graph
#         self._node = node
#         self._neighbourhood = list(graph.get_neighbours(node))

#     def choose_neighbour(self, seed):
#         node = choice(self._neighbourhood, rng=seed)

# Inherit like so
# class BaseAgent(NeighbourhoodMixin, ABC):
# Inside __init__ initialise like so
#         # Explicitly need to call super bcs of non-standard init inside the Mixin
#         # See: https://stackoverflow.com/a/50465583/5998704
#         super().__init__(graph)


class BaseAgent(ABC, Generic[TraitsT, PropertiesT]):
    """
    Base agent meant to be subclassed.

    Attributes
    ----------
    uuid : int | str
        A unique identifier for the agent.

    Methods
    -------
    get_property()
    get_trait()
    update()
    reset()

    """

    # strategy: TODO
    _traits: TraitsT
    _properties: PropertiesT
    uuid: int | str

    def __init__(
        self,
        traits: TraitsT,
        properties: PropertiesT,
        uuid: int | str | None = None,
        rng: int | None = None,
    ) -> None:
        self._traits = traits
        self._properties = properties
        if uuid is None:
            uuid = universally_unique_identifier(rng=rng)
        self.uuid = uuid

    def __hash__(self):
        return hash(self.uuid)

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
    def update(self, *args, **kwargs) -> None:
        """Play one round of the game."""

    @abstractmethod
    def reset(self) -> None:
        """Reset the agent to starting values."""


AgentT = TypeVar("AgentT", bound=BaseAgent)
"""Used to refer to BaseAgent as well as its subclasses."""


class InvestorAgent(BaseAgent):
    """
    Investor agent.

    Methods
    -------
    update()
    get_savings()
    reset()

    """

    def __init__(
        self,
        is_saver: bool,
        min_specialization: float = 0.0,
        income_per_period: float = 1.0,
        update_from_n_last_games: int = 0,
        rng: int | None = None,
    ):
        """Initialise new investor agent.

        Parameters
        ----------
        is_saver : bool
            Boolean indicating whether the agent is a saver or not.
        min_specialization : float
            The minimum specialization (default is 0.0).
        income_per_period : float
            The income per period (default is 1.0).
        """

        traits = SaverTraits(
            group=0,  # not being used
            is_saver=is_saver,
            min_consumption=0,  # not being used
            min_specialization=min_specialization,
            updates_from_n_last_games=update_from_n_last_games,
            memory=[],
        )

        props = SaverProperties(
            savings=0.0,  # all agents initialised with zero savings
            income_per_period=income_per_period,
        )

        super().__init__(traits=traits, properties=props, rng=rng)

    def update(self, *args, **kwargs) -> None:
        self._properties.update(*args, **kwargs)
        self._traits.update(*args, **kwargs)

    def reset(self) -> None:
        self._properties.reset()

    def get_savings(self) -> float:
        """Handy direct access to property savings."""
        return self.get_property("savings")

    def is_saver(self) -> bool:
        """Handy direct access to trait is_saver."""
        return self.get_trait("is_saver")


if __name__ == "__main__":
    agent = InvestorAgent(is_saver=True)
    assert agent.is_saver()
    print(f"Hello from agent {agent.uuid}!")

    # agent.update(payoff=2, did_i_win=True)
    # assert agent.get_savings() == 2
    # agent.update(payoff=0.5, did_i_win=False)
    # assert agent.get_savings() == 2.5

    p = InvestorAgent(is_saver=True, update_from_n_last_games=4)
    p.get_trait("is_saver")

    for _ in range(5):
        p.update(payoff=1.0, did_i_win=False)
        print(p.get_trait("is_saver"))
