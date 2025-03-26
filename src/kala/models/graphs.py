"""Module defining the interface for the underlying graphs."""

import warnings
from typing import Generator, Hashable, MutableMapping, Protocol, Sequence

import networkx as nx
import numpy as np

from kala.models.agents import Agent, SaverAgent
from kala.models.data import Properties, Traits


NodeID = Hashable


class AgentPlacement(Protocol):
    """Top-level protocol defining a placement of agents on top of nodes."""

    def clear_node(self, position: NodeID) -> NodeID | None:
        """Remove agent from node if present."""

    def add_agent(self, agent: Agent, position: NodeID) -> None:
        """Place an agent at a given node position."""

    def get_position(self, agent: Agent) -> NodeID | None:
        """Locate a given agent and return its node position."""

    def get_agent(self, position: NodeID) -> Agent | None:
        """Get the agent (if any) located at the given position."""

    def __iter__(self) -> Generator[tuple[NodeID, Agent], None, None]: ...


class AgentPlacementNetX(AgentPlacement):
    """
    An implementation of the AgentPlacement protocol for NetworkX.

    It is assumed that nodes in the graph can remain empty, but only a single agent
    can be located at a particular node at any given moment.

    """

    _mapping: MutableMapping[NodeID, Agent | None]

    def __init__(self):  # NB: needed (instead of attribute default) so we can define a classmethod
        self._mapping = {}

    def clear_node(self, position: NodeID) -> NodeID | None:
        node = self._mapping.pop(position, None)
        return position if node else None

    def add_agent(self, agent: Agent, position: NodeID) -> None:
        if self._mapping.get(position) is None:
            self._mapping[position] = agent
        else:
            raise ValueError("node position is not empty")

    def get_position(self, agent: Agent) -> NodeID | None:
        for k, v in self._mapping.items():
            if v is None:
                continue
            elif agent.uuid == v.uuid:
                return k
        return None

    def get_agent(self, position: NodeID) -> Agent | None:
        return self._mapping.get(position, None)

    def __iter__(self) -> Generator[tuple[NodeID, Agent], None, None]:
        for k, v in self._mapping.items():
            if v is None:
                continue
            yield (k, v)

    @classmethod
    def init_bijection(cls, agents: Sequence[Agent[Traits, Properties]], graph: nx.Graph):
        """
        Initialise a new placement from a list of agents and a graph with the same size.
        """

        if graph.number_of_nodes() != len(agents):
            raise ValueError("expected matching number of nodes and agents")

        placement = cls()
        for agent, position in zip(agents, graph):
            placement.add_agent(agent, position)

        return placement


def get_neighbours(
    agent: Agent,
    graph: nx.Graph,
    placements: AgentPlacement,
) -> list[Agent] | None:
    """

    Returns
    -------
    A (possibly empty) list of `Agent`; `None` when `agent` doesn't return a valid position.
    """

    if (position := placements.get_position(agent)) is None:
        return None

    return [
        neighbor
        for node in graph.neighbors(position)
        if (neighbor := placements.get_agent(node)) is not None
    ]


get_neighbors = get_neighbours
"""Alias for get_neighbours"""


def get_neighbour_sample_with_homophily(
    agent: SaverAgent,
    graph: nx.Graph,
    placements: AgentPlacement,
    size: int | None = None,
) -> Agent | None:
    """
    EXPERIMENTAL: draw a sample of neighbours that satisfies the homophily of a SaverAgent.

    """

    if (position := placements.get_position(agent)) is None:
        return None

    agent_is_saver = agent.properties.is_saver
    candidates = []
    ps = None

    if (homophily := agent.traits.homophily) is not None:
        ps = []
        for node in graph.neighbors(position):
            if (neighbor := placements.get_agent(node)) is not None:
                ps.append(
                    homophily if neighbor.properties.is_saver == agent_is_saver else 1 - homophily
                )
                candidates.append(neighbor)

        ps_arr = np.asarray(ps)
        mass = ps_arr.sum()
        ps_arr /= mass

    rng = np.random.default_rng()
    try:
        return rng.choice(candidates, p=ps_arr, size=size, replace=True)  # type:ignore

    except ValueError:
        warnings.warn("cannot satisfy homophily constraints")
        return None
