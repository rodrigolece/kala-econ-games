"""Module defining the interface for the underlying graphs."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, Sequence, TypeVar

import networkx as nx
from models.agents import InvestorAgent  # for testing


@dataclass
class Node:
    id: int | str
    node: Any


class BaseGraph(ABC):
    """
    Our graph interface independent of the library used for implementation.

    """

    _graph: Any
    _nodes: Sequence[Node]

    @abstractmethod
    def get_node(self, id: int | str) -> Node:
        pass

    @abstractmethod
    def get_neighbours(self, node: int | str) -> Iterable[int | str]:
        """Get the neighbourhood of a given node."""

    def get_neighbors(self, node: int | str) -> Iterable[int | str]:
        """Alias of the method get_neighbours."""
        return self.get_neighbours(node)


class SimpleGraph(BaseGraph):
    def __init__(self, graph: nx.Graph, nodes: Sequence[Any] | None = None):
        self._graph = graph
        self._nodes = []
        if nodes:
            for i, n in enumerate(nodes):
                self._nodes.append(Node(i, n))

    def get_node(self, id: int | str):
        if isinstance(id, str):
            raise NotImplementedError("will implement in the future")

        return self._nodes[id].node

    def get_neighbours(self, id: int | str):
        _neighs = self._graph.neighbors(id)
        return [self.get_node(i) for i in _neighs]


GraphType = TypeVar("GraphType", bound=BaseGraph)
"""Used to refer to BaseGraph as well as its subclasses."""


if __name__ == "__main__":
    num_nodes = 10

    # A list of InvestorAgents
    nodes = [InvestorAgent(is_saver=True, group=0) for _ in range(num_nodes)]

    g = nx.barabasi_albert_graph(num_nodes, 8, seed=0)
    G = SimpleGraph(g, nodes=nodes)

    n = G.get_node(0)
    assert isinstance(n, InvestorAgent)
    neighs = G.get_neighbours(0)
    assert isinstance(neighs[0], InvestorAgent)

    for node in range(1, num_nodes):
        neighs = list(G.get_neighbours(node))
        print(f"{node}: {len(neighs)}")
