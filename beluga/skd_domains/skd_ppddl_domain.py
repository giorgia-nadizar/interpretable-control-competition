import os

from skdecide import GoalMDPDomain, DiscreteDistribution

from beluga_lib.beluga_problem import BelugaProblem
from encoder.pddl_encoding.variant import Variant

from .skd_base_domain import SkdBaseDomain


class SkdPPDDLDomain(SkdBaseDomain, GoalMDPDomain):
    """Probabilistic planning scikit-decide domain, based on a encoding of the actions to model the logics of
    the transition function. The methods of this class should not be used directly, but rather through the
    public methods of the domain feature class from which this class derives:
    https://airbus.github.io/scikit-decide/reference/_skdecide.domains.html#goalmdpdomain

    Args:
        SkdBaseDomain (_type_): Base domain
        GoalMDPDomain (_type_): Compound scikit-decide class importing goal MDP domain features
    """

    def __init__(
        self,
        beluga_problem: BelugaProblem,
        problem_name: str,
        instance_dir: os.PathLike = None,
    ) -> None:
        variant = Variant()
        variant.classic = True
        variant.probabilistic = True
        domain_str, problem_str = self._generate_pddl(
            beluga_problem, problem_name, variant
        )
        self._create_pddl_structs(domain_str, problem_str, instance_dir)

    def _get_next_state_distribution(
        self, memory: SkdBaseDomain.T_state, action: SkdBaseDomain.T_event
    ) -> DiscreteDistribution[SkdBaseDomain.T_state]:
        successors = self.succ_gen(
            memory.to_plado(self.cost_functions), (action.action_id, action.args)
        )
        ts = [(self._translate_state(succ), float(prob)) for succ, prob in successors]
        for i in range(len(ts)):
            c = self._get_cost_from_state(successors[i][0])
            if c != 1:
                self.transition_cost[(memory, action, ts[i])] = c
        return DiscreteDistribution(ts)
