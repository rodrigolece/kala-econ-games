"""Test the shocks module."""

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


def test_remove_player(init_deterministic_game):
    """Test the RemovePlayer shock."""
    game = init_deterministic_game

    RemovePlayer("a").apply(game)

    assert game.graph.num_nodes() == 5
    assert game.graph.num_edges() == 5

    RemovePlayer("c").apply(game)

    assert game.graph.num_nodes() == 4
    assert game.graph.num_edges() == 3


def test_remove_random_player(init_deterministic_game):
    """Test the RemoveRandomPlayer shock."""
    game = init_deterministic_game

    RemoveRandomPlayer(rng=0).apply(game)

    assert game.graph.num_nodes() == 5


def test_remove_edge(init_deterministic_game):
    """Test the RemoveEdge shock."""
    game = init_deterministic_game

    RemoveEdge("c", "d").apply(game)

    assert game.graph.num_nodes() == 6
    assert game.graph.num_edges() == 6


def test_remove_random_edge(init_deterministic_game):
    """Test the RemoveRandomEdge shock."""
    game = init_deterministic_game

    RemoveRandomEdge(rng=0).apply(game)

    assert game.graph.num_edges() == 6


def test_swap_edge(init_deterministic_game):
    """Test the SwapEdge shock."""
    game = init_deterministic_game

    SwapEdge("c", "d", "e").apply(game)

    assert game.graph.num_nodes() == 6
    assert game.graph.num_edges() == 7


def test_swap_random_edge(init_deterministic_game):
    """Test the SwapRandomEdge shock."""
    game = init_deterministic_game

    SwapRandomEdge(rng=0).apply(game)

    assert game.graph.num_nodes() == 6
    assert game.graph.num_edges() == 7


def test_add_edge(init_deterministic_game):
    """Test the AddEdge shock."""
    game = init_deterministic_game

    AddEdge("a", "f").apply(game)

    assert game.graph.num_nodes() == 6
    assert game.graph.num_edges() == 8
    assert game.graph.get_node("f") in game.graph.get_neighbours("a")


def test_add_random_edge(init_deterministic_game):
    """Test the AddRandomEdge shock."""

    game = init_deterministic_game

    AddRandomEdge().apply(game)

    assert game.graph.num_nodes() == 6
    assert game.graph.num_edges() == 8
