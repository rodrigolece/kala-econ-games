"""Module defining different types of shocks."""

from abc import ABC, abstractmethod
from typing import Sequence

import numpy as np
from numpy.random import Generator

from kala.models.agents import AgentT
from kala.models.game import DiscreteGameT
from kala.utils.config import DEBUG


class BaseShock(ABC):
    """
    Base shock meant to be subclassed.

    """

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __repr__(self) -> str:
        return f"<{str(self)}>"

    @abstractmethod
    def apply(self, game: DiscreteGameT) -> None:
        """Apply the shock to the game (this modifies the game in place)."""


class RemovePlayer(BaseShock):
    """Remove a specific player from the game."""

    def __init__(self, node: AgentT | int | str):
        self.node = node

    def apply(self, game: DiscreteGameT):
        node = game.graph.get_node(self.node) if isinstance(self.node, int | str) else self.node
        if DEBUG and node is None:
            print("node not found; passing")
            return

        if DEBUG:
            print("removing player", node)
        game.graph.remove_node(node)


class RemoveRandomPlayer(BaseShock):
    """Remove a player selected at random from the game."""

    def __init__(self, rng: Generator | int | None = None):
        self.rng = np.random.default_rng(rng)

    def apply(self, game: DiscreteGameT):
        node = game.graph.select_random_node(rng=self.rng)
        if DEBUG:
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
        if DEBUG:
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
            if DEBUG:
                print(f"removing edge ({u}, {v})")
            game.graph.remove_edge(u, v)


class SwapEdge(BaseShock):
    """Swap an edge in the game."""

    def __init__(self, pivot_u: AgentT | int | str, v: AgentT | int | str, w: AgentT | int | str):
        self.pivot_u = pivot_u
        self.v = v
        self.w = w

    def apply(self, game: DiscreteGameT):
        if DEBUG:
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
            if DEBUG:
                print(f"swapping edge: ({pivot_u}, {v}) -> ({pivot_u}, {w})")
            game.graph.remove_edge(pivot_u, v)
            game.graph.add_edge(pivot_u, w)


class AddEdge(BaseShock):
    """Add an edge in the game."""

    def __init__(self, u: AgentT | int | str, v: AgentT | int | str):
        self.u = u
        self.v = v

    def apply(self, game: DiscreteGameT):
        if DEBUG:
            print(f"Adding edge: ({self.u}, {self.v})")

        game.graph.add_edge(self.u, self.v)


class AddRandomEdge(BaseShock):
    """Add an edge selected at random from the game."""

    def __init__(self, max_attempts: int = 10, rng: Generator | int | None = None):
        self.max_attempts = max_attempts
        self.rng = np.random.default_rng(rng)

    def apply(self, game: DiscreteGameT):
        u = game.graph.select_random_node(rng=self.rng)
        neighs = game.graph.get_neighbours(u)

        v = u
        attempts = 0
        while v == u or v in neighs:
            if attempts == self.max_attempts:
                v = None  # don't take any action
                break
            v = game.graph.select_random_node(rng=self.rng)
            attempts += 1

        if v is not None:
            if DEBUG:
                print(f"Adding edge: ({u}, {v})")
            game.graph.add_edge(u, v)


class FlipSaver(BaseShock):
    """Flip an agent's saving trait."""

    def __init__(self, node: AgentT | int | str):
        self.node = node

    def apply(self, game: DiscreteGameT):
        node = game.graph.get_node(self.node)
        node.flip_saver_property()


class FlipRandomSaver(BaseShock):
    """Flip a random agent's saving trait."""

    def __init__(self, rng: Generator | int | None = None):
        self.rng = np.random.default_rng(rng)

    def apply(self, game: DiscreteGameT):
        node = game.graph.select_random_node(rng=self.rng)
        node.flip_saver_property()


class FlipSavers(BaseShock):
    """Flip agents' saving traits from Sequence."""

    def __init__(self, list_of_agents: Sequence[AgentT | int | str]):
        self.list_of_agents = list_of_agents

    def apply(self, game: DiscreteGameT):
        for agent in self.list_of_agents:
            node = game.graph.get_node(agent)
            node.flip_saver_property()


class FlipAllSavers(BaseShock):
    """Flip all savers in a game."""

    def apply(self, game: DiscreteGameT):
        for node in game.graph.get_nodes():
            node.flip_saver_property()


class HomogenizeSaversTo(BaseShock):
    """Shock to homogenize savers to a given target trait."""

    def __init__(self, target: bool):
        self.target = target

    def apply(self, game: DiscreteGameT):
        filt = game.create_filter_from_property("is_saver", self.target)

        for agent, val in enumerate(filt):
            if not val:
                node = game.graph.get_node(agent)
                node.flip_saver_property()


class ChangeRandomPlayerMemoryLength(BaseShock):
    """Shock to change the memory length of a random agent."""

    def __init__(self, new_memory_length: int, rng: Generator | int | None = None):
        self.memory_length = new_memory_length
        self.rng = rng

    def apply(self, game: DiscreteGameT):
        node = game.graph.select_random_node(rng=self.rng)
        node.change_memory_length(self.memory_length)


class ChangeAllPlayersMemoryLength(BaseShock):
    """Shock to change all players memory with an integer or a list of integers."""

    def __init__(self, new_memory_length: int | Sequence[int]):
        self.memory_length = new_memory_length

    def apply(self, game: DiscreteGameT):
        num_players = game.get_num_players()

        if isinstance(self.memory_length, int):
            for node in game.graph.get_nodes():
                node.change_memory_length(self.memory_length)
        else:
            assert len(self.memory_length) == num_players
            for i, node in enumerate(game.graph.get_nodes()):
                node.change_memory_length(self.memory_length[i])


class ChangeDifferentialEfficient(BaseShock):
    """Shock to change the differential efficient parameter of the game strategy."""

    def __init__(self, new_differential_efficient: float):
        self.differential_efficient = new_differential_efficient

    def apply(self, game: DiscreteGameT):
        payoff_ss = 1 + self.differential_efficient
        game.strategy.payoff_matrix[("saver", "saver")] = (payoff_ss, payoff_ss)


class ChangeDifferentialInefficient(BaseShock):
    """Shock to change the differential inefficient parameter of the game strategy."""

    def __init__(self, new_differential_inefficient: float):
        self.differential_inefficient = new_differential_inefficient

    def apply(self, game: DiscreteGameT):
        payoff_sn = 1 - self.differential_inefficient
        game.strategy.payoff_matrix[("saver", "non-saver")] = (payoff_sn, 1)
        game.strategy.payoff_matrix[("non-saver", "saver")] = (1, payoff_sn)
