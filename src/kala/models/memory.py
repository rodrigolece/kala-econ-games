from collections import deque
from typing import Generic, Protocol
from pydantic import BaseModel

from kala.models.data import Properties, SaverProperties


class MemoryItem(BaseModel, Generic[Properties]):
    # Keep info of each payoff
    payoff: float

    # Replace `savings` with a global score attribute
    score: float

    # Information about if the current match was lost
    match_lost: bool

    # Moment in time
    time: int

    properties: Properties


# Memory is a (finite) list of memory items
Memory = deque[MemoryItem[Properties]]


# An agent can dynamically adapt its strategies, which are encoded in its
# properties. This class defines how a strategy is updated based on the
# agent's current properties  and memory.
class UpdateRule(Generic[Properties], Protocol):
    def update(
        self,
        properties: Properties,
        memory: Memory,
    ) -> None: ...


class SaverFlipAfterFractionLost(UpdateRule[SaverProperties]):
    def __init__(self, frac: float) -> None:
        self.frac = frac

    def update(
        self,
        properties,  # passed as shallow copy
        memory: Memory,
    ) -> None:
        memory_length = memory.maxlen

        if len(memory) != memory_length:
            return None

        losses = sum(item.match_lost for item in memory)

        if (self.frac == 0 and losses > 0) or losses >= (memory_length * self.frac):
            properties.is_saver = not properties.is_saver
            memory.clear()
