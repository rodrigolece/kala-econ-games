"""Pytest configuration file."""

import string

import networkx as nx
import pytest

from kala.models.agents import InvestorAgent
from kala.models.game import DiscreteTwoByTwoGame
from kala.models.graphs import SimpleGraph
from kala.models.strategies import CooperationStrategy


@pytest.fixture(scope="module")
def init_agents():
    """Return a list of agents."""
    is_saver = [True] * 3 + [False] * 3
    groups = [0] * 3 + [1] * 3
    agents = [
        InvestorAgent(is_saver=s, group=g, uuid=letter)
        for s, g, letter in zip(is_saver, groups, string.ascii_lowercase)
    ]
    return agents


@pytest.fixture(scope="function")
def init_simple_graph(init_agents):
    """Return a simple graph."""
    g = nx.Graph()
    g.add_edges_from([(0, 1), (0, 2), (1, 2), (2, 3), (3, 4), (3, 5), (4, 5)])
    return SimpleGraph(g, nodes=init_agents)


@pytest.fixture(scope="module")
def init_deterministic_cooperation_strategy():
    """Return a cooperation strategy."""
    return CooperationStrategy(stochastic=False)


@pytest.fixture(scope="function")
def init_deterministic_game(init_simple_graph, init_deterministic_cooperation_strategy):
    """Return a game."""
    return DiscreteTwoByTwoGame(init_simple_graph, init_deterministic_cooperation_strategy)
