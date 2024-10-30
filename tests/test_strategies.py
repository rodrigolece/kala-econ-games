"""Test the strategies module."""

import pytest

from kala.models.agents import InvestorAgent
from kala.models.strategies import CooperationStrategy


@pytest.fixture
def agent_pair():
    """Return a pair of agents."""
    return InvestorAgent(is_saver=True), InvestorAgent(is_saver=False)


def test_init_cooperation_strategy(agent_pair):
    """Test the initialization of a cooperation strategy."""
    saver, non_saver = agent_pair

    strategy = CooperationStrategy(stochastic=False, rng=0, dist_sigma_func=lambda x: 1e-6)
    efficient, inefficient = 1.15, 0.9
    assert not strategy.stochastic

    assert strategy.calculate_payoff(saver, saver) == pytest.approx([efficient, efficient])
    assert strategy.calculate_payoff(saver, non_saver) == pytest.approx([inefficient, 1.0])
    assert strategy.calculate_payoff(non_saver, saver) == pytest.approx([1.0, inefficient])
    assert strategy.calculate_payoff(non_saver, non_saver) == pytest.approx([1.0, 1.0])
