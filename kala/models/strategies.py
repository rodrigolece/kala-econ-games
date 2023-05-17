"""Module defining agent strategies."""
from abc import ABC, abstractmethod
from typing import Mapping, Sequence

import numpy as np
from numpy.random import Generator

from utils.stats import truncated_multivariate_normal, truncated_normal


class BaseStrategy(ABC):
    payoff_matrix: Mapping[tuple[str, ...], float | tuple[float, ...]]

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def calculate_payoff(self, *args, **kwargs) -> float | tuple[float, ...]:
        pass


class IndividualInvestingStrategy(BaseStrategy):
    payoff_matrix: Mapping[tuple[str, ...], float]

    def __init__(
        self,
        risk_var: float,
        risk_mean: float = 1.0,
    ):
        if risk_var <= 0:
            raise ValueError("provide a positive variance")

        if risk_mean < 0:
            raise ValueError("provide a non-negative mean")

        # NB: the variance should be a function of the specialization_degree
        self.risk_std = np.sqrt(risk_var)
        self.risk_mean = risk_mean

        self.payoff_matrix = {
            # TODO: model the matrix properly
            ("saver",): 2,
            ("non-saver",): 1,
        }

    # pylint: disable=arguments-differ
    def calculate_payoff(
        self, trait: str, invested_amt: float, rng: Generator | None = None
    ) -> float:
        if trait not in ("saver", "non-saver"):
            raise ValueError

        random_var: float = truncated_normal(loc=self.risk_mean, scale=self.risk_std, rng=rng)
        # size=None so numpy returns single number

        return invested_amt * self.payoff_matrix[(trait,)] * random_var


class PairwiseInvestingStrategy(BaseStrategy):
    payoff_matrix: Mapping[tuple[str, ...], tuple[float, ...]]

    def __init__(self, risk_vars: Sequence[float], risk_means: Sequence[float] = (1.0, 1.0)):
        if len(risk_vars) != 2:
            raise ValueError("provide exactly two values for the variances")

        if len(risk_means) != 2:
            raise ValueError("provide exactly two values for the means")

        self.risk_means = np.asarray(risk_means)
        self.risk_vars = np.asarray(risk_vars)

        self.payoff_matrix = {
            # TODO: model the matrix properly
            ("saver", "saver"): (3, 3),
            ("saver", "non-saver"): (3, 1),
            ("non-saver", "saver"): (1, 3),
            # symmetric defn is needed bcs multivariate doesn't treat as interchangeable
            ("non-saver", "non-saver"): (1, 1),
        }

    # pylint: disable=arguments-differ
    def calculate_payoff(
        self, traits: tuple[str, str], invested_amts: Sequence[float], rng: Generator | None = None
    ) -> tuple[float, float]:
        if len(invested_amts) != 2:
            raise ValueError("provide exactly two values for invested amounts")
        for t in traits:
            if t not in ("saver", "non-saver"):
                raise ValueError

        invested_amts = np.asarray(invested_amts)
        payoffs = np.asarray(self.payoff_matrix[traits])

        random_vars = truncated_multivariate_normal(
            mean=self.risk_means, var=self.risk_vars, rng=rng
        )

        return invested_amts * payoffs * random_vars


if __name__ == "__main__":
    rng = np.random.default_rng(seed=0)

    # Individual game
    # ---------------
    amt = 10
    strategy = IndividualInvestingStrategy(risk_var=2)

    print("Saver")
    for _ in range(3):
        pay = strategy.calculate_payoff(trait="saver", invested_amt=amt, rng=rng)
        print(f"  Invested: {amt:.2f}\tPayoff: {pay:.2f}")

    print("\nNon-saver")
    for _ in range(3):
        pay = strategy.calculate_payoff(trait="non-saver", invested_amt=amt, rng=rng)
        print(f"  Invested: {amt:.2f}\tPayoff: {pay:.2f}")

    amts = 10, 10
    pair_strategy = PairwiseInvestingStrategy(risk_vars=(2, 1))

    # Pairwise game
    # -------------
    print("\n\nSaver / saver")
    for _ in range(3):
        pay1, pay2 = pair_strategy.calculate_payoff(
            traits=("saver", "saver"), invested_amts=amts, rng=rng
        )
        print(f"  Both invested: {amt:.2f}\tPayoff 1: {pay1:.2f}\t\tPayoff 2: {pay2:.2f}")

    print("\nSaver / non-saver")
    for _ in range(3):
        pay1, pay2 = pair_strategy.calculate_payoff(
            traits=("saver", "non-saver"), invested_amts=amts, rng=rng
        )
        print(f"  Both invested: {amt:.2f}\tPayoff 1: {pay1:.2f}\t\tPayoff 2: {pay2:.2f}")
