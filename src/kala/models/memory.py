from collections import deque
from typing import Generic, Protocol

from pydantic import BaseModel

from kala.models.data import Properties, Properties_co, SaverProperties


class MemoryItem(BaseModel, Generic[Properties]):
    # Keep info of each payoff
    payoff: float

    # Replace `savings` with a global score attribute
    score: float

    # Information about if the current match was lost
    match_lost: bool

    # Moment in time
    time: int

    properties: Properties  # NB: passed by reference so cannot be considered immutable


# Memory is simply a list of memory items
Memory = list[MemoryItem[Properties]]

# A finite list of memory items
CappedMemory = deque[MemoryItem[Properties]]  # assumes maxlen attribute


# An agent can dynamically adapt its strategies, which are encoded in its
# properties. This class defines how a strategy is updated based on the
# agent's current properties  and memory.
class UpdateRule(Generic[Properties_co], Protocol):
    def update(
        self,
        properties: Properties,
        memory: CappedMemory,
    ) -> None: ...


class SaverFlipAfterFractionLost(UpdateRule[SaverProperties]):
    def __init__(self, frac: float) -> None:
        self.frac = frac

    def update(
        self,
        properties,  # passed as shallow copy
        memory: CappedMemory,
    ) -> None:
        memory_length = memory.maxlen

        if len(memory) != memory_length:
            return None

        losses = sum(item.match_lost for item in memory)

        if (self.frac == 0 and losses > 0) or losses >= (memory_length * self.frac):
            properties.is_saver = not properties.is_saver
            memory.clear()
