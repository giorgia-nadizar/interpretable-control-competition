from collections.abc import Iterable

from .pddl_action import PDDLAction
from .pddl_literal import PDDLLiteral


class ConditionalEffect:
    def __init__(
        self, condition: Iterable[PDDLLiteral], effects: Iterable[PDDLLiteral]
    ):
        self.condition: list[PDDLLiteral] = list(condition)
        self.effects: list[PDDLLiteral] = list(effects)

    def add_condition(self, l: PDDLLiteral):
        self.condition.append(l)

    def add_effect(self, l: PDDLLiteral):
        self.effects.append(l)

    def to_pddl(self) -> str:
        res = []
        if len(self.condition) > 0:
            res.append(
                "(when (and\n\t\t\t\t\t"
                + "\n\t\t\t\t\t".join(cond.to_pddl() for cond in self.condition)
                + ")\n\t\t\t\t\t"
            )
        res.append(
            "(and\n\t\t\t\t\t"
            + "\n\t\t\t\t\t".join(effect.to_pddl() for effect in self.effects)
            + ")"
        )
        if len(self.condition) > 0:
            res.append(")")
        return "".join(res)


class ProbabilisticOutcome:
    def __init__(self):
        self.probability: float = 0
        self.effect: ConditionalEffect = ConditionalEffect([], [])

    def add_effect(self, l: PDDLLiteral):
        self.effect.add_effect(l)

    def add_condition(self, l: PDDLLiteral):
        self.effect.add_condition(l)

    def set_probability(self, probability: float):
        self.probability = probability

    def to_pddl(self) -> str:
        return f"{format(self.probability, '.4g')} {self.effect.to_pddl()}"


class ProbabilisticEffect:
    def __init__(self):
        self.outcomes: list[ProbabilisticOutcome] = []

    def add_outcome(self, outcome: ProbabilisticOutcome):
        self.outcomes.append(outcome)

    def to_pddl(self) -> str:
        return (
            "(probabilistic\n\t\t\t\t"
            + "\n\t\t\t\t".join((o.to_pddl() for o in self.outcomes))
            + ")"
        )


class PDDLProbabilisticAction(PDDLAction):
    def __init__(self, name: str):
        super().__init__(name)
        self.effects: list[ProbabilisticEffect] = [ProbabilisticEffect()]

    def add_outcome(self, outcome: ProbabilisticOutcome):
        self.effects[0].add_outcome(outcome)
