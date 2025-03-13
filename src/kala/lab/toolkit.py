"""Helper functions"""

from abc import ABC
from multiprocessing import Pool

import numpy as np
import pandas as pd
from pydantic import BaseModel

from kala.models import CooperationStrategy, DiscreteTwoByTwoGame
from kala.models.graphs import init_investor_graph
from kala.models.memory_rules import MemoryRuleT
from kala.utils.io import NetzDatabase


NUM_POOL_WORKERS = 12
NET_DB = NetzDatabase()


class SurvivalSpec(BaseModel):
    """Spec for a survival experiment."""

    network_name: str
    subnetwork: str | None
    memory_length: int
    memory_frac: float
    savers_share: float
    differentials: tuple[float, float]  # efficient, inefficient
    num_rounds: int
    num_games: int


class BlackSwanShockSpec(BaseModel):
    """Spec for a survival experiment that has shocks."""

    network_name: str
    subnetwork: str | None
    memory_length: int
    memory_frac: float
    savers_share: float
    differentials: tuple[float, float]  # efficient, inefficient
    num_rounds: int
    num_games: int
    shock_type: str
    shock_spread: int
    shock_round: int


class BaseSurvivalExperiment(ABC):
    """
    Base class to run experiments.

    Methods
    -------
    multigame_summary()
    single_run_history()
    """

    spec: SurvivalSpec
    num_players: int
    mem_rule: MemoryRuleT | None

    def __init__(self, spec: SurvivalSpec):
        self.spec = spec
        self._nx_graph = NET_DB.read_netzschleuder_network(spec.network_name, spec.subnetwork)
        self.num_players = self._nx_graph.number_of_nodes()

    def _init_game(self) -> DiscreteTwoByTwoGame:
        graph = init_investor_graph(
            self._nx_graph,
            savers_share=self.spec.savers_share,
            deterministic=True,  # NB: this is new behaviour
            min_specialization=1 - self.spec.differentials[1],
            update_rule=self.mem_rule,
        )

        eff, ineff = self.spec.differentials
        coop = CooperationStrategy(
            stochastic=True,
            differential_efficient=eff,
            differential_inefficient=ineff,
        )

        return DiscreteTwoByTwoGame(graph, coop)

    # pylint: disable=unused-argument
    def _single_game_summary(self, dummy_arg) -> tuple[int, int]:
        savers = np.zeros(self.spec.num_rounds, dtype=int)
        game = self._init_game()

        for i in range(self.spec.num_rounds):
            n_savers = game.get_num_savers()
            savers[i] = n_savers

            if n_savers in [0, self.num_players]:
                return n_savers, i

            game.play_round()

        return savers.min(), savers.argmin()

    def multigame_summary(self) -> np.ndarray:
        """
        Track the min of savers and the time when it is achieved across multiple games.

        """
        empty_iterables = [[]] * self.spec.num_games  # type: ignore
        with Pool(NUM_POOL_WORKERS) as p:
            out = list(p.imap_unordered(self._single_game_summary, empty_iterables))

        return np.array(out)

    def single_run_history(self, norm: bool = True) -> pd.DataFrame:
        """
        Run `num_rounds` iterations of the game and store the results in a DataFrame.

        Parameters
        ----------
        norm : bool, optional
            Whether to normalise the wealth and number of savers (default is True).

        Returns
        -------
        pd.DataFrame

        """
        state_variables = []
        game = self._init_game()

        for i in range(self.spec.num_rounds):
            svars = [
                float(game.get_total_wealth()),
                game.get_num_savers(),
                game.get_gini(),
            ]
            state_variables.append(svars)

            game.play_round()

            # subclass BlackSwanShockExperiment will have shock attr
            if hasattr(self, "shock") and i == self.spec.shock_round:
                for _ in range(self.spec.shock_spread):
                    self.shock.apply(game)

        out = pd.DataFrame(state_variables, columns=["wealth", "savers", "gini"])

        if norm:
            N = self.num_players
            out["wealth"] /= N
            out["savers"] /= N

        return out
