"""Module defining agent strategies."""
from abc import ABC, abstractmethod
from typing import Mapping, TypeVar

import numpy as np

from scipy.optimize import minimize

# from numpy.random import Generator

from kala.utils.stats import get_payoffs


class BaseStrategy(ABC):
    payoff_matrix: Mapping[tuple[str, ...], tuple[float, ...]]

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def calculate_payoff(self, *args, **kwargs) -> tuple[float, ...]:
        """A realization of the payoff for a strategy."""


StrategyT = TypeVar("StrategyT", bound=BaseStrategy)
"""Used to refer to BaseStrategy as well as its subclasses."""


class CooperationStrategy(BaseStrategy):
    saver_encoding: Mapping[bool, str]

    def __init__(
        self,
        *args,
        differential_inefficient=0.1,
        differential_efficient=0.15,
        **kwargs,
    ):
        if not 0 < differential_efficient < 1 or not 0 < differential_inefficient < 1:
            raise ValueError("expected number between (0, 1) for 'eta_differential'")

        payoff_ss = 1 + differential_efficient
        payoff_sn = 1 - differential_inefficient

        self.payoff_matrix = {
            ("saver", "saver"): (payoff_ss, payoff_ss),
            ("saver", "non-saver"): (payoff_sn, 1),
            ("non-saver", "saver"): (1, payoff_sn),
            ("non-saver", "non-saver"): (1, 1),
        }

        self.saver_encoding = {True: "saver", False: "non-saver"}

    # FIXME: for the time being I am  making the simulation deterministic
    # pylint: disable=arguments-differ
    def calculate_payoff(
        self,
        *agents,
        stochastic=False,
        **kwargs,
    ) -> tuple[float, ...]:
        if len(agents) != 2:
            raise ValueError("expected exactly two agents")

        if stochastic:
            random_variable = np.random.lognormal(mean=1.0, sigma=1.0)
        else:
            random_variable = 1

        saver_traits = tuple(self.saver_encoding[ag.is_saver()] for ag in agents)
        random_vars = [random_variable if ag.is_saver() else 1 for ag in agents]
        payoffs = np.array(self.payoff_matrix[saver_traits]) * random_vars

        return payoffs


if __name__ == "__main__":
    from kala.models.agents import InvestorAgent

    rng = np.random.default_rng(seed=0)

    saver = InvestorAgent(is_saver=True)
    non_saver = InvestorAgent(is_saver=False)

    strategy = CooperationStrategy()
    print(strategy.calculate_payoff(saver, saver))
    print(strategy.calculate_payoff(saver, non_saver))
    print(strategy.calculate_payoff(non_saver, saver))
    print(strategy.calculate_payoff(non_saver, non_saver))

    # Below will be useful when we add stochastic variations back in
    # print("\n\nSaver / saver")
    # for _ in range(3):
    #     pay1, pay2 = strategy.calculate_payoff(saver, saver)

    # print("\nSaver / non-saver")
    # for _ in range(3):
    #     pay1, pay2 = pair_strategy.calculate_payoff(saver, non_saver)
