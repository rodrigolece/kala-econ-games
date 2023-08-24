from typing import Any, Callable, Iterable, Sequence

import numpy as np
from numpy.random import Generator
from scipy import integrate
from scipy.optimize import fsolve
from scipy.special import erf  # pylint: disable=no-name-in-module
from scipy.stats import multivariate_normal as mvn


def _default_rng(rng: Generator | None = None):
    """If rng is already a Generator, pass-through; otherwise return default."""

    if rng is None:
        rng = np.random.default_rng()
    elif isinstance(rng, int):
        rng = np.random.default_rng(rng)

    return rng


def choice(
    lst: Iterable[Any], size: int | None = None, replace: bool = False, rng: Generator | None = None
):
    rng = _default_rng(rng)
    rng.choice(lst, size=size, replace=replace)

    return rng.choice(lst, size=size, replace=replace)


def normal(
    loc: float,
    scale: float,
    size: int | None = None,
    rng: Generator | None = None,
) -> float | np.ndarray:
    """
    Thin wrapper around NumPy's normal distribution.

    """
    rng = _default_rng(rng)

    return rng.normal(loc, scale, size)


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


def roots_eta_hat(
    eta: float,
    min_specialization: float,
    min_consumption: float,
    sigma: Callable,
    d_sigma: Callable,
    args_sigma: list,
):
    """
    Equation from which we obtain eta hat.
    """
    sigma_eta = sigma(eta, args_sigma)
    d_sigma_eta = d_sigma(eta, args_sigma)
    arg = min_consumption / (np.sqrt(2) * sigma_eta)
    d_erf = (
        np.sqrt(2 / np.pi)
        * (min_consumption / (sigma_eta**2))
        * (1 - np.exp(-1 * arg**2))
        * d_sigma_eta
    )

    equation = (min_specialization + eta) * d_erf + erf(arg) - 1
    return equation


def kernel(x: float, y: float, sigma: float):
    """
    Kernel of multivariate normal distribution used to integrate.
    """
    arg = (x**2 + y**2) / (2 * sigma)
    return np.exp(-1 * arg) * (arg - 1)


def roots_eta_hat_hat(
    eta: float,
    min_specialization: float,
    min_consumption: float,
    sigma: Callable,
    d_sigma: Callable,
    args_sigma: list,
):
    """
    Equation from which we obtain eta hat hat.
    """
    # FIXME: below is a hack but I don't understand why sigma returns array
    sigma_eta = sigma(eta, args_sigma)[0]
    d_sigma_eta = d_sigma(eta, args_sigma)

    if sigma_eta > 0:
        area = mvn.cdf(
            [min_consumption, min_consumption],
            mean=[0, 0],
            cov=[[sigma_eta, 0], [0, sigma_eta]],
        )
    else:
        area = 1
    integral = integrate.nquad(
        kernel,
        [[-np.inf, min_consumption], [-np.inf, min_consumption]],
        args=[sigma_eta],
    )[0]
    d_area = (1 / (2 * np.pi * sigma_eta**2)) * d_sigma_eta * integral

    equation = (min_specialization + eta) * d_area + area - 1
    return equation


def get_eta_hat(
    min_specialization: float,
    min_consumption: float,
    sigma: Callable,
    d_sigma: Callable,
    args_sigma: list,
    x0: float = 1.0,
):
    """
    Function to obtain eta hat for an individual saver.
    """
    eta_hat = fsolve(
        roots_eta_hat, x0, args=(min_specialization, min_consumption, sigma, d_sigma, args_sigma)
    )
    return eta_hat[0]


def get_eta_hat_hat(
    min_specialization: float,
    min_consumption: float,
    sigma: Callable,
    d_sigma: Callable,
    args_sigma: list,
    x0: float = 1.0,
):
    """
    Function to obtain eta hat hat for two savers,
    supposing that min_specialization and s are the same for both.
    """
    eta_hat_hat = fsolve(
        roots_eta_hat_hat,
        x0,
        args=(min_specialization, min_consumption, sigma, d_sigma, args_sigma),
    )
    return eta_hat_hat[0]
