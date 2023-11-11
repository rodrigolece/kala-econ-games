"""Pytest configuration file."""

import networkx as nx
import pytest

from kala.models.agents import InvestorAgent
from kala.models.graphs import SimpleGraph


NUM_NODES = 10


@pytest.fixture(scope="module")
def init_agents():
    """Return a list of agents."""
    savers = [True, False] * (NUM_NODES // 2)
    agents = [InvestorAgent(is_saver=savers[i]) for i in range(NUM_NODES)]
    return agents


@pytest.fixture(scope="module")
def init_simple_graph(init_agents):
    """Return a simple graph."""
    g = nx.barabasi_albert_graph(NUM_NODES, 8, seed=0)
    return SimpleGraph(g, nodes=init_agents)
