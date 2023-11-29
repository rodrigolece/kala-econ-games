"""Module defining the interface for the underlying graphs."""

from abc import ABC, abstractmethod
from typing import Any, Generic, Sequence, TypeVar

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
    add_node()
    remove_node()
    add_edge()
    remove_edge()

    """

    _graph: Any
    _nodes: list[AgentT]
    _addition_order: dict[str, int]

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

    @abstractmethod
    def add_node(self, node: AgentT) -> bool:
        """Add the node to the graph."""

    @abstractmethod
    def remove_node(self, node: AgentT | int | str) -> bool:
        """Remove the node from the graph."""

    @abstractmethod
    def add_edge(self, u: AgentT | int | str, v: AgentT | int | str) -> bool:
        """Add an edge between nodes u and v (the nodes should already be in the graph)."""

    @abstractmethod
    def remove_edge(self, u: AgentT | int | str, v: AgentT | int | str) -> bool:
        """Remove the edge between nodes u and v."""


GraphT = TypeVar("GraphT", bound=BaseGraph)
"""Used to refer to BaseGraph as well as its subclasses."""


class SimpleGraph(BaseGraph, Generic[AgentT]):
    """Unweighted, undirected graph built on top of NetworkX."""

    _nodes: list[AgentT | None]

    def __init__(self, graph: nx.Graph, nodes: Sequence[AgentT]):
        self._graph = graph
        self._nodes = []
        self._addition_order = {}

        # NB: nodes is relied upon and cannot be None in this implementation
        for i, n in enumerate(nodes):
            self._nodes.append(n)
            nid = getattr(n, "uuid", str(i))
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

    def num_nodes(self) -> int:
        # NB: this is specific to NetworkX because we allow None so as to not invalidate
        # the self._addition_order
        return len(list(filter(None, self._nodes)))

    def get_node(self, nid: int | str) -> AgentT | None:
        # FIXME: return could be node if the node is removed
        pos = self._get_pos_from_node(nid)  # type: ignore
        return self._nodes[pos]

    def get_neighbours(self, node: AgentT | int | str) -> Sequence[AgentT]:
        pos = self._get_pos_from_node(node)
        _neighs = self._graph.neighbors(pos)
        return list(filter(None, (self.get_node(i) for i in _neighs)))

    def add_node(self, node: AgentT) -> bool:
        pos = len(self._nodes)  # no +1 bcs python is 0-indexed

        if getattr(node, "uuid", None) in self._addition_order:
            # node is already in the graph (networkx does not raise an error)
            return False

        self._graph.add_node(pos)
        self._nodes.append(node)
        self._addition_order[getattr(node, "uuid", str(pos))] = pos

        return True

    def remove_node(self, node: AgentT | int | str) -> bool:
        pos = self._get_pos_from_node(node)
        try:
            self._graph.remove_node(pos)
            # NB: networkx does not invalidate node labels so we cannot change self._addition_order
            self._nodes[pos] = None

            return True
        except nx.NetworkXError:
            return False

    def add_edge(self, u: AgentT | int | str, v: AgentT | int | str) -> bool:
        try:
            pos_u = self._get_pos_from_node(u)
            pos_v = self._get_pos_from_node(v)

        except KeyError:  # at least one of the nodes is not in the graph
            return False

        if self._graph.has_edge(pos_u, pos_v):
            return False

        if pos_u == pos_v:  # self-loops are not allowed
            return False

        self._graph.add_edge(pos_u, pos_v)
        return True

    def remove_edge(self, u: AgentT | int | str, v: AgentT | int | str) -> bool:
        pos_u = self._get_pos_from_node(u)
        pos_v = self._get_pos_from_node(v)
        try:
            self._graph.remove_edge(pos_u, pos_v)
            return True
        except nx.NetworkXError:
            return False
