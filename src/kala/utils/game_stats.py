"""Utility functions to interact with a game and calculate some statistics."""

from kala.models import GameState, SaverProperties, SaverTraits
from kala.models.agents import Agent


def get_summed_score(agents: list[Agent]) -> float:
    """Get the sum of the scores of all agents in the game."""
    return sum(a.score for a in agents)


def get_saver_agents(
    state: GameState[SaverTraits, SaverProperties],
) -> list[Agent[SaverTraits, SaverProperties]]:
    """Get all saver agents from the game state."""
    return [a for a in state.agents if a.properties.is_saver]
