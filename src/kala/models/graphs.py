"""Module defining the interface for the underlying graphs."""

from abc import ABC, abstractmethod
from typing import Any, Generic, Mapping, Sequence, TypeVar

import networkx as nx

from kala.models.agents import AgentT


class BaseGraph(ABC, Generic[AgentT]):
    """
    Our graph interface independent of the library used for implementation.

    Methods
    -------
    get_node()
    get_neighbours()
    num_nodes()

    """

    _graph: Any
    _nodes: Sequence[AgentT]
    _addition_order: Mapping[int | str, int]

    @abstractmethod
    def get_node(self, nid: int | str, by_pos: bool = False) -> AgentT:
        """Get the node object given its id."""

    @abstractmethod
    def get_neighbours(self, node: AgentT | int | str) -> Sequence[AgentT]:
        """Get the neighbourhood of a given node."""

    def get_neighbors(self, node: AgentT | int | str) -> Sequence[AgentT]:
        """Alias of the method get_neighbours."""
        return self.get_neighbours(node)

    def num_nodes(self) -> int:
        """Return the number of nodes in the graph."""
        return len(self._nodes)


GraphT = TypeVar("GraphT", bound=BaseGraph)
"""Used to refer to BaseGraph as well as its subclasses."""


class SimpleGraph(BaseGraph):
    """Unweighted, undirected graph built using a NetworkX graph."""

    def __init__(self, graph: nx.Graph, nodes: Sequence[AgentT] | None = None):
        self._graph = graph
        self._nodes = []
        self._addition_order = {}

        if nodes:
            for i, node in enumerate(nodes):
                self._nodes.append(node)
                nid = getattr(node, "uuid", i)
                self._addition_order[nid] = i

    # pylint: disable=unused-argument
    def get_node(self, nid: int | str, by_pos: bool = False, dummy: AgentT | None = None) -> AgentT:
        pos: int = nid if by_pos else self._addition_order[nid]  # type: ignore
        return self._nodes[pos]

    def get_neighbours(self, node: AgentT | int | str) -> Sequence[AgentT]:
        nid = getattr(node, "uuid") if hasattr(node, "uuid") else node
        pos = self._addition_order[nid]
        _neighs = self._graph.neighbors(pos)
        return [self.get_node(i, by_pos=True) for i in _neighs]
