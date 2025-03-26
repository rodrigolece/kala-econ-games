"""Test the game module."""

import pytest

from kala.models.game import GamePlan, GameState, play_game
from kala.models.shocks import RemoveRandomPlayer, SwapRandomEdge


@pytest.fixture(scope="module")
def fixture_game_plan():
    shocks = {
        4: [SwapRandomEdge()],
        6: [RemoveRandomPlayer()],
    }
    return GamePlan(steps=10, shocks=shocks)


def test_game_plan(fixture_game_plan):
    """Test that GamePlan works correctly."""

    plan = fixture_game_plan
    assert plan.steps == 10
    assert len(plan.shocks) == 2
    assert 4 in plan.shocks
    assert 6 in plan.shocks


def test_play_game(fixture_game_state, fixture_game_plan):
    """Test that a game can be played through multiple steps."""
    initial_num_agents = len(fixture_game_state.agents)
    initial_num_edges = fixture_game_state.graph.number_of_edges()

    # Play through the game and check state at each step
    for time, state in play_game(fixture_game_state, fixture_game_plan):
        # Before player shock
        if time < 6:
            assert len(state.agents) == initial_num_agents
        # After player shock
        elif time >= 6:
            assert len(state.agents) == initial_num_agents - 1

        # Before edge shock shouldn't change number of edges
        assert state.graph.number_of_edges() == initial_num_edges

        # Basic invariants that should always hold
        assert isinstance(state, GameState)
        assert state.graph.number_of_nodes() > 0
