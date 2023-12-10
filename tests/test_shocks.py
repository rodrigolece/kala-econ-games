"""Test the shocks module."""

from kala.models.shocks import (
    AddEdge,
    AddRandomEdge,
    ChangeAllPlayersMemoryLength,
    ChangeDifferentialEfficient,
    ChangeDifferentialInefficient,
    ChangePlayerMemoryLength,
    ChangeRandomPlayerMemoryLength,
    FlipAllSavers,
    FlipRandomSaver,
    FlipSaver,
    FlipSavers,
    HomogenizeSaversTo,
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


def test_flip_random_saver(init_deterministic_game):
    """Test the FlipRandomSaver shock."""

    game = init_deterministic_game
    initial_number_of_savers = game.get_num_savers()

    FlipRandomSaver(rng=0).apply(game)

    assert game.get_num_savers() != initial_number_of_savers


def test_flip_saver(init_deterministic_game):
    """Test the FlipSaver shock."""

    game = init_deterministic_game

    initial_number_of_savers = game.get_num_savers()
    FlipSaver("a").apply(game)
    number_of_savers = game.get_num_savers()

    assert number_of_savers != initial_number_of_savers


def test_flip_all_savers(init_deterministic_game):
    """Test the FlipAllSavers shock."""

    game = init_deterministic_game

    players = game.get_num_players()
    initial_number_of_savers = game.get_num_savers()
    initial_number_of_non_savers = players - initial_number_of_savers

    FlipAllSavers().apply(game)

    new_number_of_savers = game.get_num_savers()
    new_number_number_of_non_savers = players - new_number_of_savers

    assert new_number_of_savers == initial_number_of_non_savers
    assert new_number_number_of_non_savers == initial_number_of_savers


def test_flip_savers(init_deterministic_game):
    """Test the FlipSavers shock."""

    game = init_deterministic_game
    list_players = ["a", "f"]

    is_saver_a = game.graph.get_node("a").is_saver
    is_saver_f = game.graph.get_node("f").is_saver

    FlipSavers(list_players).apply(game)

    assert game.graph.get_node("a").is_saver is not is_saver_a
    assert game.graph.get_node("f").is_saver is not is_saver_f


def test_homogenize_savers_to(init_deterministic_game):
    """Test the HomogenizeSaversTo shock."""

    game = init_deterministic_game

    HomogenizeSaversTo(True).apply(game)
    assert game.get_num_savers() == game.get_num_players()

    HomogenizeSaversTo(False).apply(game)
    assert game.get_num_savers() == 0


def test_change_player_memory_length(init_deterministic_game):
    """Test the ChangePlayerMemoryLength shock."""

    game = init_deterministic_game

    ChangePlayerMemoryLength("a", 100).apply(game)

    node = game.graph.get_node("a")
    new_memory_length = node.get_trait("updates_from_n_last_games")

    assert new_memory_length == 100


def test_change_random_player_memory_length(init_deterministic_game):
    """Test the ChangeRandomPlyaerMemoryLength shock."""
    game = init_deterministic_game

    ChangeRandomPlayerMemoryLength(1000).apply(game)

    filt = game.create_filter_from_trait("updates_from_n_last_games", 1000)

    assert sum(filt) == 1


def test_change_all_players_memory_length_int(init_deterministic_game):
    """Test the ChangeAllPlayersMemoryLength shock."""
    game = init_deterministic_game

    ChangeAllPlayersMemoryLength(100).apply(game)

    filt = game.create_filter_from_trait("updates_from_n_last_games", 100)
    assert sum(filt) == game.get_num_players()


def test_change_all_players_memory_length_sequence(init_deterministic_game):
    """Test the ChangeAllPlayersMemoryLength shock."""
    game = init_deterministic_game

    memory_dist = [1, 2, 3, 4, 5, 6]
    ChangeAllPlayersMemoryLength(memory_dist).apply(game)

    memories = [node.get_trait("updates_from_n_last_games") for node in game.graph.get_nodes()]
    memories.sort()
    assert memories == memory_dist


def test_change_differential_efficient(init_deterministic_game):
    """Test the ChangeDifferentialEfficient shock."""
    game = init_deterministic_game

    ChangeDifferentialEfficient(0).apply(game)

    assert game.strategy.payoff_matrix[("saver", "saver")] == (1.0, 1.0)


def test_change_differential_inefficient(init_deterministic_game):
    """Test the ChangeDifferentialInefficient shock."""
    game = init_deterministic_game

    ChangeDifferentialInefficient(0.5).apply(game)

    assert game.strategy.payoff_matrix[("saver", "non-saver")] == (0.5, 1.0)
    assert game.strategy.payoff_matrix[("non-saver", "saver")] == (1.0, 0.5)
