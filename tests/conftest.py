"""Pytest configuration file."""

import networkx as nx
import pytest

from kala.models.agents import init_saver_agent
from kala.models.graphs import AgentPlacementNetX

# from kala.models.game import DiscreteTwoByTwoGame
# from kala.models.strategies import CooperationStrategy


@pytest.fixture(scope="module")
def init_agents():
    """Return a list of agents."""
    is_saver = [True] * 3 + [False] * 3
    groups = [0] * 3 + [1] * 3
    agents = [init_saver_agent(is_saver=s, group=g) for s, g in zip(is_saver, groups)]
    return agents


@pytest.fixture(scope="module")
def init_networkx_graph():
    """Return the butterfly graph."""
    g = nx.Graph()
    g.add_edges_from([(0, 1), (0, 2), (1, 2), (2, 3), (3, 4), (3, 5), (4, 5)])
    return g


@pytest.fixture(scope="function")
def init_agent_placement(init_agents, init_networkx_graph):
    """Return an agent placement."""
    return AgentPlacementNetX.init_bijection(init_agents, init_networkx_graph)


# @pytest.fixture(scope="module")
# def init_deterministic_cooperation_strategy():
#     """Return a cooperation strategy."""
#     return CooperationStrategy(stochastic=False)


# @pytest.fixture(scope="function")
# def init_deterministic_game(init_simple_graph, init_deterministic_cooperation_strategy):
#     """Return a game."""
#     return DiscreteTwoByTwoGame(
#         init_simple_graph, init_deterministic_cooperation_strategy
#     )
