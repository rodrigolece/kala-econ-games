"""Test the strategies module."""

import pytest

from kala.models.agents import SaverAgent
from kala.models.strategies import MatchingStrategy, SaverCooperationPayoffStrategy


@pytest.fixture
def agent_pair(fixture_saver_agents):
    """Return a pair of agents."""
    # Assuming the first is a saver and the fourth is a non-saver
    return fixture_saver_agents[0], fixture_saver_agents[3]


def test_init_saver_cooperation_payoff_strategy(agent_pair):
    """Test the initialization of a saver cooperation payoff strategy."""
    saver, non_saver = agent_pair

    strategy = SaverCooperationPayoffStrategy(dist_sigma_func=lambda x: 1e-6)
    pay_ss, pay_sn = 1.15, 0.9
    assert strategy.stochastic  # stochastic=True by default

    assert strategy.calculate_payoff([saver, saver]) == pytest.approx([pay_ss, pay_ss], rel=1e-2)
    assert strategy.calculate_payoff([saver, non_saver]) == pytest.approx([pay_sn, 1.0], rel=1e-2)
    assert strategy.calculate_payoff([non_saver, saver]) == pytest.approx([1.0, pay_sn], rel=1e-2)
    assert strategy.calculate_payoff([non_saver, non_saver]) == pytest.approx([1.0, 1.0])


def test_matching_strategy(fixture_agent_placement, fixture_networkx_graph):
    """Test the matching strategy."""
    strategy = MatchingStrategy()
    matches = strategy.select_matches(fixture_agent_placement, fixture_networkx_graph)

    assert len(matches) == fixture_networkx_graph.number_of_nodes() // 2
    for match in matches:
        assert len(match) == 2
        assert isinstance(match[0], SaverAgent)
        assert isinstance(match[1], SaverAgent)
