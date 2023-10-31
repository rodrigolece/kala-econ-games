"""Module defining different types of agents"""
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from kala.models.memory_rules import AverageMemoryRule, MemoryRuleT
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


class BaseAgent(
    ABC,
    Generic[TraitsT, PropertiesT, MemoryRuleT],
):
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
    update_rule: MemoryRuleT
    uuid: int | str

    def __init__(
        self,
        traits: TraitsT,
        properties: PropertiesT,
        update_rule: MemoryRuleT | None = None,
        uuid: int | str | None = None,
        rng: int | None = None,
    ) -> None:
        self._traits = traits
        self._properties = properties

        self.update_rule = (
            AverageMemoryRule() if update_rule is None else update_rule  # type: ignore
        )

        self.uuid = universally_unique_identifier(rng=rng) if uuid is None else uuid

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

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        is_saver: bool,
        min_specialization: float = 0.0,
        income_per_period: float = 1.0,
        homophily: float | None = None,
        update_from_n_last_games: int = 0,
        update_rule: MemoryRuleT | None = None,
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
        homophily : float | None
            The homophily of the agent (default is None), if passed should be a
            number between [0, 1].
        update_from_n_last_games : int
            The number of previous outcomes kept in memory to decide whether to
            change the saving strategy (default is 0).
        update_rule: MemoryRuleT | None
            The rule used to decide whether the agent should change their saver
             status depending on the outcome of the previous matches (default is None).
        """

        traits = SaverTraits(
            group=0,  # not being used
            is_saver=is_saver,
            min_consumption=0,  # not being used
            min_specialization=min_specialization,
            homophily=homophily,
            updates_from_n_last_games=update_from_n_last_games,
        )

        props = SaverProperties(
            savings=0.0,  # all agents initialised with zero savings
            income_per_period=income_per_period,
        )

        super().__init__(
            traits=traits,
            properties=props,
            update_rule=update_rule,
            rng=rng,
        )

    def update(self, *args, **kwargs) -> None:
        self._properties.update(*args, **kwargs)
        self._traits.update(*args, update_rule=self.update_rule, **kwargs)

    def reset(self) -> None:
        self._properties.reset()
        self._traits.reset()

    def get_savings(self) -> float:
        """Handy direct access to property savings."""
        return self.get_property("savings")

    def is_saver(self) -> bool:
        """Handy direct access to trait is_saver."""
        return self.get_trait("is_saver")


if __name__ == "__main__":
    import numpy as np

    agent = InvestorAgent(is_saver=True)
    assert agent.is_saver()
    print(f"Hello from agent {agent.uuid}!")

    agent.update(payoff=2)
    assert agent.get_savings() == 2
    agent.update(payoff=0.5)
    assert agent.get_savings() == 2.5

    n_games = 5
    agent_w_memory = InvestorAgent(is_saver=False, update_from_n_last_games=n_games)
    print(f"Hello from agent {agent_w_memory.uuid} with {n_games} games of memory!")

    a = np.array([False] * (n_games - 1) + [True])
    expected_states = np.hstack((a, ~a))

    for i in range(2 * n_games):
        agent_w_memory.update(payoff=1.0, successful_round=False)
        # print("\tis saver:", agent_w_memory.is_saver())
        assert agent_w_memory.is_saver() == expected_states[i]
