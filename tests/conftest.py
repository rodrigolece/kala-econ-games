"""Pytest configuration file."""

import networkx as nx
import pytest

from kala import (
    AgentPlacementNetX,
    GameState,
    MatchingStrategy,
    SaverCooperationPayoffStrategy,
    init_saver_agent,
)


@pytest.fixture(scope="function")
def fixture_networkx_graph():
    """Return the butterfly graph."""
    g = nx.Graph()
    g.add_edges_from([(0, 1), (0, 2), (1, 2), (2, 3), (3, 4), (3, 5), (4, 5)])
    return g


@pytest.fixture(scope="function")
def fixture_saver_agents():
    """Return a list of 3 saver agents and 3 non-saver agents."""
    is_saver = [True] * 3 + [False] * 3
    groups = [0] * 3 + [1] * 3
    agents = [init_saver_agent(is_saver=s, group=g) for s, g in zip(is_saver, groups)]
    return agents


@pytest.fixture(scope="function")
def fixture_agent_placement(fixture_saver_agents, fixture_networkx_graph):
    """Return an agent placement."""
    return AgentPlacementNetX.init_bijection(fixture_saver_agents, fixture_networkx_graph)


@pytest.fixture(scope="module")
def fixture_deterministic_cooperation_strategy():
    """Return a deterinistic cooperation strategy."""
    return SaverCooperationPayoffStrategy(stochastic=False)


@pytest.fixture(scope="module")
def fixture_matching_strategy():
    """Return a deterministic matching strategy."""
    return MatchingStrategy()


@pytest.fixture(scope="function")
def fixture_game_state(
    fixture_networkx_graph,
    fixture_saver_agents,
    fixture_agent_placement,
    fixture_deterministic_cooperation_strategy,
    fixture_matching_strategy,
):
    """Return a game."""
    return GameState(
        graph=fixture_networkx_graph,
        agents=fixture_saver_agents,
        placements=fixture_agent_placement,
        payoff_strategy=fixture_deterministic_cooperation_strategy,
        matching_strategy=fixture_matching_strategy,
    )
