"""Test the game module."""

import logging

import pytest

from kala.models.game import DiscreteTwoByTwoGame
from kala.models.strategies import CooperationStrategy


@pytest.fixture(scope="function")  # needs to match scope of init_simple_graph
def init_game(init_simple_graph):
    """Initialize a game."""
    coop = CooperationStrategy(
        stochastic=True, differential_efficient=0.5, differential_inefficient=0.05, rng=0
    )

    return DiscreteTwoByTwoGame(init_simple_graph, coop)


def test_filter_functions(init_game):
    """Test filter functions."""
    game = init_game
    assert game.get_num_savers() == 3
    assert game.create_filter_from_trait("group", 0) == [True] * 3 + [False] * 3


def test_init(init_game):
    """NB: this is currently not a real test but it's here to make sure the functions run."""
    game = init_game
    wealth, num_savers = game.get_total_wealth(), game.get_num_savers()
    logging.info(f"Init: wealth={wealth:.2f}, {num_savers=}")

    for _ in range(10):
        game.play_round()
        wealth, num_savers = game.get_total_wealth(), game.get_num_savers()
        logging.info(f"wealth={wealth:.2f}, {num_savers=}")
