from typing import Sequence

import numpy as np
from numpy.random import Generator


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
