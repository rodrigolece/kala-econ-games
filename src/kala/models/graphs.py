"""Module defining the interface for the underlying graphs."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Iterable, Sequence, TypeVar
from warnings import warn

import networkx as nx
import numpy as np
from numpy.random import Generator

from kala.models.agents import AgentT
from kala.utils.stats import choice


class BaseGraph(ABC, Generic[AgentT]):
    """
    Our graph interface independent of the library used for implementation.

    Methods
    -------
    get_node()
    get_nodes()
    num_nodes()
    num_edges()
    get_neighbours()
    add_node()
    remove_node()
    add_edge()
    remove_edge()
    select_random_node()
    select_random_neighbour()
    edges()
    get_property()
    get_trait()

    """

    _graph: Any
    _nodes: list[AgentT]
    _addition_order: dict[str, int]

    def __str__(self) -> str:
        agent_type_str = f"[{type(self._nodes[0]).__name__}]" if self._nodes else ""
        n, e = self.num_nodes(), self.num_edges()
        return f"{self.__class__.__name__}{agent_type_str}(num_nodes={n}, num_edges={e})"

    def __repr__(self) -> str:
        return f"<{str(self)}>"

    @abstractmethod
    def get_node(self, nid: int | str) -> AgentT:
        """Get the node object given its id."""

    def get_nodes(self):
        """Get all the nodes in the graph."""
        return self._nodes

    def num_nodes(self) -> int:
        """Return the number of nodes in the graph."""
        return len(self._nodes)

    @abstractmethod
    def num_edges(self) -> int:
        """Return the number of edges in the graph."""

    @abstractmethod
    def get_neighbours(self, node: AgentT | int | str) -> Sequence[AgentT]:
        """Get the neighbourhood of a given node."""

    def get_neighbors(self, *args, **kwargs) -> Sequence[AgentT]:
        """Alias for the method get_neighbours."""
        return self.get_neighbours(*args, **kwargs)

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

    def select_random_node(self, rng: Generator | int | None = None) -> AgentT:
        """Select a random node in the graph."""
        return choice(self.get_nodes(), rng=rng)

    def select_random_neighbour(
        self,
        node: AgentT | int | str,
        rng: Generator | int | None = None,
    ) -> AgentT | None:
        """
        Select a random neighbour of a node in the graph.

        If the nodes have homophily then the neighbours are chosen with probability
        proportional to their homophily.

        Parameters
        ----------
        node : AgentT | int | str
            The node for which to select a neighbour.
        rng : Generator | int | None, optional
            The random number generator to use, by default None.

        Returns
        -------
        AgentT | None
            If the node is disconnected or the homophily constraints cannot be satisfied,
            then None is returned.

        """
        if isinstance(node, int | str):
            node = self.get_node(node)

        neighs = self.get_neighbours(node)

        if len(neighs) == 0:
            warn("selected player does not have any neighbours")
            return None

        if (hom := node.get_trait("homophily")) is not None:
            saver_trait = node.get_trait("is_saver")
            ps = [hom if n.get_trait("is_saver") == saver_trait else 1 - hom for n in neighs]
            # the `choice` function below takes care of the normalisation
        else:
            ps = None

        try:
            return choice(neighs, p=ps, rng=rng)

        except ValueError:
            warn("cannot satisfy homophily constraint for selected player")
            return None

    def select_random_neighbor(self, *args, **kwargs) -> AgentT | None:
        """Alias for the method select_random_neighbour."""
        return self.select_random_neighbour(*args, **kwargs)

    # @abstractmethod
    # def nodes(fun: Callable | None = None) -> Iterable:
    #     """Get an iterator on the nodes, optionally calling a function."""

    @abstractmethod
    def edges(self, fun: Callable | None = None) -> Iterable:
        """Get an iterator on the edges, optionally calling a function."""

    def get_property(self, property_name: str) -> list[Any]:
        """Get the values corresponding to a given property of all nodes."""
        return [n.get_property(property_name) for n in self.get_nodes()]

    def get_trait(self, trait_name: str) -> list[Any]:
        """Get the node values corresponding to a given trait of all nodes."""
        return [n.get_trait(trait_name) for n in self.get_nodes()]


GraphT = TypeVar("GraphT", bound=BaseGraph)
"""Used to refer to BaseGraph as well as its subclasses."""


class SimpleGraph(BaseGraph, Generic[AgentT]):
    """Unweighted, undirected graph built on top of NetworkX."""

    _nodes: list[AgentT | None]

    def __init__(self, graph: nx.Graph, nodes: Sequence[AgentT]):
        self._graph = graph.copy()  # to avoid corruption due to the original graph being modified
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
        elif isinstance(node, int | np.integer):
            pass
        else:
            raise TypeError(f"Invalid type for node: {type(node)}")
        return node

    def get_node(self, nid: int | str) -> AgentT | None:
        pos = self._get_pos_from_node(nid)  # type: ignore
        return self._nodes[pos]

    def get_nodes(self):
        return list(filter(None, self._nodes))

    def num_nodes(self) -> int:
        # NB: this is specific to NetworkX because we allow None so as to not invalidate
        # the self._addition_order
        return len(list(filter(None, self._nodes)))

    def num_edges(self) -> int:
        return nx.number_of_edges(self._graph)

    def get_neighbours(self, node: AgentT | int | str) -> list[AgentT]:
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

    def edges(self, fun: Callable | None = None) -> Iterable:
        fun = fun or (lambda x: x)

        for e in self._graph.edges:  # NB: this is specific to NetworkX
            yield fun(e)
