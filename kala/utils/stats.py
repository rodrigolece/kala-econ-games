from typing import Callable, Sequence

import numpy as np
from numpy.random import Generator
from scipy import integrate
from scipy.optimize import fsolve
from scipy.special import erf
from scipy.stats import multivariate_normal as mvn


def truncated_normal(
    loc: float,
    scale: float,
    size: int | None = None,
    rng: Generator | None = None,
) -> float | np.ndarray:
    if rng is None:
        rng = np.random.default_rng()

    vals = rng.normal(loc, scale, size)
    return np.maximum(vals, 0)


def truncated_multivariate_normal(
    mean: Sequence[float],
    var: Sequence[float] | None = None,
    cov: np.ndarray | None = None,
    size: int | None = None,
    rng: Generator | None = None,
):
    """
    Exactly one of vars or cov must be non-null.
    """
    if rng is None:
        rng = np.random.default_rng()

    mean = np.asarray(mean)

    if var is not None:
        assert len(var) == len(mean)
        cov = np.diag(var)

    elif cov is not None:
        cov = np.asarray(cov)

    vals = rng.multivariate_normal(mean, cov, size=size)
    return np.maximum(vals, 0)


def roots_eta_hat(
    eta: float, alpha: float, a: float, sigma: Callable, d_sigma: Callable, args_sigma: list
):
    """
    Equation from which we obtain eta hat.
    """
    sigma_eta = sigma(eta, args_sigma)
    d_sigma_eta = d_sigma(eta, args_sigma)
    arg = a / (np.sqrt(2) * sigma_eta)
    d_erf = np.sqrt(2 / np.pi) * a * (sigma_eta**2) * (1 - np.exp(-1 * arg**2)) * d_sigma_eta

    equation = (alpha + eta) * d_erf + erf(arg) - 1
    return equation


def kernel(x: float, y: float, sigma: float):
    """
    Kernel of multivariate normal distribution used to integrate.
    """
    arg = (x**2 + y**2) / (2 * sigma)
    return np.exp(-1 * arg) * (arg - 1)


def roots_eta_hat_hat(
    eta: float, alpha: float, a: float, sigma: Callable, d_sigma: Callable, args_sigma: list
):
    """
    Equation from which we obtain eta hat hat.
    """
    sigma_eta = sigma(eta, args_sigma)
    d_sigma_eta = d_sigma(eta, args_sigma)
    # arg = a / (np.sqrt(2) * sigma_eta)  # FIXME: not used

    if sigma_eta > 0:
        F = mvn.cdf([a, a], mean=[0, 0], cov=[[sigma_eta, 0], [0, sigma_eta]])
    else:
        F = 1
    integral = integrate.nquad(kernel, [[-np.inf, a], [-np.inf, a]], args=[sigma_eta])[0]
    d_F = (1 / (2 * np.pi * sigma_eta**2)) * d_sigma_eta * integral

    equation = (alpha + eta) * d_F + F - 1
    return equation


def get_eta_hat(
    alpha: float, a: float, sigma: Callable, d_sigma: Callable, args_sigma: list, x0: float = 1.0
):
    """
    Function to obtain eta hat for an individual saver.
    """
    eta_hat = fsolve(roots_eta_hat, x0, args=(alpha, a, sigma, d_sigma, args_sigma))
    return eta_hat[0]


def get_eta_hat_hat(
    alpha: float, a: float, sigma: Callable, d_sigma: Callable, args_sigma: list, x0: float = 1.0
):
    """
    Function to obtain eta hat hat for two savers, supposing that alpha and s are the same for both.
    """
    eta_hat_hat = fsolve(roots_eta_hat_hat, x0, args=(alpha, a, sigma, d_sigma, args_sigma))
    return eta_hat_hat[0]
