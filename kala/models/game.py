from abc import ABC, abstractmethod
from typing import Sequence
from warnings import warn

# for testing
import networkx as nx
from models.agents import AgentType, InvestorAgent
from models.graphs import GraphType, SimpleGraph

from utils.stats import choice


class DiscreteBaseGame(ABC):
    time: int
    players: Sequence[AgentType]
    graph: GraphType
    _num_players: int

    def __init__(self, players: Sequence[AgentType], graph: GraphType):
        self.time = 0
        self.players = players
        self.graph = graph
        self._num_players = len(players)

    @abstractmethod
    def match_opponents(self, *args, **kwargs) -> tuple | None:
        """Returned (two or more) matched opponents."""

    def advance_time(self):
        players = self.match_opponents()
        if players is not None:
            for agent in players:
                agent.play_strategy()
        self.time += 1


class DiscreteTwoByTwoGame(DiscreteBaseGame):
    def match_opponents(self, seed: int | None = None) -> tuple | None:
        player_id = choice(range(self._num_players), rng=seed)
        player = self.graph.get_node(player_id)
        neighs = self.graph.get_neighbours(player_id)

        if len(neighs) == 0:
            warn("selected player does not have any neighbours")
            return None
        else:
            opponent = choice(neighs)

        return player, opponent


if __name__ == "__main__":
    num_players = 10

    # A list of InvestorAgents
    players = [InvestorAgent(is_saver=True, group=0) for _ in range(num_players)]

    g = nx.barabasi_albert_graph(num_players, 8, seed=0)
    G = SimpleGraph(g, nodes=players)

    game = DiscreteTwoByTwoGame(players, G)
    game.advance_time()
