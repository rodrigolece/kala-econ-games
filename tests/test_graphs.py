"""Test the graphs module."""

import pytest

from kala.models.agents import SaverAgent
from kala.models.graphs import AgentPlacementNetX, get_neighbours


def test_get_agent_get_neighbours(
    init_networkx_graph,
    init_agent_placement,
):
    """Test the methods get_agent and get_neighbours."""
    g = init_networkx_graph  # pylint: disable=invalid-name
    plcmt = init_agent_placement

    # get_node using the identifier
    n0 = plcmt.get_agent(0)
    assert isinstance(n0, SaverAgent)

    neighs = get_neighbours(n0, g, plcmt)
    assert len(neighs) == 2
    assert all(isinstance(n, SaverAgent) for n in neighs)

    n2 = plcmt.get_agent(2)
    assert len(get_neighbours(n2, g, plcmt)) == 3


def test_get_position(init_agents, init_networkx_graph, init_agent_placement):
    """Test the method get_position."""
    plcmt = init_agent_placement
    g = init_networkx_graph  # pylint: disable=invalid-name

    agent = init_agents[2]
    assert plcmt.get_position(agent) == 2

    neighs = get_neighbours(agent, g, plcmt)  # repeats test above
    assert len(neighs) == 3


def test_add_agent(init_agents):
    """Test the method add_agent."""
    plcmt = AgentPlacementNetX()
    for i, a in enumerate(init_agents):
        plcmt.add_agent(a, i)

    with pytest.raises(ValueError):
        plcmt.add_agent(init_agents[0], 0)  # already full


def test_clear_node(init_networkx_graph, init_agent_placement):
    """Test the method remove_node."""
    plcmt = init_agent_placement

    agent = plcmt.get_agent(2)
    neighs = get_neighbours(agent, init_networkx_graph, plcmt)
    assert len(neighs) == 3

    plcmt.clear_node(3)
    neighs = get_neighbours(agent, init_networkx_graph, plcmt)
    assert len(neighs) == 2
