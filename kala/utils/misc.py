"""Miscellaneous utilities."""
import random
import string


def uuid(length: int = 6) -> str:
    """
    Generate an identifier random string (no guarantees are made wrt clashes).

    Parameters
    ----------
    length : int, optional
        The number of characters in the string, by default 6.

    Returns
    -------
    str

    """
    if length <= 1:
        raise ValueError("choose length > 1")

    first = random.choice(string.ascii_lowercase)
    rest = "".join(random.sample(string.ascii_letters + string.digits, k=length - 1))

    return first + rest
