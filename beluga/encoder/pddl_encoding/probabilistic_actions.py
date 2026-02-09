# from beluga_lib.problem_def import BelugaProblem
from beluga_lib.beluga_problem import BelugaProblem

from ..pddl import PDDLNumericFluent, PDDLNumericValue, PDDLParam
from ..pddl.pddl_predicate_def import PDDLPredicateDef
from ..pddl.pddl_probabilistic_action import (
    PDDLProbabilisticAction,
    ProbabilisticOutcome,
)
from ..pddl.type import Type
from .feature_action import FeatureAction
from .variant import Variant


class ProceedToNextBeluga(FeatureAction):

    def __init__(
        self,
        variant: Variant,
        beluga_problem: BelugaProblem,
        types: dict[str:Type],
        constants: dict[str:PDDLParam],
        predicates: dict[str:PDDLPredicateDef],
        functions: dict[str:PDDLPredicateDef],
    ) -> None:
        super().__init__(variant, types, constants, predicates, functions)

        self.problem = beluga_problem

        self.name = "complete-beluga"

        self.loc_t = self.register_type("location")
        self.beluga_t = self.register_type("beluga", self.loc_t)
        self.jig_t = self.register_type("jig", self.loc_t)
        self.type_t = self.register_type("type")
        self.slot_t = self.register_type("slot")

        self.beluga = PDDLParam("?b", self.beluga_t)
        self.next_beluga = PDDLParam("?nb", self.beluga_t)
        self.jig = PDDLParam("?j", self.jig_t)
        self.jig_type = PDDLParam("?jt", self.type_t)
        self.slot = PDDLParam("?s", self.slot_t)

        self.dummy_jig = self.register_constant("dummy-jig", self.jig_t)
        self.dummy_type = self.register_constant("dummy-type", self.type_t)
        self.dummy_slot = self.register_constant("dummy-slot", self.slot_t)

        self.in_phase = self.register_predicate("processed-flight", self.beluga)
        self.to_unload = self.register_predicate("to_unload", self.jig, self.beluga)
        self.to_load = self.register_predicate(
            "to_load", self.jig_type, self.slot, self.beluga
        )

        self.max_hist_len: int = max((len(h) for h in beluga_problem.tt_last))
        self.transition_tables: dict[tuple[str], list[tuple[str, float]]] = {}
        assert len(self.problem.tt_last) == len(self.problem.tt_next) and len(
            self.problem.tt_next
        ) == len(self.problem.tt_prob)
        for i, hist in enumerate(self.problem.tt_last):
            j = None
            for j, flight in enumerate(hist):
                if flight is not None:
                    j -= 1
                    break
            j += 1
            assert j is not None
            assert all((f is not None for f in hist[j:]))
            self.transition_tables.setdefault(hist[j:], []).append(
                (self.problem.tt_next[i], self.problem.tt_prob[i])
            )
        self.belugas = tuple(
            PDDLParam(f"?b{i}", self.beluga_t) for i in range(self.max_hist_len)
        )
        self.flight_history = self.register_predicate("flight-history", *self.belugas)

        self.done_processing = self.register_predicate("done-processing", self.beluga)

        for flight in beluga_problem.flights:
            self.register_constant(flight.name, self.beluga_t)
        for i in range(self.max_hist_len):
            self.register_constant(f"dummy-beluga-{i+1}", self.beluga_t)

    def create_PDDL_action(self) -> list[PDDLProbabilisticAction]:
        result = []
        for history in self.transition_tables:
            extended_history = (
                tuple(
                    f"dummy-beluga-{i+1}"
                    for i in reversed(range(self.max_hist_len - len(history)))
                )
                + history
            )
            beluga = PDDLParam(extended_history[-1], self.beluga_t)
            a = PDDLProbabilisticAction(self.name + "-" + "-".join(extended_history))
            a.add_precondition(self.in_phase.inst(beluga))
            a.add_precondition(self.to_unload.inst(self.dummy_jig, beluga))
            a.add_precondition(
                self.to_load.inst(self.dummy_type, self.dummy_slot, beluga)
            )
            a.add_precondition(
                self.flight_history.inst(
                    *(PDDLParam(b, self.beluga_t) for b in extended_history)
                )
            )
            for next_b, prob in self.transition_tables[history]:
                out = ProbabilisticOutcome()
                out.add_condition(
                    self.done_processing.negated_inst(PDDLParam(next_b, self.beluga_t))
                )
                out.add_effect(self.in_phase.negated_inst(beluga))
                out.add_effect(self.done_processing.inst(beluga))
                out.add_effect(
                    self.flight_history.negated_inst(
                        *(PDDLParam(b, self.beluga_t) for b in extended_history)
                    )
                )
                out.add_effect(self.in_phase.inst(PDDLParam(next_b, self.beluga_t)))
                out.add_effect(
                    self.flight_history.inst(
                        *(PDDLParam(b, self.beluga_t) for b in extended_history[1:]),
                        PDDLParam(next_b, self.beluga_t),
                    )
                )
                out.add_effect(
                    PDDLNumericFluent(
                        "increase", self.total_cost.inst(), PDDLNumericValue(1)
                    )
                )
                out.set_probability(prob)
                a.add_outcome(out)
            result.append(a)
        return result
