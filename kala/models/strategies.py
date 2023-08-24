"""Module defining agent strategies."""
from abc import ABC, abstractmethod
from typing import Mapping, TypeVar

import numpy as np

# from numpy.random import Generator

# from kala.utils.stats import multivariate_normal, normal


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

    def __init__(self, *args, eta_differential: float = 0.1, **kwargs):
        if not 0 < eta_differential < 1:
            raise ValueError("expected number between (0, 1) for 'eta_differential'")

        payoff_ss = 1 + eta_differential
        payoff_sn = 1 - eta_differential

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
        # risk_vars: Sequence[float],
        # rng: Generator | None = None,
        **kwargs,
    ) -> tuple[float, ...]:
        if len(agents) != 2:
            raise ValueError("expected exactly two agents")

        # if len(risk_vars) != 2:
        #     raise ValueError("provide exactly two values for the variances")

        saver_traits = tuple(self.saver_encoding[ag.is_saver()] for ag in agents)
        payoffs = self.payoff_matrix[saver_traits]  # np.asarray

        # random_vars = multivariate_normal(mean=(1.0, 1.0), var=risk_vars, rng=rng)
        # np.maximum(payoffs * random_vars, 0)

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
