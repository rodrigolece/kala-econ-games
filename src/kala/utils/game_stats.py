"""Utility functions to interact with a game and calculate some statistics."""

import numpy as np

from kala.models import GameState, SaverProperties, SaverTraits
from kala.models.agents import Agent


def get_summed_score(agents: list[Agent]) -> float:
    """
    Get the sum of the scores of all agents in the game.

    Parameters
    ----------
    agents : list[Agent]
        The list of agents to get the summed score for.

    Returns
    -------
    float

    """
    return sum(a.score for a in agents)


def get_saver_agents(
    state: GameState[SaverTraits, SaverProperties],
) -> list[Agent[SaverTraits, SaverProperties]]:
    """
    Get all saver agents from the game state.

    Parameters
    ----------
    state : GameState[SaverTraits, SaverProperties]
        The game state to get the saver agents from (this assumes SaverTraits and SaverProperties
        are being stored in the Agent class and will not work with more general agents).

    Returns
    -------
    list[Agent[SaverTraits, SaverProperties]]

    """
    return [a for a in state.agents if a.properties.is_saver]


def get_gini_coefficient(agents: list[Agent]) -> float:
    """
    Calculate the Gini coefficient for the scores of a group of agents.

    Parameters
    ----------
    agents : list[Agent]
        The list of agents to calculate the Gini coefficient for.

    Returns
    -------
    float

    """
    savings = sorted(a.score for a in agents)

    total_wealth = sum(savings)
    if np.isclose(total_wealth, 0):
        return 0.0

    N = len(savings)
    cumsum = np.cumsum(savings) / total_wealth
    gini = (N + 1 - 2 * np.sum(cumsum)) / N

    return gini
