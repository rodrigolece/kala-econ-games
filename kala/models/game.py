from abc import ABC, abstractmethod
from typing import Generic, Sequence
from warnings import warn

from kala.models.agents import AgentT
from kala.models.graphs import GraphT
from kala.models.strategies import StrategyT
from kala.utils.stats import choice


class DiscreteBaseGame(ABC, Generic[AgentT, GraphT, StrategyT]):
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
        players = self.match_opponents()

        if players is not None:
            payoffs = self.strategy.calculate_payoff(*players, **kwargs)

            for agent, pay in zip(players, payoffs):
                # printing just for debug purposes
                # TODO: remove
                saver_str = self.strategy._saver_encoding[  # pylint: disable=protected-access
                    agent.is_saver()
                ]
                print(f"Updating: {agent.uuid} ({saver_str})")

                agent.update(payoff=pay)

        self.time += 1

    def get_total_wealth(self) -> float:
        """Sum the total savings of all the agents."""
        out = 0.0
        for player in self.players:
            out += player.get_savings()

        return out


class DiscreteTwoByTwoGame(DiscreteBaseGame):
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

    coop = CooperationStrategy()

    game = DiscreteTwoByTwoGame(coop, agents, G)
    print(game.get_total_wealth())
    for _ in range(5):
        game.play_round()
        print(game.get_total_wealth())
