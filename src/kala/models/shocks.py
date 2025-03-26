"""Module defining different types of shocks."""

import numpy as np

from kala.models.agents import Agent
from kala.models.game import GameState, Shock
from kala.settings import DEBUG


class RemovePlayer(Shock):
    """Remove a specific player from the game."""

    def __init__(self, agent: Agent):
        self.agent = agent

    def apply(self, state: GameState) -> GameState:
        node = state.placements.get_position(self.agent)
        if node is None:
            if DEBUG:
                print("node not found; passing")
            return state

        if DEBUG:
            print("removing player", self.agent.uuid)

        state.placements.clear_node(node)
        for i, agent in enumerate(state.agents):
            if agent.uuid == self.agent.uuid:
                state.agents.pop(i)
                break

        return state


class RemoveRandomPlayer(Shock):
    """Remove a player selected at random from the game."""

    def apply(self, state: GameState) -> GameState:
        rng = np.random.default_rng()
        node = rng.choice(state.graph, size=1)[0]
        agent = state.placements.get_agent(node)

        if agent is None:
            if DEBUG:
                print("node not found; passing")
            return state

        if DEBUG:
            print("removing player", agent.uuid)

        state.placements.clear_node(node)
        for i, a in enumerate(state.agents):
            if a.uuid == agent.uuid:
                state.agents.pop(i)
                break

        return state


class AddEdge(Shock):
    """Add an edge in the game."""

    def __init__(self, agent_u: Agent, agent_v: Agent):
        self.agent_u = agent_u
        self.agent_v = agent_v

    def apply(self, state: GameState) -> GameState:
        node_u = state.placements.get_position(self.agent_u)
        node_v = state.placements.get_position(self.agent_v)

        if node_u is None or node_v is None:
            if DEBUG:
                print("one or both nodes not found; passing")
            return state

        if DEBUG:
            print(f"Adding edge: ({node_u}, {node_v})")

        state.graph.add_edge(node_u, node_v)
        return state


class AddRandomEdge(Shock):
    """Add an edge selected at random from the game."""

    def __init__(self, max_attempts: int = 10):
        self.max_attempts = max_attempts

    def apply(self, state: GameState) -> GameState:
        rng = np.random.default_rng()
        node_u = rng.choice(list(state.graph), size=1)[0]
        neighbors = list(state.graph.neighbors(node_u))

        node_v = node_u
        attempts = 0
        while node_v == node_u or node_v in neighbors:
            if attempts == self.max_attempts:
                node_v = None  # don't take any action
                break
            node_v = rng.choice(list(state.graph), size=1)[0]
            attempts += 1

        if node_v is not None:
            if DEBUG:
                print(f"Adding edge: ({node_u}, {node_v})")
            state.graph.add_edge(node_u, node_v)

        return state


class RemoveEdge(Shock):
    """Remove a specific edge from the game."""

    def __init__(self, agent_u: Agent, agent_v: Agent):
        self.agent_u = agent_u
        self.agent_v = agent_v

    def apply(self, state: GameState) -> GameState:
        node_u = state.placements.get_position(self.agent_u)
        node_v = state.placements.get_position(self.agent_v)

        if node_u is None or node_v is None:
            if DEBUG:
                print("one or both nodes not found; passing")
            return state

        if DEBUG:
            print(f"removing edge ({node_u}, {node_v})")

        state.graph.remove_edge(node_u, node_v)
        return state


class RemoveRandomEdge(Shock):
    """Remove an edge selected at random from the game."""

    def apply(self, state: GameState) -> GameState:
        rng = np.random.default_rng()
        node_u = rng.choice(state.graph, size=1)[0]
        neighbors = list(state.graph.neighbors(node_u))

        if not neighbors:
            if DEBUG:
                print("no neighbors found; passing")
            return state

        node_v = rng.choice(neighbors, size=1)[0]

        if DEBUG:
            print(f"removing edge ({node_u}, {node_v})")

        state.graph.remove_edge(node_u, node_v)
        return state


class SwapEdge(Shock):
    """Swap an edge in the game."""

    def __init__(self, pivot_u: Agent, agent_v: Agent, agent_w: Agent):
        self.pivot_u = pivot_u
        self.agent_v = agent_v
        self.agent_w = agent_w

    def apply(self, state: GameState) -> GameState:
        node_u = state.placements.get_position(self.pivot_u)
        node_v = state.placements.get_position(self.agent_v)
        node_w = state.placements.get_position(self.agent_w)

        if node_u is None or node_v is None or node_w is None:
            if DEBUG:
                print("one or more nodes not found; passing")
            return state

        if DEBUG:
            print(f"swapping edge: ({node_u}, {node_v}) -> ({node_u}, {node_w})")

        state.graph.remove_edge(node_u, node_v)
        state.graph.add_edge(node_u, node_w)
        return state


class SwapRandomEdge(Shock):
    """Swap an edge selected at random from the game."""

    def __init__(self, max_attempts: int = 10):
        self.max_attempts = max_attempts

    def apply(self, state: GameState) -> GameState:
        rng = np.random.default_rng()
        node_u = rng.choice(state.graph, size=1)[0]
        neighbors = list(state.graph.neighbors(node_u))

        if not neighbors:
            if DEBUG:
                print("no neighbors found; passing")
            return state

        node_v = rng.choice(neighbors, size=1)[0]

        node_w = node_u
        attempts = 0
        while node_w == node_u or node_w in neighbors:
            if attempts == self.max_attempts:
                node_w = None  # don't take any action
                break
            node_w = rng.choice(state.graph, size=1)[0]
            attempts += 1

        if node_w is not None:
            if DEBUG:
                print(f"swapping edge: ({node_u}, {node_v}) -> ({node_u}, {node_w})")
            state.graph.remove_edge(node_u, node_v)
            state.graph.add_edge(node_u, node_w)

        return state
