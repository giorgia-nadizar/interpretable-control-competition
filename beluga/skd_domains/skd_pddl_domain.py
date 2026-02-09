import os

from skdecide import DeterministicPlanningDomain

from beluga_lib.beluga_problem import BelugaProblem
from beluga_lib.problem_state import BelugaProblemState
from encoder.pddl_encoding.variant import Variant

from .skd_base_domain import SkdBaseDomain


class SkdPDDLDomain(SkdBaseDomain, DeterministicPlanningDomain):
    """Deterministic planning scikit-decide domain, based on a encoding of the actions to model the logics of
    the transition function. The methods of this class should not be used directly, but rather through the
    public methods of the domain feature class from which this class derives:
    https://airbus.github.io/scikit-decide/reference/_skdecide.domains.html#deterministicplanningdomain

    Args:
        SkdBaseDomain (_type_): Base domain
        DeterministicPlanningDomain (_type_): Compound scikit-decide class importing deterministic planning domain features
    """

    def __init__(
        self,
        beluga_problem: BelugaProblem,
        problem_name: str,
        instance_dir: os.PathLike = None,
        classic : bool = True,
        initial_state : BelugaProblemState = None
    ) -> None:
        variant = Variant()
        # variant.classic = True
        variant.classic = classic
        variant.probabilistic = False
        domain_str, problem_str = self._generate_pddl(
            beluga_problem, problem_name, variant, state=initial_state
        )
        self._create_pddl_structs(domain_str, problem_str, instance_dir)

    def _get_next_state(
        self, memory: SkdBaseDomain.T_state, action: SkdBaseDomain.T_event
    ) -> SkdBaseDomain.T_state:
        successors = self.succ_gen(
            memory.to_plado(self.cost_functions), (action.action_id, action.args)
        )
        successor = successors[0][0]
        t = self._translate_state(successor)
        c = self._get_cost_from_state(successor)
        if c != 1:
            self.transition_cost[(memory, action, t)] = c
        return t
