from abc import ABC, abstractmethod
from typing import Generic, Sequence
from warnings import warn

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
    players : Sequence[AgentT]
        A list of agents.
    graph : GraphT
        The graph connecting the agents.
    strategy : StrategyT
        The strategy of the agents.

    Methods
    -------
    match_opponents()
    play_round()
    get_total_wealth()

    """

    time: int
    players: Sequence[AgentT]
    graph: GraphT
    strategy: StrategyT
    _num_players: int

    def __init__(self, strategy: StrategyT, players: Sequence[AgentT], graph: GraphT):
        self.strategy = strategy
        self.players = players
        self.graph = graph
        self._num_players = len(players)
        self.time = 0

    @abstractmethod
    def match_opponents(self, seed: int | None = None) -> tuple | None:
        """Return a pair of matched opponents."""

    # pylint: disable=unused-argument
    def play_round(self, *args, **kwargs) -> None:
        """Match two opponents and advance the time."""
        for _ in range(self._num_players // 2):
            if (players := self.match_opponents()) is not None:
                payoffs = self.strategy.calculate_payoff(*players, **kwargs)

                for agent, pay in zip(players, payoffs):
                    agent.update(payoff=pay)

        self.time += 1

    def get_total_wealth(self) -> float:
        """Sum the total savings of all the agents."""
        out = 0.0
        for player in self.players:
            out += player.get_savings()

        return out


class DiscreteTwoByTwoGame(DiscreteBaseGame):
    """
    A discrete 2x2 game where agents play their strategy in pairs.

    """

    def match_opponents(self, seed: int | None = None) -> tuple | None:
        player = choice(self.players, rng=seed)

        neighs = self.graph.get_neighbours(player)
        if len(neighs) == 0:
            warn("selected player does not have any neighbours")
            return None

        opponent = choice(neighs)
        return player, opponent


if __name__ == "__main__":
    import networkx as nx

    from kala.models.agents import InvestorAgent
    from kala.models.graphs import SimpleGraph
    from kala.models.strategies import CooperationStrategy

    num_players = 10

    # A list of InvestorAgents
    savers = [True, False] * 5
    agents = [InvestorAgent(is_saver=savers[i]) for i in range(num_players)]

    g = nx.barabasi_albert_graph(num_players, 8, seed=0)
    G = SimpleGraph(g, nodes=agents)

    # coop = CooperationStrategy()
    coop = CooperationStrategy(stochastic=True, rng=0)

    game = DiscreteTwoByTwoGame(coop, agents, G)
    print(game.get_total_wealth())
    for _ in range(5):
        game.play_round()
        print(game.get_total_wealth())
