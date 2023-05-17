"""Miscellaneous utilities."""
import random
import string


def uuid(length: int = 6) -> str:
    """
    Generate a random string identifier (no guarantees are made wrt to clashes).

    Parameters
    ----------
    length : int, optional
        _description_, by default 6

    Returns
    -------
    str

    """
    if length <= 1:
        raise ValueError("choose length > 1")
    first = random.choice(string.ascii_lowercase)

    rest = "".join(random.sample(string.ascii_letters + string.digits, k=length - 1))
    return first + rest
