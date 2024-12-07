"""Survival experiments."""

from kala.lab.toolkit import BaseSurvivalExperiment, SurvivalSpec
from kala.models import CooperationStrategy, DiscreteTwoByTwoGame, FractionMemoryRule
from kala.models.graphs import init_investor_graph


class MemoryThresholdExperiment(BaseSurvivalExperiment):
    """
    The game is initialised with 50% of savers and the parameter changing is the memory threshold.

    """

    def __init__(self, spec: SurvivalSpec):
        super().__init__(spec)
        self._mem_rule = FractionMemoryRule(spec.memory_length, fraction=spec.memory_frac)

    def _init_game(self) -> DiscreteTwoByTwoGame:
        graph = init_investor_graph(
            self._nx_graph,
            savers_share=0.5,  # self.spec.savers_share is ignored
            min_specialization=1 - self.spec.differentials[1],
            update_rule=self._mem_rule,
        )

        eff, ineff = self.spec.differentials
        coop = CooperationStrategy(
            stochastic=True,
            differential_efficient=eff,
            differential_inefficient=ineff,
        )

        return DiscreteTwoByTwoGame(graph, coop)


class SaversShareExperiment(BaseSurvivalExperiment):
    """
    The game is initialised with a fixed 0.5 memory threshold and the parameter changing is
    the share of savers.

    """

    def __init__(self, spec: SurvivalSpec):
        super().__init__(spec)
        self._mem_rule = FractionMemoryRule(
            spec.memory_length,
            fraction=0.5,  # self.spec.memory_frac is ignored
        )

    def _init_game(self) -> DiscreteTwoByTwoGame:
        graph = init_investor_graph(
            self._nx_graph,
            savers_share=self.spec.savers_share,
            min_specialization=1 - self.spec.differentials[1],
            update_rule=self._mem_rule,
        )

        eff, ineff = self.spec.differentials
        coop = CooperationStrategy(
            stochastic=True,
            differential_efficient=eff,
            differential_inefficient=ineff,
        )

        return DiscreteTwoByTwoGame(graph, coop)


if __name__ == "__main__":
    spec = SurvivalSpec(
        network_name="student_cooperation",
        subnetwork=None,
        memory_length=10,
        memory_frac=0.5,  # will be ignored
        savers_share=0.1,
        differentials=(0.1, 0.15),  # efficient, inefficient
        num_rounds=800,
        num_games=1,
    )

    exp = SaversShareExperiment(spec)
    df = exp.single_run_history(norm=False)
