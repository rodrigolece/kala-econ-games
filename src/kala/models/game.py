"""Module defining the top-level classes of games that put everything together."""

from typing import Generator, Generic, Mapping, Protocol, Sequence

import networkx as nx

from kala.models.agents import Agent
from kala.models.data import Properties, Traits
from kala.models.graphs import AgentPlacement
from kala.models.strategies import MatchingStrategy, PayoffStrategy


class GameState(Generic[Traits, Properties]):
    graph: nx.Graph
    agents: list[Agent[Traits, Properties]]
    placements: AgentPlacement
    payoff_strategy: PayoffStrategy[Traits, Properties]
    matching_strategy: MatchingStrategy[Traits, Properties]

    def __init__(
        self,
        graph: nx.Graph,
        agents: Sequence[Agent[Traits, Properties]],
        placements: AgentPlacement,
        payoff_strategy: PayoffStrategy[Traits, Properties],
        matching_strategy: MatchingStrategy[Traits, Properties],
    ):
        self.graph = graph
        self.agents = list(agents)
        self.placements = placements
        self.payoff_strategy = payoff_strategy
        self.matching_strategy = matching_strategy


# NB: this is placed here instead of shocks.py to avoid circular imports
class Shock(Protocol):
    def apply(self, state: GameState[Traits, Properties]) -> GameState[Traits, Properties]:
        """Apply the shock to the game (this modifies the game in place)."""


class GamePlan:
    """The `GamePlan` class manages the administration of "shocks" during the game."""

    steps: int

    # The `shocks` dictionary maps time steps (integers) to lists of `Shock`
    # objects. This structure simplifies scheduling shocks at specific times.
    shocks: Mapping[int, list[Shock]]

    # Example Usage:
    #
    # shocks = {
    #     20: [RemoveRandomEdge()],  # Shock at time step 20
    #     50: [AddEdge(), RemoveRandomEdge()], # Multiple shocks at time step 50
    # }

    def __init__(self, steps: int, shocks: Mapping[int, list[Shock]]):
        self.steps = steps
        self.shocks = shocks


# Game Logic Functions


def play_match(
    agents: list[Agent[Traits, Properties]],
    payoff_strategy: PayoffStrategy,
) -> list[tuple[Agent, float, bool]]:
    """This function determines how a match (between two agents) is played out."""
    payoffs = payoff_strategy.calculate_payoff(agents)
    max_payoff = max(payoffs)
    # Returns a list of (agent, payoff, lost_match) tuples, where lost_match is
    # True if the agent received strictly less than the max payoff
    return [(agent, payoff, payoff < max_payoff) for agent, payoff in zip(agents, payoffs)]


def play_step(time: int, state: GameState):
    """This function determines how a game step is played out."""
    matches = state.matching_strategy.select_matches(state.placements, state.graph)
    updates = [payoff for agents in matches for payoff in play_match(agents, state.payoff_strategy)]
    # For each agent, update its state based on the calculated payoff and
    # whether it received the minimum payoff in its match (lost_match).
    for agent, payoff, lost_match in updates:
        agent.update(payoff=payoff, lost_match=lost_match, time=time)


# This function orchestrates the entire game, running it step by step until
# completion. It follows the structured workflow outlined earlier, with each
# step customizable through the provided matching strategy and game plan.
# The initial `GameState` encapsulates the game's rules, including how payoffs
# are computed and how agents behave. While setting up the initial state can be
# a bit cumbersome, this could be streamlined with helper functions if needed.
# Note that this function is an iterator, yielding the game state at each step.
# Since the game state contains information about agents, the graph, and other
# relevant details, it allows for easy tracking and analysis during the game's
# progression.
def play_game(
    state: GameState,
    game_plan: GamePlan,
) -> Generator[tuple[int, GameState], None, None]:
    """
    Orchestate a full game.
    """
    for time in range(game_plan.steps):
        shocks = game_plan.shocks.get(time, [])

        for shock in shocks:
            state = shock.apply(state)

        play_step(time, state)

        yield time, state
