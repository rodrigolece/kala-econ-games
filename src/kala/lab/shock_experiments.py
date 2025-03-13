"""Shock experiments."""

from multiprocessing import Pool

import numpy as np

from kala.lab.toolkit import (
    NUM_POOL_WORKERS,
    BaseSurvivalExperiment,
    BlackSwanShockSpec,
)
from kala.models import FractionMemoryRule, shocks


class BlackSwanShockExperiment(BaseSurvivalExperiment):
    spec: BlackSwanShockSpec
    num_players: int
    shock: shocks.ShockT

    def __init__(self, spec: BlackSwanShockSpec):
        if spec.shock_type not in ("AddRandomEdge", "RemoveRandomEdge", "SwapRandomEdge"):
            raise NotImplementedError

        super().__init__(spec)
        self.mem_rule = FractionMemoryRule(spec.memory_length, fraction=spec.memory_frac)
        shock_handle = getattr(shocks, spec.shock_type)
        self.shock = shock_handle()

    def _single_game_savers(self, dummy_arg) -> np.ndarray:
        savers = np.zeros(self.spec.num_rounds, dtype=int)
        game = self._init_game()

        for i in range(self.spec.num_rounds):
            n_savers = game.get_num_savers()
            savers[i] = n_savers

            game.play_round()

            if i == self.spec.shock_round:
                for _ in range(self.spec.shock_spread):
                    self.shock.apply(game)

        return savers

    def multigame_savers(self) -> np.ndarray:
        empty_iterables = [[]] * self.spec.num_games  # type: ignore
        with Pool(NUM_POOL_WORKERS) as p:
            out = list(p.imap_unordered(self._single_game_savers, empty_iterables))

        return np.vstack(out).T

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
            if i == self.spec.shock_round:
                for _ in range(self.spec.shock_spread):
                    self.shock.apply(game)

        return savers.min(), savers.argmin()
