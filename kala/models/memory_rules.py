"""Module defining the learning/updating strategies available for agents."""
from abc import ABC, abstractmethod
from collections import deque
from typing import TypeVar


class BaseMemoryRule(ABC):
    """
    Base memory rule intended to be subclassed.

    Methods
    -------
    should_update()

    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the memory rule."""

    @abstractmethod
    def should_update(self, memory: deque) -> bool:
        """
        Determine whether the states held in memory grant and update or not."""


MemoryRuleT = TypeVar("MemoryRuleT", bound=BaseMemoryRule)
"""Used to refer to BaseMemoryRule as well as its subclasses."""


class FractionMemoryRule(BaseMemoryRule):
    """
    Memory rule that ascertains that an agent should updates its strategy if the
    fraction of games won is below a certain fraction.
    """

    def __init__(self, *args, **kwargs) -> None:
        if (frac := kwargs.get("fraction", None)) is None:
            raise ValueError("expected 'fraction' keyword argument")
        self.fraction = frac

    def should_update(self, memory: deque) -> bool:
        n = memory.maxlen  # pylint: disable=invalid-name
        return len(memory) == n and sum(memory) < n * self.fraction


class AverageMemoryRule(BaseMemoryRule):
    """
    Memory rule that ascertains that an agent should updates its strategy if the
    fraction of games won is below 1/2.
    """

    def __init__(self, *args, **kwargs) -> None:
        self.fraction = 0.5

    def should_update(self, memory: deque) -> bool:
        n = memory.maxlen  # pylint: disable=invalid-name
        return len(memory) == n and sum(memory) < n * self.fraction


class AllPastMemoryRule(BaseMemoryRule):
    """
    Memory rule that ascertains that an agent should updates its strategy if all
    of the games in memory were lost."""

    def should_update(self, memory: deque) -> bool:
        n = memory.maxlen  # pylint: disable=invalid-name
        return len(memory) == n and sum(memory) == n


class AnyPastMemoryRule(BaseMemoryRule):
    """
    Memory rule that ascertains that an agent should updates its strategy if any
    of the games in memory were lost."""

    def should_update(self, memory: deque) -> bool:
        n = memory.maxlen  # pylint: disable=invalid-name
        return len(memory) == n and sum(memory) > 0
