"""Module defining the agents"""

from typing import Generic, Protocol
from uuid import UUID, uuid4

from kala.models.data import Properties, SaverProperties, SaverTraits, Traits
from kala.models.memory import CappedMemory, Memory, MemoryItem, UpdateRule


class Agent(Generic[Traits, Properties], Protocol):
    """
    Top-level protocol defining an agent.

    Attributes
    ----------
    uuid : UUID
        A unique identifier for the agent.
    traits : Traits
        The traits of the agent, fixed during the course of a game.
    properties : Properties
        The properties of the agent that could changed during the course of a game.
    score : float
        The score accumulated by the agent.
    update_rule : UpdateRule | None
        The rule used to decide whether the agent should change their saver
        status depending on the outcome of the previous matches.
    memory : CappedMemory | None
        The memory of the agent, storing a number of previous matches.

    Methods
    -------
    update()

    """

    uuid: UUID
    traits: Traits
    properties: Properties
    score: float = 0

    # Optional attributes
    memory: Memory | CappedMemory | None
    update_rule: UpdateRule[Properties] | None

    def update(
        self,
        payoff: float,
        lost_match: bool,
        time: int,
    ) -> None: ...


class SaverAgent(Agent[SaverTraits, SaverProperties]):
    """
    A saver agent with (generic) Traits and Properties.

    Attributes
    ----------
    uuid : UUID
        A unique identifier for the agent.
    traits : Traits
        The traits of the agent, fixed during the course of a game.
    properties : Properties
        The properties of the agent that could changed during the course of a game.
    score : float
        The score accumulated by the agent.
    update_rule : UpdateRule | None
        The rule used to decide whether the agent should change their saver
        status depending on the outcome of the previous matches.
    memory : CappedMemory | None
        The memory of the agent, storing a number of previous matches.

    Methods
    -------
    update()

    """

    uuid: UUID
    traits: SaverTraits
    properties: SaverProperties
    score: float = 0

    memory: CappedMemory
    update_rule: UpdateRule[SaverProperties] | None

    def __init__(
        self,
        traits: SaverTraits,
        properties: SaverProperties,
        memory: CappedMemory,
        score: float = 0,
        uuid: UUID | None = None,
        update_rule: UpdateRule | None = None,
    ):
        self.score = score
        self.uuid = uuid or uuid4()
        self.traits = traits
        self.properties = properties
        self.memory = memory
        self.update_rule = update_rule

    def __hash__(self):
        return hash(self.uuid)

    def update(
        self,
        payoff: float,
        lost_match: bool,
        time: int,
    ) -> None:
        """
        Update the state of the agent after playing a match.

        Parameters
        ----------
        payoff: float
            The payoff obtained after the match.
        lost_match: bool
            True if the payoff was strictly less than the opponent's.
        time: int
            The time at which the match was played.

        """
        # This method is called at each game step where the agent is involved.
        # It updates the agent’s state and properties based on the provided
        # information.
        self.score += payoff

        # The memory stores shallow copies of the properties
        self.add_memory(payoff, lost_match, time)

        if not self.update_rule:
            return None

        # properties are passed as shallow copies so the code below updates properties
        # even without the need of a new assignment
        # NB: when the properties need to be changed this will also reset the memory
        self.update_rule.update(self.properties, self.memory)

    def add_memory(self, payoff: float, lost_match: bool, time: int) -> None:
        """
        Add the outcome of a match to the agent's memory.

        Parameters
        ----------
        payoff: float
            The payoff obtained after the match.
        lost_match: bool
            True if the payoff was strictly less than the opponent's.
        time: int
            The time at which the match was played.

        """
        self.memory.append(
            MemoryItem(
                payoff=payoff,
                score=self.score,
                properties=self.properties.model_copy(),  # shallow copy
                match_lost=lost_match,  # TODO: rename to match_lost
                time=time,
            )
        )
