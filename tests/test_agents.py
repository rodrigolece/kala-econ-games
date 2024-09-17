"""Test the agents module."""

import numpy as np
import pytest

from kala.models.agents import InvestorAgent
from kala.models.memory_rules import AverageMemoryRule


NUM_GAMES = 5


@pytest.fixture
def simple_investor_agent():
    """ "Simple investor agent."""
    return InvestorAgent(is_saver=True)


def test_init_of_simple_agent(simple_investor_agent):
    """Test the init of an InvestorAgent."""
    agent = simple_investor_agent
    assert agent.is_saver()
    assert hasattr(agent, "uuid")
    assert isinstance(agent.uuid, str)

    agent.update(payoff=2)
    assert agent.get_savings() == 2
    agent.update(payoff=0.5)
    assert agent.get_savings() == 2.5


@pytest.fixture
def memoried_investor_agent():
    """Investor agent with memory."""
    update_rule = AverageMemoryRule(memory_length=NUM_GAMES)
    return InvestorAgent(is_saver=False, update_rule=update_rule)


def test_init_of_memoried_agent(memoried_investor_agent):
    """Test the memory init of an InvestorAgent."""
    agent = memoried_investor_agent
    a = np.array([False] * (NUM_GAMES - 1) + [True])
    expected_states = np.hstack((a, ~a))

    for i in range(2 * NUM_GAMES):
        agent.update(payoff=1.0, successful_round=False)
        assert agent.is_saver() == expected_states[i]
