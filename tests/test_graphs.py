"""Test the graphs module."""

import pytest

from kala.models.agents import SaverAgent
from kala.models.graphs import AgentPlacementNetX, get_neighbours


def test_get_agent_get_neighbours(
    fixture_networkx_graph,
    fixture_agent_placement,
):
    """Test the methods get_agent and get_neighbours."""
    g = fixture_networkx_graph  # pylint: disable=invalid-name
    plcmt = fixture_agent_placement

    # get_node using the identifier
    n0 = plcmt.get_agent(0)
    assert isinstance(n0, SaverAgent)

    neighs = get_neighbours(n0, g, plcmt)
    assert len(neighs) == 2
    assert all(isinstance(n, SaverAgent) for n in neighs)

    n2 = plcmt.get_agent(2)
    assert len(get_neighbours(n2, g, plcmt)) == 3


def test_get_position(fixture_saver_agents, fixture_networkx_graph, fixture_agent_placement):
    """Test the method get_position."""
    plcmt = fixture_agent_placement
    g = fixture_networkx_graph  # pylint: disable=invalid-name

    agent = fixture_saver_agents[2]
    assert plcmt.get_position(agent) == 2

    neighs = get_neighbours(agent, g, plcmt)  # repeats test above
    assert len(neighs) == 3


def test_add_agent(fixture_saver_agents):
    """Test the method add_agent."""
    plcmt = AgentPlacementNetX()
    for i, a in enumerate(fixture_saver_agents):
        plcmt.add_agent(a, i)

    with pytest.raises(ValueError):
        plcmt.add_agent(fixture_saver_agents[0], 0)  # already full


def test_clear_node(fixture_networkx_graph, fixture_agent_placement):
    """Test the method remove_node."""
    plcmt = fixture_agent_placement

    agent = plcmt.get_agent(2)
    neighs = get_neighbours(agent, fixture_networkx_graph, plcmt)
    assert len(neighs) == 3

    # Remove the RHS central node; this disconnects the two sides of the graph
    plcmt.clear_node(3)
    neighs = get_neighbours(agent, fixture_networkx_graph, plcmt)
    assert len(neighs) == 2

    # Remove one of the two remaining nodes on the RHS
    agent = plcmt.get_agent(4)
    plcmt.clear_node(4)
    assert get_neighbours(agent, fixture_networkx_graph, plcmt) is None

    # The remaining RHS node should be disconnected
    assert get_neighbours(plcmt.get_agent(5), fixture_networkx_graph, plcmt) == []
