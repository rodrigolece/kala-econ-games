"""Survival experiments."""

from kala.lab.toolkit import BaseSurvivalExperiment, SurvivalSpec
from kala.models import FractionMemoryRule


class MemoryThresholdExperiment(BaseSurvivalExperiment):
    """
    The game is initialised with a fixed share of savers and the parameter changing is
    the memory threshold.

    """

    def __init__(self, spec: SurvivalSpec):
        super().__init__(spec)
        self.mem_rule = FractionMemoryRule(spec.memory_length, fraction=spec.memory_frac)


class SaversShareExperiment(BaseSurvivalExperiment):
    """
    The game is initialised with a fixed 0.5 memory threshold and the parameter changing is
    the share of savers.

    """

    def __init__(self, spec: SurvivalSpec):
        super().__init__(spec)
        self.mem_rule = FractionMemoryRule(
            spec.memory_length,
            fraction=0.5,  # self.spec.memory_frac is ignored
        )


# TODO: remove below
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
