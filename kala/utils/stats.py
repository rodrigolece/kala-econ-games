from typing import Any, Iterable, Sequence

import numpy as np
from numpy.random import Generator
from scipy.optimize import minimize

# from scipy.special import erf  # pylint: disable=no-name-in-module


def _default_rng(rng: Generator | None = None):
    """If rng is already a Generator, pass-through; otherwise return default."""

    if rng is None:
        rng = np.random.default_rng()
    elif isinstance(rng, int):
        rng = np.random.default_rng(rng)

    return rng


def choice(
    lst: Iterable[Any],
    size: int | None = None,
    replace: bool = False,
    rng: Generator | None = None,
):
    rng = _default_rng(rng)
    rng.choice(lst, size=size, replace=replace)

    return rng.choice(lst, size=size, replace=replace)


def normal(
    mean: float,
    sigma: float,
    size: int | None = None,
    rng: Generator | None = None,
) -> float | np.ndarray:
    """
    Thin wrapper around NumPy's normal distribution.

    """
    rng = _default_rng(rng)

    return rng.normal(loc=mean, scale=sigma, size=size)


def normal_truncated(
    *args,
    threshold: int = 0,
    **kwargs,
) -> float | np.ndarray:
    """
    Draw normal random variables and compare them against a lower bound.

    TODO: In the future we might want to add a/ an equivalent upper bound and b/ a
    normalisation constant.
    """
    vals = normal(*args, **kwargs)

    return np.maximum(vals, threshold)


def multivariate_normal(
    mean: Sequence[float],
    var: Sequence[float] | None = None,
    cov: np.ndarray | None = None,
    size: int | None = None,
    rng: Generator | None = None,
):
    """
    Thin wrapper around NumPy's multivariate normal distribution.

    NB: Exactly one of vars or cov must be non-null.

    """
    rng = _default_rng(rng)
    mean = np.asarray(mean)

    if var is not None:
        assert len(var) == len(mean)
        cov = np.diag(var)

    elif cov is not None:
        cov = np.asarray(cov)

    return rng.multivariate_normal(mean, cov, size=size)


def multivariate_normal_truncated(
    *args,
    threshold: int = 0,
    **kwargs,
):
    """
    Draw multivariate normal random variables and compare them against a lower bound.

    NB: Exactly one of vars or cov must be non-null.
    """

    vals = multivariate_normal(*args, **kwargs)

    return np.maximum(vals, threshold)


def lognormal(
    mean: float,
    sigma: float,
    size: int | None = None,
    rng: Generator | None = None,
) -> float | np.ndarray:
    """
    Thin wrapper around NumPy's log-normal distribution.

    """
    rng = _default_rng(rng)

    return rng.lognormal(mean, sigma, size)


def condition_efficient_specialization(
    strategy, efficient_specialization, min_specialization_i, min_specialization_j
):
    """Function to model the condition for the efficient specialization."""
    value = -1 * (
        efficient_specialization
        + (1 - strategy) * min_specialization_i
        + strategy * min_specialization_j
    )
    return value


def get_strategy(efficient_specialization, min_specialization_i, min_specialization_j):
    """Function to obtain a strategy given two minimum specializations of two agents"""
    results_strategy = minimize(
        condition_efficient_specialization,
        x0=0.5,
        args=(efficient_specialization, min_specialization_i, min_specialization_j),
        bounds=(0, 1),
    )

    if not results_strategy.success:
        raise Exception(results_strategy.message)

    return results_strategy.x


def get_payoffs(*agents, differential_inefficient, differential_efficient):
    """Function to compute the payoffs given two differentials with respect to 1."""
    if len(agents) != 2:
        raise ValueError("expected exactly two agents")

    # eta_hat
    inefficient_specialization = 1 - differential_inefficient

    # eta_hat_hat
    min_min_specialization = min(
        agents[0].get_trait("min_specialization"), agents[1].get_trait("min_specialization")
    )
    efficient_specialization = 1 - min_min_specialization + differential_efficient

    strategy = get_strategy(
        efficient_specialization,
        agents[0].get_trait("min_specialization"),
        agents[1].get_trait("min_specialization"),
    )

    payoff_sn = inefficient_specialization
    payoff_ss = (1 - strategy) * (
        agents[0].get_trait("min_specialization") + efficient_specialization
    ) + strategy * (agents[1].get_trait("min_specialization") + efficient_specialization)

    return payoff_sn, payoff_ss
