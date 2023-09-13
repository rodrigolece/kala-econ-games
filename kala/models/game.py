import itertools
from abc import ABC, abstractmethod
from typing import Generic, Sequence
from warnings import warn

import numpy as np
from numpy.random import Generator

from kala.models.agents import AgentT
from kala.models.graphs import GraphT
from kala.models.strategies import StrategyT
from kala.utils.stats import choice


class DiscreteBaseGame(ABC, Generic[AgentT, GraphT, StrategyT]):
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
    get_total_wealth()
    get_savers()
    get_number_of_savers()
    reset_agents()

    """

    time: int
    graph: GraphT
    strategy: StrategyT
    _players: Sequence[AgentT]
    _num_players: int

    def __init__(self, graph: GraphT, strategy: StrategyT):
        self.time = 0
        self.graph = graph
        self.strategy = strategy
        self._players = graph._nodes
        self._num_players = graph.num_nodes()

    @abstractmethod
    def match_opponents(self, rng: Generator | int | None = None, **kwargs) -> tuple | None:
        """Return a pair of matched opponents."""

    # pylint: disable=unused-argument
    def play_round(self, *args, **kwargs) -> None:
        """Match two opponents and advance the time."""
        if (rng := kwargs.get("rng", None)) is not None:
            kwargs["rng"] = np.random.default_rng(rng)

        for _ in range(self._num_players // 2):
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
            assert len(filt) == self._num_players, "'filt' must be the same length as players"
        players = itertools.compress(self._players, filt) if filt is not None else self._players

        for player in players:
            out += player.get_property("savings")

        return out

    def get_savers(self) -> Sequence[AgentT]:
        """
        Return a list of savers.

        Returns
        -------
        Sequence[AgentT]

        """
        return [player for player in self._players if player.get_trait("is_saver")]

    def get_number_of_savers(self) -> int:
        """
        Return the number of savers.

        Returns
        -------
        int

        """
        return len(self.get_savers())

    def reset_agents(self) -> None:
        """Reset the savings of agents to their initial state."""
        for player in self._players:
            player.reset()


class DiscreteTwoByTwoGame(DiscreteBaseGame):
    """
    A discrete 2x2 game where agents play their strategy in pairs.

    """

    def match_opponents(self, rng: Generator | int | None = None, **kwargs) -> tuple | None:
        player = choice(self._players, rng=rng)

        neighs = self.graph.get_neighbours(player)
        if len(neighs) == 0:
            warn("selected player does not have any neighbours")
            return None

        opponent = choice(neighs, rng=rng)
        # print(f"{p.uuid} ({p.get_trait('is_saver')}) - {o.uuid} ({o.get_trait('is_saver')})")
        return player, opponent


if __name__ == "__main__":
    import networkx as nx

    from kala.models.agents import InvestorAgent
    from kala.models.graphs import SimpleGraph
    from kala.models.strategies import CooperationStrategy

    num_players = 10

    # A list of InvestorAgents
    savers = [True, False] * (num_players // 2)
    agents = [
        InvestorAgent(is_saver=savers[i], update_from_n_last_games=1, rng=i)
        for i in range(num_players)
    ]

    g = nx.barabasi_albert_graph(num_players, 8, seed=0)
    G = SimpleGraph(g, nodes=agents)

    # coop = CooperationStrategy()
    coop = CooperationStrategy(
        stochastic=True, differential_efficient=0.5, differential_inefficient=0.05, rng=0
    )

    game = DiscreteTwoByTwoGame(G, coop)
    wealth, num_savers = game.get_total_wealth(), game.get_number_of_savers()
    print(f"Init: wealth={wealth:.2f}, {num_savers=}")

    for _ in range(10):
        game.play_round()
        wealth, num_savers = game.get_total_wealth(), game.get_number_of_savers()
        print(f"wealth={wealth:.2f}, {num_savers=}")
