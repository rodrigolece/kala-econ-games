from collections import deque

import numpy as np

from kala.models import (
    AgentPlacementNetX,
    GameState,
    MatchingStrategy,
    SaverAgent,
    SaverCooperationPayoffStrategy,
    SaverFlipAfterFractionLost,
    SaverProperties,
    SaverTraits,
)
from kala.models.memory import CappedMemory, UpdateRule

from .io.netz import NetzDatabase


DB = NetzDatabase()


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
    memory_length = memory_length or 10
    memory: CappedMemory = deque([], maxlen=memory_length)

    return SaverAgent(traits, props, memory, score=0, update_rule=update_rule)


def init_savers_gamestate_from_netz(
    network_name: str,
    savers_share: float = 0.5,
    memory_length: int = 10,
    memory_frac: float = 0.5,
) -> GameState:
    """
    Initialise a game state from a network.

    Parameters
    ----------
    network_name : str
        The name of the network to initialise the game state from.
    savers_share : float
        The initial share of savers in the network (default is 0.5).
    memory_length : int
        The number of matches played that an agent holds in memory (default is 10).
    memory_frac : float
        The agent is using the `SaverFlipAfterFractionLost` update rule which takes a `frac`
        as an input parameter. `memory_frac` is used to set this parameter.

    Returns
    -------
    GameState

    """
    graph = DB.read_netzschleuder_network(network_name)
    num_nodes = graph.number_of_nodes()

    rng = np.random.default_rng()
    is_saver = rng.choice([True, False], num_nodes, p=[savers_share, 1 - savers_share])

    rule = SaverFlipAfterFractionLost(frac=memory_frac)
    agents = [init_saver_agent(s, memory_length=memory_length, update_rule=rule) for s in is_saver]
    placement = AgentPlacementNetX.init_bijection(agents, graph)

    return GameState(graph, agents, placement, SaverCooperationPayoffStrategy(), MatchingStrategy())
