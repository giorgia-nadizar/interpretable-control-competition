import os

from skdecide import RLDomain, Value, Space, TransitionOutcome
from skdecide.builders.domain.observability import FullyObservable

from beluga_lib.beluga_problem import BelugaProblem
from encoder.pddl_encoding.variant import Variant
from utils.uncertainty import ArrivalSampler

from .skd_base_domain import SkdBaseDomain


class SkdSPDDLDomain(SkdBaseDomain, RLDomain, FullyObservable):
    """Reinforcement learning scikit-decide domain, based on a encoding of the actions to model the logics of
    the transition function. The methods of this class should not be used directly, but rather through the
    public methods of the domain feature class from which this class derives:
    https://airbus.github.io/scikit-decide/reference/_skdecide.domains.html#rldomain

    Important note #1: in addition to standard gymnasium-like domains, this class also provides access to the
    set of applicable actions in a given state with the `get_applicable_actions(memory: State)` method via the
    inherited RLDomain compound domain feature class. The `step(action: Action)` method will raise an exception
    if the passed action is not applicable in the current state, i.e. in the state returned by the previous call
    to the `step(action: Action)` method or to the `reset()` method. Therefore, it is important to get the set
    of applicable actions with the `get_applicable_actions(memory: State)` method in the current state before
    calling the `step(action: Action)` method.

    Important note #2: the simulator is based on a random shuffle of the ordering of Beluga flights when calling
    the `reset()` method at the beginning of each episode, from which an episode-specific PDDL file is generated
    to define the logics of the transition function in the `step(action: Action)` method. It means that different
    calls of the `step(action: Action)` from the same internal PDDL state but within different episodes will result
    in different next states (since the PDDL problems in each episode are different). In order to avoid misuse and
    misinterpretation of the internal state by the solver, we intentionally hide the internal state of the domain,
    which is also consistent with gym-like definitions of reinforcement learning domains.

    Args:
        SkdBaseDomain (_type_): Base domain
        RLDomain (_type_): Compound scikit-decide class importing reinforcement learning domain features
        FullyObservable (_type_): Domain feature class making the RL domain fully observable
    """

    def __init__(
        self,
        beluga_problem: BelugaProblem,
        problem_name: str,
        instance_dir: os.PathLike = None,
        seed: int = None,
        classic: bool = True,
    ) -> None:
        self.task = None
        self.beluga_problem = beluga_problem
        self.problem_name = problem_name
        self.instance_dir = instance_dir
        self.problem_sampler = ArrivalSampler()
        self.problem_sampler.setup()
        self.original_seed = seed
        self._current_seed = seed
        self.classic = classic

    def _state_reset(self) -> SkdBaseDomain.T_state:
        prb_seq, times = self.problem_sampler.sample_scenarios_as_problems(
            self.beluga_problem, size=1, seed=self._current_seed
        )
        # Change the RNG seed in a predictable fashion
        if self.original_seed is not None:
            self._current_seed += 1
        variant = Variant()
        variant.classic = self.classic
        variant.probabilistic = False
        domain_str, problem_str = self._generate_pddl(
            prb_seq[0], self.problem_name, variant
        )
        self._create_pddl_structs(domain_str, problem_str)
        self.state = self._translate_state(self.task.initial_state)
        return self.state

    def _state_step(self, action: SkdBaseDomain.T_event) -> TransitionOutcome[
        SkdBaseDomain.T_state,
        Value[SkdBaseDomain.T_value],
        SkdBaseDomain.T_predicate,
        SkdBaseDomain.T_info,
    ]:
        successors = self.succ_gen(
            self.state.to_plado(self.cost_functions), (action.action_id, action.args)
        )
        successor = successors[0][0]
        t = self._translate_state(successor)
        c = self._get_cost_from_state(successor)
        self.state = t
        return TransitionOutcome(
            state=self.state,
            value=Value(cost=c),
            termination=super()._is_terminal(self.state),
            info=None,
        )

    def _get_action_space_(self) -> Space[SkdBaseDomain.T_event]:
        if not hasattr(self, "action_space"):
            self._state_reset()
        return self.action_space

    def _get_observation_space_(self) -> Space[SkdBaseDomain.T_observation]:
        if not hasattr(self, "observation_space"):
            self._state_reset()
        return self.observation_space
