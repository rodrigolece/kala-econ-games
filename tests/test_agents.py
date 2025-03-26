"""Test the agents module."""

from uuid import UUID

import numpy as np
import pytest

from kala import SaverFlipAfterFractionLost, init_saver_agent


NUM_GAMES = 5


@pytest.fixture
def saver_agent():
    """Simple investor agent."""
    return init_saver_agent(is_saver=True, memory_length=NUM_GAMES, update_rule=None)


def test_init_of_saver_agent(saver_agent):
    """Test the init of an SaverAgent."""
    agent = saver_agent
    assert agent.properties.is_saver
    assert hasattr(agent, "uuid")
    assert isinstance(agent.uuid, UUID)

    agent.update(payoff=2, lost_match=False, time=0)
    assert agent.score == 2
    agent.update(payoff=0.5, lost_match=True, time=1)
    assert agent.score == 2.5


@pytest.fixture
def saver_agent_with_update_rule():
    """Investor agent with memory."""
    rule = SaverFlipAfterFractionLost(frac=0.5)
    return init_saver_agent(is_saver=True, memory_length=NUM_GAMES, update_rule=rule)


def test_update_rule(saver_agent_with_update_rule):
    """Test the update rule of a SaverAgent."""
    agent = saver_agent_with_update_rule
    a = np.array([True] * (NUM_GAMES - 1) + [False])
    expected_states = np.hstack((a, ~a))

    # all matches will be lost and the agent will play twice as many games as its memory_length
    for i in range(2 * NUM_GAMES):
        agent.update(payoff=1.0, lost_match=True, time=i)
        assert agent.properties.is_saver == expected_states[i]
