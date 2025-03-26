"""Test the shocks module."""

from kala.models.graphs import get_neighbours
from kala.models.shocks import (
    AddEdge,
    AddRandomEdge,
    RemoveEdge,
    RemovePlayer,
    RemoveRandomEdge,
    RemoveRandomPlayer,
    SwapEdge,
    SwapRandomEdge,
)


def test_remove_player(fixture_game_state):
    """Test the RemovePlayer shock."""
    game = fixture_game_state
    agents = game.agents

    # Remove the LHS central node; this disconnects the two sides of the graph
    RemovePlayer(agents[2]).apply(game)
    assert game.graph.number_of_nodes() == 6
    assert len(game.agents) == 5

    # after removing agent, the agents coming after are shifted down
    # we test that the RHS is still connected
    neighs = get_neighbours(agents[2], game.graph, game.placements)  # NB: [3] is now [2]
    for n in neighs:
        print(f"neigh: {str(n.uuid)[:8]}")
    assert len(neighs) == 2

    # Remove one of the two remaining nodes on the LHS
    a = agents[0]
    RemovePlayer(a).apply(game)

    assert game.graph.number_of_nodes() == 6
    assert len(game.agents) == 4
    assert get_neighbours(a, game.graph, game.placements) is None

    # The last LHS node shoudl be disconnected
    assert get_neighbours(agents[0], game.graph, game.placements) == []


def test_remove_random_player(fixture_game_state):
    """Test the RemoveRandomPlayer shock."""
    game = fixture_game_state

    RemoveRandomPlayer().apply(game)

    assert game.graph.number_of_nodes() == 6
    assert len(game.agents) == 5


def test_add_edge(fixture_game_state):
    """Test the AddEdge shock."""
    game = fixture_game_state
    agents = game.agents

    a = agents[0]
    AddEdge(a, agents[-1]).apply(game)

    assert game.graph.number_of_nodes() == 6
    assert game.graph.number_of_edges() == 8

    assert agents[-1] in get_neighbours(a, game.graph, game.placements)


def test_add_random_edge(fixture_game_state):
    """Test the AddRandomEdge shock."""

    game = fixture_game_state

    AddRandomEdge().apply(game)

    assert game.graph.number_of_nodes() == 6
    assert game.graph.number_of_edges() == 8


def test_remove_edge(fixture_game_state):
    """Test the RemoveEdge shock."""
    game = fixture_game_state
    agents = game.agents

    RemoveEdge(agents[2], agents[3]).apply(game)

    assert game.graph.number_of_nodes() == 6
    assert game.graph.number_of_edges() == 6
    assert agents[3] not in get_neighbours(agents[2], game.graph, game.placements)


def test_remove_random_edge(fixture_game_state):
    """Test the RemoveRandomEdge shock."""
    game = fixture_game_state

    RemoveRandomEdge().apply(game)

    assert game.graph.number_of_nodes() == 6
    assert game.graph.number_of_edges() == 6


def test_swap_edge(fixture_game_state):
    """Test the SwapEdge shock."""
    game = fixture_game_state
    agents = game.agents

    SwapEdge(agents[2], agents[3], agents[4]).apply(game)

    assert game.graph.number_of_nodes() == 6
    assert game.graph.number_of_edges() == 7
    assert agents[4] in get_neighbours(agents[2], game.graph, game.placements)


def test_swap_random_edge(fixture_game_state):
    """Test the SwapRandomEdge shock."""
    game = fixture_game_state

    SwapRandomEdge().apply(game)

    assert game.graph.number_of_nodes() == 6
    assert game.graph.number_of_edges() == 7
