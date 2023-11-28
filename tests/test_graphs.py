"""Test the graphs module."""


from kala.models.agents import InvestorAgent


def test_get_node_and_get_neighbours(init_simple_graph):
    """Test the methods get_node and get_neighbours and the return type of the node"""
    G = init_simple_graph  # pylint: disable=invalid-name

    n0 = G.get_node(0, by_pos=True)  # type: ignore
    assert isinstance(n0, InvestorAgent)
    assert n0.uuid == "a"

    # get_node using the identifier
    assert G.get_node("a") == n0

    neighs = G.get_neighbours(n0)
    assert len(neighs) == 2
    assert all(isinstance(n, InvestorAgent) for n in neighs)

    n2 = G.get_node("c")  # type: ignore
    assert len(G.get_neighbors(n2)) == 3
