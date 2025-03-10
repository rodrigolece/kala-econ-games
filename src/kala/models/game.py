"""Module defining the top-level classes of games that put everything together."""

from typing import Generator, Generic, Mapping, Protocol

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


class Shock(Protocol):
    def apply(self, state: GameState) -> GameState: ...


class GamePlan:
    """The `GamePlan` class manages the administration of "shocks" during the game."""

    steps: int = 0

    # The `shocks` dictionary maps time steps (integers) to lists of `Shock`
    # objects. This structure simplifies scheduling shocks at specific times.
    shocks: dict[int, list[Shock]]

    # Example Usage:
    #
    # shocks = {
    #     20: [RemoveRandomEdge()],  # Shock at time step 20
    #     50: [AddEdge(), RemoveRandomEdge()], # Multiple shocks at time step 50
    # }

    state = GameState

    def __init__(self, steps: int, shocks: Mapping[int, list[Shock]]):
        self.steps = steps
        self.shocks = shocks


# Game Logic Functions
#
# With the data structures defined, the core game logic is implemented as a set of
# functions.


# This function determines how a match is played out (depending on the payoff strategy)
def play_match(
    agents: list[Agent[Traits, Properties]],
    payoff_strategy: PayoffStrategy,
) -> list[tuple[Agent, float, bool]]:
    payoffs = payoff_strategy.calculate_payoff(agents)
    max_payoff = max(payoffs)
    # Returns a list of (agent, payoff, lost_match) tuples, where lost_match is
    # True if the agent received strictly less than the max payoff
    return [
        (agent, payoff, payoff < max_payoff) for agent, payoff in zip(agents, payoffs)
    ]


# This function determines how a game step is played
def play_step(time: int, state: GameState):
    matches = state.matching_strategy.select_matches(state.placements, state.graph)
    updates = [
        payoff
        for agents in matches
        for payoff in play_match(agents, state.payoff_strategy)
    ]
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


# class DiscreteBaseGame(ABC, Generic[GraphT, StrategyT]):
#     """
#     Base game meant to be subclassed.

#     Attributes
#     ----------
#     time : int
#         The current time of the game.


#     Methods
#     -------
#     play_round()
#     get_num_players()
#     get_total_wealth()
#     create_filter_from_property()
#     create_filter_from_trait()
#     get_num_savers()
#     reset_agents()

#     """


#     def play_round(self, *args, **kwargs) -> None:
#         """Match pairs of agents and advance the time."""

#     def get_total_wealth(self, filt: Sequence[bool] | None = None) -> float:
#         out = 0.0
#         if filt is not None:
#             assert len(filt) == self.get_num_players(), "'filt' must be the same length as players"
#         players = (
#             itertools.compress(self._get_players(), filt)
#             if filt is not None
#             else self._get_players()
#         )

#         for player in players:
#             out += player.get_property("savings")

#         return out


# class DiscreteTwoByTwoGame(DiscreteBaseGame):
#     """
#     A discrete 2x2 game where agents play their strategy in pairs.

#     """

#     # pylint: disable=unused-argument
#     def play_round(self, *args, **kwargs) -> None:
#         rng = get_random_state(kwargs.get("rng", None))

#         players = self.graph.get_nodes()
#         selection = rng.choice(players, size=(len(players) // 2))

#         for player in selection:
#             opponent = self.graph.select_random_neighbour(player, rng=rng)
#             if opponent is None:
#                 continue

#             payoffs = np.array(self.strategy.calculate_payoff(player, opponent, **kwargs))
#             achieved_min_payoff = payoffs < payoffs.max()

#             for agent, pay, outcome in zip((player, opponent), payoffs, achieved_min_payoff):
#                 agent.update(payoff=pay, match_lost=outcome)

#         self.time += 1
