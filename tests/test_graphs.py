"""Test the graphs module."""


from kala.models.agents import InvestorAgent


def test_get_functions_by_agents(init_simple_graph):
    """Test the methods get_node and get_neighbours and the return type of the node"""
    G = init_simple_graph  # pylint: disable=invalid-name

    # get_node using the identifier
    n0 = G.get_node("a")  # type: ignore
    assert isinstance(n0, InvestorAgent)

    neighs = G.get_neighbours(n0)
    assert len(neighs) == 2
    assert all(isinstance(n, InvestorAgent) for n in neighs)

    assert len(G.get_neighbors(G.get_node("c"))) == 3


def test_get_functions_by_string(init_simple_graph):
    G = init_simple_graph  # pylint: disable=invalid-name

    neighs = G.get_neighbours("a")
    assert len(neighs) == 2
    assert all(isinstance(n, InvestorAgent) for n in neighs)

    assert len(G.get_neighbors("c")) == 3


def test_get_functions_by_pos(init_simple_graph):
    G = init_simple_graph  # pylint: disable=invalid-name

    n0 = G.get_node(0)  # type: ignore
    assert isinstance(n0, InvestorAgent)
    assert n0.uuid == "a"

    neighs = G.get_neighbours(0)
    assert len(neighs) == 2
    assert all(isinstance(n, InvestorAgent) for n in neighs)

    assert len(G.get_neighbors(2)) == 3
