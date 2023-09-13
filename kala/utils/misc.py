"""Miscellaneous utilities."""
import random
import string


def universally_unique_identifier(length: int = 6, rng: int | None = None) -> str:
    """
    Generate an identifier random string (no guarantees are made wrt clashes).

    Parameters
    ----------
    length : int, optional
        The number of characters in the string, by default 6.
    rng : int, optional
        A seed for the random number generator, by default None.

    Returns
    -------
    str

    """
    if length <= 1:
        raise ValueError("choose length > 1")

    if rng:
        random.seed(rng)

    first = random.choice(string.ascii_lowercase)
    rest = "".join(random.sample(string.ascii_letters + string.digits, k=length - 1))

    return first + rest
