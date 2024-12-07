"""Helper functions"""

from abc import ABC, abstractmethod
from multiprocessing import Pool

import numpy as np
import pandas as pd
from pydantic import BaseModel

from kala.models import DiscreteTwoByTwoGame
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

    def __init__(self, spec: SurvivalSpec):
        self.spec = spec
        self._nx_graph = NET_DB.read_netzschleuder_network(spec.network_name, spec.subnetwork)
        self.num_players = self._nx_graph.number_of_nodes()

    @abstractmethod
    def _init_game(self) -> DiscreteTwoByTwoGame:
        pass

    # pylint: disable=unused-argument
    def _single_game_summary(self, dummy_arg) -> tuple[int, int]:
        savers = np.zeros(self.spec.num_rounds, dtype=int)
        game = self._init_game()

        for i in range(self.spec.num_rounds):
            n_savers = game.get_num_savers()
            savers[i] = n_savers

            if n_savers == self.num_players:
                return self.num_players, i

            if n_savers == 0:
                savers = savers[: i + 1]
                break

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

        # if shock_names is None:
        #     shock_names = []

        # if shock_rounds is None:
        #     shock_rounds = []

        # shock_iterator = zip(filter(None, shock_names), filter(None, shock_rounds))

        game = self._init_game()

        for _ in range(self.spec.num_rounds):
            svars = [
                float(game.get_total_wealth()),
                game.get_num_savers(),
                game.get_gini(),
            ]
            state_variables.append(svars)

            # if i == shock_time:
            #     shock_handle = getattr(shocks, shock_name, None)

            #     if shock_handle is not None:
            #         # print(f"applying shock {shock_name} at t={shock_time}")
            #         shock = shock_handle()
            #         shock.apply(game)

            #     try:
            #         shock_name, shock_time = next(shock_iterator)
            #     except StopIteration:
            #         shock, shock_time = None, None

            game.play_round()

        out = pd.DataFrame(state_variables, columns=["wealth", "savers", "gini"])

        if norm:
            N = self.num_players
            out["wealth"] /= N
            out["savers"] /= N

        return out
