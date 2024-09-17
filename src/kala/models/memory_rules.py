"""Module defining the learning/updating strategies available for agents."""

from abc import ABC, abstractmethod
from collections import deque
from typing import TypeVar

import numpy as np


class BaseMemoryRule(ABC):
    """
    Base memory rule intended to be subclassed.

    Attributes
    ----------
    memory_length : int
        The number of previous outcomes kept in memory to decide whether to
        change the saving strategy (default is 1).

    Methods
    -------
    should_update()

    """

    def __init__(self, memory_length: int = 1, **kwargs) -> None:  # pylint: disable=unused-argument
        """Initialize the memory rule."""
        if memory_length < 0 or not isinstance(memory_length, int):
            raise ValueError("expected non-negative integer for 'memory_length'")
        self.memory_length = memory_length

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def __str__(self) -> str:
        return f"<{str(self)}>"

    @abstractmethod
    def should_update(self, memory: deque) -> bool:
        """
        Determine whether the states held in memory grant and update or not."""


MemoryRuleT = TypeVar("MemoryRuleT", bound=BaseMemoryRule)
"""Used to refer to BaseMemoryRule as well as its subclasses."""


class WeightedMemoryRule(BaseMemoryRule):
    """
    Memory rule that ascertains that an agent should updates its strategy if the
    sum of the weighted games won is below the sum of the weighted games lost.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if (weights := kwargs.get("weights", None)) is None:
            raise ValueError("expected 'weights' keyword argument")
        self.weights = weights

        if (frac := kwargs.get("fraction", None)) is None:
            raise ValueError("expected 'fraction' keyword argument")
        self.fraction = frac

        self.name = "Weighted Memory Rule"

    def should_update(self, memory: deque) -> bool:
        n = self.memory_length  # pylint: disable=invalid-name
        if len(self.weights) != n:
            raise ValueError(f"expected length of {n} for 'weights', observed {len(self.weights)}")
        return len(memory) == n and np.average(memory, weights=self.weights) < self.fraction


class FractionMemoryRule(BaseMemoryRule):
    """
    Memory rule that ascertains that an agent should update its strategy if the
    fraction of games won is below a certain fraction.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if (frac := kwargs.get("fraction", None)) is None:
            raise ValueError("expected 'fraction' keyword argument")
        self.fraction = frac
        self.name = f"Fraction Memory {frac} Rule"

    def should_update(self, memory: deque) -> bool:
        n = self.memory_length  # pylint: disable=invalid-name

        if len(memory) != n:
            return False

        if self.fraction == 0:
            # NB: we add this condition so that FractionMemoryRule(fraction=0)
            # is equivalent to AllPastMemoryRule
            return sum(memory) == 0

        return sum(memory) < n * self.fraction


class AverageMemoryRule(BaseMemoryRule):
    """
    Memory rule that ascertains that an agent should updates its strategy if the
    fraction of games won is below 1/2.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fraction = 0.5
        self.name = "Average Memory Rule"

    def should_update(self, memory: deque) -> bool:
        n = self.memory_length  # pylint: disable=invalid-name
        return len(memory) == n and sum(memory) < n * self.fraction


class AllPastMemoryRule(BaseMemoryRule):
    """
    Memory rule that ascertains that an agent should updates its strategy if all
    of the games in memory were lost."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name = "All Past Memory Rule"

    def should_update(self, memory: deque) -> bool:
        return len(memory) == self.memory_length and sum(memory) == 0


class AnyPastMemoryRule(BaseMemoryRule):
    """
    Memory rule that ascertains that an agent should updates its strategy if any
    of the games in memory were lost."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name = "Any Past Memory"

    def should_update(self, memory: deque) -> bool:
        n = self.memory_length  # pylint: disable=invalid-name
        return len(memory) == n and sum(memory) < n
