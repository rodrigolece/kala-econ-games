"""Test the graphs module."""

import networkx as nx

from kala.models.agents import InvestorAgent


def test_get_functions_by_agents(init_simple_graph):
    """Test the methods get_node and get_neighbours and the return type of the node."""
    G = init_simple_graph  # pylint: disable=invalid-name

    # get_node using the identifier
    n0 = G.get_node("a")  # type: ignore
    assert isinstance(n0, InvestorAgent)

    neighs = G.get_neighbours(n0)
    assert len(neighs) == 2
    assert all(isinstance(n, InvestorAgent) for n in neighs)

    assert len(G.get_neighbors(G.get_node("c"))) == 3


def test_get_functions_by_string(init_simple_graph):
    """Test the methods get_node and get_neighbours using a string identifier."""
    G = init_simple_graph  # pylint: disable=invalid-name

    neighs = G.get_neighbours("a")
    assert len(neighs) == 2
    assert all(isinstance(n, InvestorAgent) for n in neighs)

    assert len(G.get_neighbors("c")) == 3


def test_get_functions_by_pos(init_simple_graph):
    """Test the methods get_node and get_neighbours using an integer (position)."""
    G = init_simple_graph  # pylint: disable=invalid-name

    n0 = G.get_node(0)  # type: ignore
    assert isinstance(n0, InvestorAgent)
    assert n0.uuid == "a"

    neighs = G.get_neighbours(0)
    assert len(neighs) == 2
    assert all(isinstance(n, InvestorAgent) for n in neighs)

    assert len(G.get_neighbors(2)) == 3


def test_add_node(init_simple_graph):
    """Test the method add_node."""
    G = init_simple_graph  # pylint: disable=invalid-name

    # NB: we are not adding the nodes in order
    agent = InvestorAgent(is_saver=False, uuid="g")
    assert G.add_node(agent)
    assert G.num_nodes() == 7

    assert G.get_node(agent).uuid == "g"
    assert G.get_node("g") == agent
    assert G.get_node(6) == agent

    assert G.add_node(agent) is False  # the second time it should fail


def test_remove_node(init_simple_graph):
    """Test the method remove_node."""
    G = init_simple_graph  # pylint: disable=invalid-name

    # NB: we are not removing the nodes in order
    assert G.remove_node("e")
    assert G.num_nodes() == 5

    assert G.remove_node("f")
    assert G.num_nodes() == 4

    assert G.remove_node("f") is False


def test_add_edge(init_simple_graph):
    """Test the method add_edge."""
    G = init_simple_graph  # pylint: disable=invalid-name

    assert G.add_edge("a", "b") is False  # the edge already exists
    assert G.add_edge("a", "a") is False  # self-loops are not allowed
    assert G.add_edge("a", "g") is False  # the node does not exist

    assert G.add_edge("a", "d")
    assert nx.number_of_edges(G._graph) == 8  # pylint: disable=protected-access


def test_remove_edge(init_simple_graph):
    """Test the method remove_edge."""
    G = init_simple_graph  # pylint: disable=invalid-name

    assert G.remove_edge("c", "d")
    assert nx.number_of_edges(G._graph) == 6  # pylint: disable=protected-access
    assert nx.is_connected(G._graph) is False  # pylint: disable=protected-access
