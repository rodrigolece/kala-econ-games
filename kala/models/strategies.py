"""Module defining agent strategies."""
from abc import ABC, abstractmethod
from typing import Mapping, TypeVar

import numpy as np
from numpy.random import Generator

from kala.utils.stats import lognormal


class BaseStrategy(ABC):
    """
    Base strategy meant to be subclassed.

    Attributes
    ----------
    stochastic : bool
        Whether the strategy is stochastic.
    payoff_matrix : Mapping[tuple[str, ...], tuple[float, ...]]
        A mapping from the strategy of each agent to the payoff tuple.

    Methods
    -------
    calculate_payoff()
        Calculate the payoff for a strategy.

    """

    stochastic: bool
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
    """
    A strategy that models cooperation between agents.

    Two agents that are savers will have a higher payoff (on expectation) than in all other cases,
    but a saver that encounters a non-saver will see a worse outcome than the non-saver.

    """

    # pylint: disable=unused-argument
    def __init__(
        self,
        *args,
        stochastic: bool = False,
        differential_inefficient: float = 0.1,
        differential_efficient: float = 0.15,
        min_specialization: float = 0.0,
        dist_mean: float = 1.0,
        dist_sigma: float = 1.0,
        rng: Generator | None = None,
        **kwargs,
    ):
        """
        Initialize a cooperation strategy.

        Parameters
        ----------
        stochastic : bool, optional
            Whether to use a stochastic payoff matrix, by default False.
        differential_inefficient : float, optional
            The amount by which a saver is less efficient when encountering non-savers,
            by default 0.1.
        differential_efficient : float, optional
            The amount by which a saver is more efficient when encountering another saver,
            by default 0.15.
        min_specialization : float, optional
            The minimum specialization of savers. NB: our implementation of the more
            general model assumes the special case of the minimum specialization
            being equal for all agents.
        dist_mean : float, optional
            The mean of the lognormal distribution used to generate stochastic payoffs,
            by default 1.0.
        dist_sigma : float, optional
            The sigma of the lognormal distribution used to generate stochastic payoffs,
            by default 1.0.
        rng : Generator, optional
            A numpy random number generator, by default None.

        Raises
        ------
        ValueError
            If any of the parameters are invalid.

        """
        # Checks
        if not 0 < differential_inefficient < 1:
            raise ValueError("expected number between (0, 1) for 'differential_inefficient'")

        if differential_efficient <= 0:
            raise ValueError("expected number greater than 0 for 'differential_efficient'")

        if not 0 <= min_specialization < 1:
            raise ValueError("expected number between [0, 1) for 'min_specialization'")

        # Initialize
        self.stochastic = stochastic

        payoff_ss = 1 + differential_efficient - min_specialization
        payoff_sn = 1 - differential_inefficient - min_specialization

        self.payoff_matrix = {
            ("saver", "saver"): (payoff_ss, payoff_ss),
            ("saver", "non-saver"): (payoff_sn, 1),
            ("non-saver", "saver"): (1, payoff_sn),
            ("non-saver", "non-saver"): (1, 1),
        }

        self._saver_encoding = {True: "saver", False: "non-saver"}
        # used to map the trait is_saver to the payoff matrix entries

        self._rng = rng
        self._mean = dist_mean
        self._sigma = dist_sigma
        # TODO: more elegant solution would be to accept initialized distribution that
        # doesn't need parameters and is ready to return random numbers

    # pylint: disable=arguments-differ
    def calculate_payoff(
        self,
        *agents,
        **kwargs,
    ) -> tuple[float, ...]:
        if len(agents) != 2:
            raise ValueError("expected exactly two agents")

        saver_traits = tuple(self._saver_encoding[ag.is_saver()] for ag in agents)
        payoffs = np.asarray(self.payoff_matrix[saver_traits])

        if self.stochastic:
            draw = lognormal(mean=self._mean, sigma=self._sigma, rng=self._rng)
            payoffs *= [draw if ag.is_saver() else 1 for ag in agents]

        return tuple(payoffs)


if __name__ == "__main__":
    from kala.models.agents import InvestorAgent

    saver = InvestorAgent(is_saver=True)
    non_saver = InvestorAgent(is_saver=False)

    strategy = CooperationStrategy(stochastic=True, rng=0)
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
