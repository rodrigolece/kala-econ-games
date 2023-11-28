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
    _addition_order: Mapping[str, int]

    @abstractmethod
    def get_node(self, nid: int | str) -> AgentT:
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
    """Unweighted, undirected graph built on top of NetworkX."""

    _nodes: Sequence[AgentT | None]

    def __init__(self, graph: nx.Graph, nodes: Sequence[AgentT]):
        self._graph = graph
        self._nodes = []
        self._addition_order = {}

        # NB: nodes is relied upon and cannot be None in this implementation
        for i, n in enumerate(nodes):
            self._nodes.append(n)
            nid = getattr(n, "uuid", i)
            self._addition_order[nid] = i

    def _get_pos_from_node(self, node: AgentT | int | str) -> int:
        if hasattr(node, "uuid"):
            node = self._addition_order[getattr(node, "uuid")]
        elif isinstance(node, str):
            node = self._addition_order[node]
        elif isinstance(node, int):
            pass
        else:
            raise TypeError(f"Invalid type for node: {type(node)}")
        return node

    def get_node(self, nid: int | str) -> AgentT:
        pos: int = self._get_pos_from_node(nid)  # type: ignore
        return self._nodes[pos]

    def get_neighbours(self, node: AgentT | int | str) -> Sequence[AgentT]:
        pos = self._get_pos_from_node(node)
        _neighs = self._graph.neighbors(pos)
        return [self.get_node(i) for i in _neighs]
