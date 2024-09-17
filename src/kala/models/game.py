"""Module defining the top-level classes of games that put everything together."""

import itertools
from abc import ABC, abstractmethod
from typing import Any, Generic, Sequence, TypeVar

import numpy as np
from numpy.random import Generator

from kala.models.graphs import GraphT
from kala.models.strategies import StrategyT


class DiscreteBaseGame(ABC, Generic[GraphT, StrategyT]):
    """
    Base game meant to be subclassed.

    Attributes
    ----------
    time : int
        The current time of the game.
    graph : GraphT
        The graph connecting the agents.
    strategy : StrategyT
        The strategy of the agents.

    Methods
    -------
    match_opponents()
    play_round()
    get_num_players()
    get_total_wealth()
    create_filter_from_property()
    create_filter_from_trait()
    get_num_savers()
    reset_agents()

    """

    time: int
    graph: GraphT
    strategy: StrategyT

    def __init__(self, graph: GraphT, strategy: StrategyT):
        self.time = 0
        self.graph = graph
        self.strategy = strategy

    def __str__(self) -> str:
        graph_str = type(self.graph).__name__
        stgy_str = type(self.strategy).__name__
        t, np = self.time, self.get_num_players()
        return f"{self.__class__.__name__}[{graph_str}, {stgy_str}](time={t}, num_players={np})"

    def __repr__(self) -> str:
        return f"<{str(self)}>"

    def _get_players(self):
        # NB: networkx; implementation makes it necessary to call this method to filter out None's
        return self.graph.get_nodes()

    def get_num_players(self) -> int:
        """
        Return the number of players.

        Returns
        -------
        int

        """
        return self.graph.num_nodes()

    @abstractmethod
    def match_opponents(self, rng: Generator | int | None = None, **kwargs) -> tuple | None:
        """Return a pair of matched opponents."""

    # pylint: disable=unused-argument
    def play_round(self, *args, **kwargs) -> None:
        """Match two opponents and advance the time."""
        if (rng := kwargs.get("rng", None)) is not None:
            kwargs["rng"] = np.random.default_rng(rng)

        for _ in range(self.get_num_players() // 2):
            if (players := self.match_opponents(**kwargs)) is not None:
                payoffs = self.strategy.calculate_payoff(*players, **kwargs)
                achieved_max_payoff = np.array(payoffs) == max(payoffs)

                for agent, pay, success in zip(players, payoffs, achieved_max_payoff):
                    agent.update(payoff=pay, successful_round=success)

        self.time += 1

    def get_total_wealth(self, filt: Sequence[bool] | None = None) -> float:
        """
        Sum the total savings of all the players.

        Parameters
        ----------
        filt : Sequence[bool], optional
            A sequence of booleans to keep a subset of the players.

        Returns
        -------
        float

        """
        out = 0.0
        if filt is not None:
            assert len(filt) == self.get_num_players(), "'filt' must be the same length as players"
        players = (
            itertools.compress(self._get_players(), filt)
            if filt is not None
            else self._get_players()
        )

        for player in players:
            out += player.get_property("savings")

        return out

    def create_filter_from_trait(self, trait_name: str, trait_value: Any = True) -> list[bool]:
        """
        Create a filter from a trait name and value.

        Parameters
        ----------
        trait_name : str
            The name of the trait.
        trait_value : Any, optional
            The value of the trait, by default True ('is_saver', which would be the primary use
            case, is a boolean).

        Returns
        -------
        list[bool]

        """
        return [player.get_trait(trait_name) == trait_value for player in self._get_players()]

    def create_filter_from_property(self, prop_name: str, prop_value: Any = True) -> list[bool]:
        """
        Create a filter from a property name and value.

        Parameters
        ----------
        prop_name : str
            The name of the property.
        prop_value : Any, optional
            The value of the property, by default True ('is_saver', which would be the primary use
            case, is a boolean).

        Returns
        -------
        list[bool]

        """
        return [player.get_property(prop_name) == prop_value for player in self._get_players()]

    def get_num_savers(self) -> int:
        """
        Return the number of savers.

        Returns
        -------
        int

        """
        return sum(self.create_filter_from_property("is_saver"))

    def reset_agents(self) -> None:
        """Reset the savings of agents to their initial state."""
        for player in self._get_players():
            player.reset()


DiscreteGameT = TypeVar("DiscreteGameT", bound=DiscreteBaseGame)
"""Used to refer to DiscreteBaseGame as well as its subclasses."""


class DiscreteTwoByTwoGame(DiscreteBaseGame):
    """
    A discrete 2x2 game where agents play their strategy in pairs.

    """

    def match_opponents(self, rng: Generator | int | None = None, **kwargs) -> tuple | None:
        player = self.graph.select_random_node(rng=rng)
        opponent = self.graph.select_random_neighbour(player, rng=rng)
        if opponent is None:
            return None

        # print(f"{p.uuid} ({p.get_trait('is_saver')}) - {o.uuid} ({o.get_trait('is_saver')})")
        return player, opponent
