"""Module defining agent strategies."""

from abc import ABC, abstractmethod
from typing import Callable, Mapping, TypeVar

import numpy as np
from numpy.random import Generator

from kala.utils.stats import get_random_state, lognormal


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

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(stochastic={self.stochastic})"

    def __repr__(self) -> str:
        return f"<{str(self)}>"

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

    _sigma: Mapping[tuple[str, ...], float]

    # pylint: disable=unused-argument
    def __init__(
        self,
        *args,
        stochastic: bool = False,
        differential_inefficient: float = 0.1,
        differential_efficient: float = 0.15,
        dist_mean: float = 0.0,
        dist_sigma_func: Callable = lambda x: x,
        rng: Generator | int | None = None,
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
        dist_mean : float, optional
            The mean of the lognormal distribution used to generate stochastic payoffs,
            by default 1.0.
        dist_sigma_func : Callable, optional
            A function that maps specializations (efficient and inefficient) to the
            standard deviation of the lognormal distribution. By default, the function
            is the identity function.
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

        # Initialize
        self.stochastic = stochastic

        payoff_ss = 1 + differential_efficient
        payoff_sn = 1 - differential_inefficient

        self.payoff_matrix = {
            ("saver", "saver"): (payoff_ss, payoff_ss),
            ("saver", "non-saver"): (payoff_sn, 1),
            ("non-saver", "saver"): (1, payoff_sn),
            ("non-saver", "non-saver"): (1, 1),
        }

        self._saver_encoding = {True: "saver", False: "non-saver"}
        # used to map the trait is_saver to the payoff matrix entries

        self._rng = get_random_state(rng)
        self._mean = dist_mean
        self._sigma = {
            ("saver", "saver"): dist_sigma_func(payoff_ss),
            ("saver", "non-saver"): dist_sigma_func(payoff_sn),
            ("non-saver", "saver"): dist_sigma_func(payoff_sn),
            ("non-saver", "non-saver"): 1,
        }
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
            sigma = self._sigma[saver_traits]
            draw = lognormal(mean=self._mean, sigma=sigma, rng=self._rng)
            payoffs *= [draw if ag.is_saver() else 1 for ag in agents]

        return tuple(payoffs)
