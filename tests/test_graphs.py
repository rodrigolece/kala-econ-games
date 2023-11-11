"""Test the graphs module."""


from kala.models.agents import InvestorAgent


def test_get_node_and_get_neighbours(init_simple_graph, init_agents):
    """Test the methods get_node and get_neighbours and the return type of the node"""
    G = init_simple_graph  # pylint: disable=invalid-name
    n0 = G.get_node(init_agents[0].uuid)  # type: ignore
    assert isinstance(n0, InvestorAgent)

    neighs = G.get_neighbours(n0)
    assert isinstance(neighs[0], InvestorAgent)

    # for n in agents:
    #     neighs = list(G.get_neighbours(n))
    #     print(f"{n.uuid}: {len(neighs)}")
