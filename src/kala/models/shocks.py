"""Module defining different types of shocks."""

from abc import ABC, abstractmethod

import numpy as np
from numpy.random import Generator

from kala.models.agents import AgentT
from kala.models.game import DiscreteGameT


class BaseShock(ABC):
    """
    Base shock meant to be subclassed.

    """

    @abstractmethod
    def apply(self, game: DiscreteGameT) -> None:
        """Apply the shock to the game (this modifies the game in place)."""


class RemovePlayer(BaseShock):
    """Remove a specific player from the game."""

    def __init__(self, node: AgentT | int | str):
        self.node = node

    def apply(self, game: DiscreteGameT):
        node = game.graph.get_node(self.node) if isinstance(self.node, int | str) else self.node
        if node is None:
            print("node not found; passing")
            return

        print("removing player", node)
        game.graph.remove_node(node)


class RemoveRandomPlayer(BaseShock):
    """Remove a player selected at random from the game."""

    def __init__(self, rng: Generator | int | None = None):
        self.rng = np.random.default_rng(rng)

    def apply(self, game: DiscreteGameT):
        node = game.graph.select_random_node(rng=self.rng)
        print("removing player", node)
        game.graph.remove_node(node)


class RemoveEdge(BaseShock):
    """Remove a specific edge from the game."""

    def __init__(self, u: AgentT | int | str, v: AgentT | int | str):
        self.u = u
        self.v = v

    def apply(self, game: DiscreteGameT):
        u = game.graph.get_node(self.u) if isinstance(self.u, int | str) else self.u
        v = game.graph.get_node(self.v) if isinstance(self.v, int | str) else self.v
        print(f"removing edge ({u}, {v})")
        game.graph.remove_edge(u, v)


class RemoveRandomEdge(BaseShock):
    """Remove an edge selected at random from the game."""

    def __init__(self, rng: Generator | int | None = None):
        self.rng = np.random.default_rng(rng)

    def apply(self, game: DiscreteGameT):
        u = game.graph.select_random_node(rng=self.rng)
        v = game.graph.select_random_neighbour(u, rng=self.rng)

        if v is not None:
            print(f"removing edge ({u}, {v})")
            game.graph.remove_edge(u, v)


class SwapEdge(BaseShock):
    """Swap an edge in the game."""

    def __init__(self, pivot_u: AgentT | int | str, v: AgentT | int | str, w: AgentT | int | str):
        self.pivot_u = pivot_u
        self.v = v
        self.w = w

    def apply(self, game: DiscreteGameT):
        print(f"swapping edge: ({self.pivot_u}, {self.v}) -> ({self.pivot_u}, {self.w})")

        game.graph.remove_edge(self.pivot_u, self.v)
        game.graph.add_edge(self.pivot_u, self.w)


class SwapRandomEdge(BaseShock):
    """Swap an edge selected at random from the game."""

    def __init__(self, max_attempts: int = 10, rng: Generator | int | None = None):
        self.max_attempts = max_attempts
        self.rng = np.random.default_rng(rng)

    def apply(self, game: DiscreteGameT):
        pivot_u = game.graph.select_random_node(rng=self.rng)
        neighs = game.graph.get_neighbours(pivot_u)
        v = game.graph.select_random_neighbour(pivot_u, rng=self.rng)

        w = pivot_u
        attempts = 0
        while w == pivot_u or w in neighs:
            if attempts == self.max_attempts:
                v = None  # don't take any action
                break
            w = game.graph.select_random_node(rng=self.rng)
            attempts += 1

        if v is not None:
            print(f"swapping edge: ({pivot_u}, {v}) -> ({pivot_u}, {w})")
            game.graph.remove_edge(pivot_u, v)
            game.graph.add_edge(pivot_u, w)
