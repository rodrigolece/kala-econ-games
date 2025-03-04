"""Module defining the agents"""

from collections import deque
from typing import Generic  # Any,TypeVar
from uuid import UUID, uuid4

from kala.models.data import Properties, SaverProperties, SaverTraits, Traits
from kala.models.memory import Memory, MemoryItem, UpdateRule


class SaverAgent(Generic[Traits, Properties]):
    """
    Attributes
    ----------
    uuid : int | str
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
    memory : Memory | None
        The memory of the agent, storing a number of previous matches.
    """

    # Using the built-in uuid library
    uuid: UUID

    # These properties are intentionally public (no leading underscore) to
    # allow direct access, making it easier to extract necessary information.
    traits: Traits
    properties: Properties

    # The `savings` attribute was removed from `SaverProperty` and moved to the
    # agent’s `score`. This makes sense if payoff is a global concept, as
    # tracking its accumulation throughout a game is generally useful.
    score: float = 0

    memory: Memory | None
    update_rule: UpdateRule[Properties] | None

    def __init__(
        self,
        traits: Traits,
        properties: Properties,
        score: float = 0,
        uuid: UUID | None = None,
        memory: Memory | None = None,
        update_rule: UpdateRule | None = None,
    ):
        self.score = score
        self.uuid = uuid or uuid4()

        # Traits, properties, memory and update rules must be provided when creating
        # an agent. This allows different agents in the same game to have
        # distinct update rules. While this makes instantiation more involved,
        # convenient initializers can be created for common scenarios.
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


def init_saver_agent(
    is_saver: bool,
    group: int | None = None,
    min_specialization: float = 0.0,
    income_per_period: float = 1.0,
    homophily: float | None = None,
    memory_length: int = 10,
    update_rule: UpdateRule | None = None,
) -> SaverAgent:
    """Initialise new saver agent.

    Parameters
    ----------
    is_saver : bool
        Boolean indicating whether the agent is a saver or not.
    group : int
        Optional group (handy to keep track for example of SBM clusters).
    min_specialization : float
        The minimum specialization (default is 0.0).
    income_per_period : float
        The income per period (default is 1.0).
    homophily : float | None
        The homophily of the agent (default is None), if passed should be a
        number between [0, 1].
    memory_length: int
        The number of matches played that an agent holds in memory (default is 10).
    update_rule: MemoryRuleT | None
        The rule used to decide whether the agent should change their saver
        status depending on the outcome of the previous matches (default is None).
    uuid : int | str | None
        The unique identifier of the agent (default is None and a random string
        is generated).

    Returns
    -------
    SaverAgent

    """
    traits = SaverTraits(
        group=group,
        min_specialization=min_specialization,
        income_per_period=income_per_period,
        homophily=homophily,
    )

    props = SaverProperties(is_saver=is_saver)
    memory = deque([], maxlen=memory_length) if memory_length else None

    return SaverAgent(traits, props, score=0, memory=memory, update_rule=update_rule)
