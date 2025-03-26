"""Module defining agent strategies."""

from typing import Callable, Generic, Protocol

import networkx as nx
import numpy as np

from kala.models.agents import Agent, SaverProperties, SaverTraits
from kala.models.data import Properties, Traits
from kala.models.graphs import AgentPlacement, get_neighbours


class MatchingStrategy(Generic[Traits, Properties]):
    def select_matches(
        self,
        placements: AgentPlacement,
        graph: nx.Graph,
    ) -> list[list[Agent[Traits, Properties]]]:
        rng = np.random.default_rng()
        num_nodes = graph.number_of_nodes()
        selection = rng.choice(graph, size=num_nodes // 2)

        out = []

        for node in selection:
            if (agent := placements.get_agent(node)) is None:
                continue

            neighs = get_neighbours(agent, graph, placements)
            if neighs is None or neighs == []:
                continue

            if (opponent := rng.choice(neighs)) is None:  # type: ignore
                continue

            out.append([agent, opponent])

        return out


class PayoffStrategy(Generic[Traits, Properties], Protocol):
    """
    Initialize a cooperation strategy.

    Attributes
    ----------
    stochastic : bool, optional
        Whether to use a stochastic payoff matrix, by default True.
    payoff_matrix : dict[tuple[str, str], tuple[float, float]]
        A dictionary mapping types of agent traits to numerical payoffs.

    """

    stochastic: bool = True
    payoff_matrix: dict[tuple[str, str], tuple[float, float]]

    def calculate_payoff(self, agents: list[Agent[Traits, Properties]]) -> list[float]:
        """A realization of the payoff for a strategy."""


class SaverCooperationPayoffStrategy(PayoffStrategy[SaverTraits, SaverProperties]):
    """
    A strategy that models cooperation between Saver agents.

    Two agents that are savers will have a higher payoff (on expectation) than in all other cases,
    but a saver that encounters a non-saver will see a worse outcome than the non-saver.

    """

    def __init__(
        self,
        stochastic: bool = True,
        differential_inefficient: float = 0.1,
        differential_efficient: float = 0.15,
        dist_sigma_func: Callable = lambda x: x,
    ):
        """
        Initialize a cooperation strategy.

        Parameters
        ----------
        stochastic : bool, optional
            Whether to use a stochastic payoff matrix, by default True.
        differential_inefficient : float, optional
            The amount by which a saver is less efficient when encountering non-savers,
            by default 0.1.
        differential_efficient : float, optional
            The amount by which a saver is more efficient when encountering another saver,
            by default 0.15.
        dist_sigma_func : Callable, optional
            A function that maps specializations (efficient and inefficient) to the
            standard deviation of the lognormal distribution. By default, the function
            is the identity function.

        Raises
        ------
        ValueError
            If any of the parameters are invalid.

        """
        # Checks

        # Initialize
        self.stochastic = stochastic

        payoff_ss = 1 + differential_efficient
        payoff_sn = 1 - differential_inefficient

        self.payoff_matrix = {
            ("saver", "saver"): (payoff_ss, payoff_ss),
            ("saver", "non-saver"): (payoff_sn, 1),
            ("non-saver", "saver"): (1, payoff_sn),
            ("non-saver", "non-saver"): (1, 1),
        }

        self._saver_encoding = {True: "saver", False: "non-saver"}
        # used to map the trait is_saver to the payoff matrix entries

        # We prescribe the variance of the RV
        var_ss = dist_sigma_func(payoff_ss)
        var_sn = dist_sigma_func(payoff_sn)

        # We invert an equation to find the param of the log-normals
        param_var_ss = np.log(1 + np.sqrt(1 + 4 * var_ss)) - np.log(2)
        param_var_sn = np.log(1 + np.sqrt(1 + 4 * var_sn)) - np.log(2)

        self._sigma = {
            ("saver", "saver"): np.sqrt(param_var_ss),
            ("saver", "non-saver"): np.sqrt(param_var_sn),
            ("non-saver", "saver"): np.sqrt(param_var_sn),
            ("non-saver", "non-saver"): 1,  # dummy (ignored) value
        }
        # TODO: more elegant solution would be to accept initialized distribution that
        # doesn't need parameters and is ready to return random numbers

    def calculate_payoff(self, agents: list[Agent[SaverTraits, SaverProperties]]) -> list[float]:
        """A realization of the payoff for a strategy."""

        if len(agents) != 2:
            raise ValueError("expected exactly two agents")

        saver_traits: tuple[str, str] = tuple(
            self._saver_encoding[ag.properties.is_saver] for ag in agents
        )  # type: ignore
        specs = np.asarray([ag.traits.min_specialization for ag in agents])
        payoffs = np.asarray(self.payoff_matrix[saver_traits]) + specs

        if self.stochastic:
            rng = np.random.default_rng()
            draw = rng.lognormal(mean=0, sigma=self._sigma[saver_traits])
            # below ignores the dummy draw for (non-saver, non-saver)
            payoffs *= [draw if ag.properties.is_saver else 1 for ag in agents]

        return payoffs
