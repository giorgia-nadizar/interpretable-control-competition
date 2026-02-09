import copy  # TODO temporarily added to avoid constructing the pddl string twice
import os
from tempfile import TemporaryDirectory
from typing import Any, Iterable, Optional

from beluga_lib.beluga_problem import BelugaProblem
from beluga_lib.problem_state import BelugaProblemState
from encoder.pddl_encoding import DomainEncoding, encode
from encoder.pddl_encoding.variant import Variant
from plado.parser import parse_and_normalize
from plado.semantics.applicable_actions_generator import ApplicableActionsGenerator
from plado.semantics.goal_checker import GoalChecker
from plado.semantics.successor_generator import SuccessorGenerator
from plado.semantics.task import State as PladoState
from plado.semantics.task import Task
from plado.utils import Float
from skdecide import EmptySpace, ImplicitSpace, Space, Value
from skdecide.hub.space.gym import ListSpace


class State:
    """Class defining the state type used by the scikit-decide domains"""

    def __init__(self, domain: Any, state: PladoState, cost_function: set[int] = set()):
        self.atoms: tuple[tuple[tuple[int]]] = tuple(
            tuple(sorted(state.atoms[p])) for p in range(len(state.atoms))
        )
        self.domain: Any = domain
        self.fluents: tuple[tuple[tuple[int], int]] = tuple(
            (
                tuple(
                    (args, int(state.fluents[f][args]))
                    for args in sorted(state.fluents[f].keys())
                )
                if f not in cost_function
                else tuple()
            )
            for f in range(len(state.fluents))
        )

    def to_plado(self, cost_functions: set[int]) -> PladoState:
        state = PladoState(0, len(self.fluents))
        state.atoms = self.atoms
        for f, values in enumerate(self.fluents):
            for args, val in values:
                state.fluents[f][args] = Float(val)
        for f in cost_functions:
            state.fluents[f][tuple()] = Float(0)
        return state

    def __str__(self) -> str:
        return self.domain.task.dump_state(self.to_plado(self.domain.cost_functions))

    def __hash__(self) -> int:
        return hash((self.atoms, self.fluents))

    def __eq__(self, o: object) -> bool:
        return (
            isinstance(o, State) and self.atoms == o.atoms and self.fluents == o.fluents
        )


class Action:
    """Class defining the action type used by the scikit-decide domains"""

    def __init__(self, domain: Any, action_id: int, args: tuple[int]) -> None:
        self.domain = domain
        self.action_id = action_id
        self.args = args

    def __str__(self) -> str:
        return self.domain.task.dump_action(self.action_id, self.args)

    def __hash__(self) -> int:
        return hash((self.action_id, self.args))

    def __eq__(self, o: object) -> bool:
        return (
            isinstance(o, Action)
            and self.action_id == o.action_id
            and self.args == o.args
        )


class D:
    T_state = State  # Type of states
    T_observation = T_state  # Type of observations
    T_event = Action  # Type of events
    T_value = float  # Type of transition values (rewards or costs)
    T_predicate = bool  # Type of test results
    T_info = None  # Type of additional information in environment outcome


class ObservationSpace(Space[D.T_observation]):
    """Class defining the observation space used by the scikit-decide domains"""

    def __init__(
        self,
        predicate_arities: Iterable[int],
        function_arities: Iterable[int],
        num_objects: int,
    ):
        self.predicate_arities: tuple[int] = tuple(predicate_arities)
        self.function_arities: tuple[int] = tuple(function_arities)
        self.num_objects: int = num_objects

    def contains(self, x: D.T_observation) -> bool:
        if len(x.atoms) != len(self.predicate_arities) or len(x.fluents) != len(
            self.function_arities
        ):
            return False
        for p in range(x.atoms):
            for params in x.atoms[p]:
                if (
                    len(params) != self.predicate_arities[p]
                    or min(params) < 0
                    or max(params) >= self.num_objects
                ):
                    return False
        for f in range(x.fluents):
            for params, _ in x.fluents[f]:
                if (
                    len(params) != self.function_arities[f]
                    or min(params) < 0
                    or max(params) >= self.num_objects
                ):
                    return False
        return True


class ActionSpace(Space[D.T_event]):
    """Class defining the action space used by the scikit-decide domains"""

    def __init__(self, action_arities: Iterable[int], num_objects: int):
        self.action_arities: tuple[int] = tuple(action_arities)
        self.num_objects: int = num_objects

    def contains(self, a: D.T_event) -> bool:
        return (
            a[0] >= 0
            and a[0] < len(self.action_arities)
            and len(a[1]) == self.action_arities[a[0]]
            and min(a[1]) >= 0
            and max(a[1]) < self.num_objects
        )


class SkdBaseDomain(D):
    """Base class of the scikit-decide domains.
    All those domains are based on a PDDL encoding of the actions
    to model the logics of the transition function."""

    def cleanup(self):
        """Erases the temporary directory containing PDDL files (if any)"""
        if self.temp_pddl_directory is not None:
            self.temp_pddl_directory.cleanup()

    def _translate_state(self, state: PladoState) -> State:
        return State(self, state, self.cost_functions)

    def _get_cost_from_state(self, state: PladoState) -> int:
        if self.total_cost is None:
            return 1  # assume unit cost
        return int(state.fluents[self.total_cost][tuple()])

    def get_pddl_domain(self) -> os.PathLike:
        """Get the path to the PDDL domain file

        Returns:
            os.PathLike: Path to the PDDL domain file
        """
        return self.domain_path

    def get_pddl_problem(self) -> os.PathLike:
        """Get the path to the PDDL problem file

        Returns:
            os.PathLike: Path to the PDDL problem file
        """
        return self.problem_path

    def _is_terminal(self, state: D.T_state) -> D.T_predicate:
        return self.check_goal(state.to_plado(self.cost_functions))

    def _get_transition_value(
        self,
        memory: D.T_state,
        action: D.T_event,
        next_state: Optional[D.T_state] = None,
    ) -> Value[D.T_value]:
        return Value(cost=self.transition_cost.get((memory, action, next_state), 1))

    def _get_goals_(self) -> Space[D.T_observation]:
        return ImplicitSpace(lambda s: self.check_goal(s.to_plado(self.cost_functions)))

    def _get_initial_state_(self) -> D.T_state:
        return self._translate_state(self.task.initial_state)

    def _get_applicable_actions_from(self, memory: D.T_state) -> Space[D.T_event]:
        aops = [
            Action(self, a[0], a[1])
            for a in self.aops_gen(memory.to_plado(self.cost_functions))
        ]
        if len(aops) == 0:
            return EmptySpace()
        return ListSpace(aops)

    def _get_action_space_(self) -> Space[D.T_event]:
        return self.action_space

    def _get_observation_space_(self) -> Space[D.T_observation]:
        return self.observation_space

    def _init_deserializer(self):
        self._action_idx: dict[str, int] = {}
        for i, a in enumerate(self.task.actions):
            self._action_idx[a.name.lower()] = i
        self._predicate_idx: dict[str, int] = {}
        for i, p in enumerate(self.task.predicates):
            self._predicate_idx[p.name.lower()] = i
        self._function_idx: dict[str, int] = {}
        for i, f in enumerate(self.task.functions):
            self._function_idx[f.name.lower()] = i
        self._object_idx: dict[str, int] = {}
        for i, o in enumerate(self.task.objects):
            self._object_idx[o.lower()] = i

    def _deserialize_objects(self, objs: tuple[str]) -> tuple[int]:
        res = []
        for o in objs:
            res.append(self._object_idx.get(o, None))
            if res[-1] is None:
                raise ValueError(f"object {o} doesn't exist")
        return tuple(res)

    def _deserialize_atom(self, atom: tuple[str]) -> tuple[int] | None:
        if len(atom) == 0:
            raise ValueError("empty tuple doesn't represent a fact")
        idx = self._predicate_idx.get(atom[0].lower(), None)
        if idx is None:
            raise ValueError(f"predicate {atom[0]} doesn't exist")
        params = self._deserialize_objects(atom[1:])
        if idx > self.task.num_fluent_predicates:
            return None
        return (idx, *params)

    def _deserialize_fluent_atom(self, atom: tuple[str]) -> tuple[int] | None:
        if len(atom) == 0:
            raise ValueError("empty tuple doesn't represent a fluent")
        idx = self._function_idx.get(atom[0].lower(), None)
        if idx is None:
            raise ValueError(f"function {atom[0]} doesn't exist")
        params = self._deserialize_objects(atom[1:])
        return (idx, *params)

    def deserialize_state(
        self, atoms: Iterable[tuple[str]], fluents: Iterable[tuple[tuple[str], int]]
    ):
        atoms_ = tuple(
            x for x in (self._deserialize_atom(atom) for atom in atoms) if x is not None
        )
        fluents_ = tuple(
            (self._deserialize_fluent_atom(atom), value) for (atom, value) in fluents
        )
        state = State(self, PladoState(0, 0), [])
        state.atoms = atoms_
        state.fluents = fluents_
        return state

    def deserialize_action(self, action: tuple[str]) -> Action:
        if len(action) == 0:
            raise ValueError("empty tuple doesn't represent an action")
        idx = self._action_idx.get(action[0].lower(), None)
        if idx is None:
            raise ValueError(f"action {action[0]} doesn't exist")
        return Action(self, idx, self._deserialize_objects(action[1:]))

    def serialize_state(
        self, state: State
    ) -> tuple[tuple[str], tuple[tuple[str], int]]:
        return tuple(
            (self.task.predicates[p[0]].name, *(self.task.objects[f] for f in p[1:]))
            for p in state.atoms
        ), tuple(
            (
                (
                    self.task.functions[f[0]].name,
                    *(self.task.objects[f] for f in f[1:]),
                    value,
                )
                for f, value in state.fluents
            )
        )

    def serialize_action(self, action: Action) -> tuple[str]:
        return (
            self.task.actions[action.action_id],
            *(self.task.objects[f] for f in action.args),
        )

    def _create_pddl_structs(
        self,
        domain_str: str,
        problem_str: str,
        instance_dir: os.PathLike = None,
        domain_filename: str = "domain.pddl",
        problem_filename: str = "problem.pddl",
    ):

        if instance_dir is None:
            self.temp_pddl_directory = TemporaryDirectory()
            instance_dir = self.temp_pddl_directory.name
        else:
            self.temp_pddl_directory = None

        self.domain_path = os.path.join(instance_dir, domain_filename)
        with open(self.domain_path, "w") as f:
            f.write(domain_str)

        self.problem_path = os.path.join(instance_dir, problem_filename)
        with open(self.problem_path, "w") as f:
            f.write(problem_str)

        domain, problem = parse_and_normalize(self.domain_path, self.problem_path)
        self.task: Task = Task(domain, problem)
        self.check_goal: GoalChecker = GoalChecker(self.task)
        self.aops_gen: ApplicableActionsGenerator = ApplicableActionsGenerator(
            self.task
        )
        self.succ_gen: SuccessorGenerator = SuccessorGenerator(self.task)
        self.total_cost: int | None = None
        for i, f in enumerate(self.task.functions):
            if f.name == "total-cost":
                self.total_cost = i
                break
        self.cost_functions: set[int] = set(
            [self.total_cost] if self.total_cost is not None else []
        )
        self.transition_cost: dict[tuple[State, Action, State], int] = {}

        self.observation_space = ObservationSpace(
            (
                len(self.task.predicates[p].parameters)
                for p in range(self.task.num_fluent_predicates)
            ),
            (len(f.parameters) for f in self.task.functions),
            len(self.task.objects),
        )

        self.action_space = ActionSpace(
            (a.parameters for a in self.task.actions), len(self.task.objects)
        )

        self._init_deserializer()

    def _generate_pddl(
        self,
        beluga_problem: BelugaProblem,
        problem_name: str,
        variant: Variant,
        state: BelugaProblemState = None,
    ):

        domain_encoding = DomainEncoding(variant, beluga_problem)
        self.domain_str = domain_encoding.domain.to_pddl("beluga")

        # TODO replaced the double encoding with a copy; there's a good chance not even the copy is needed
        # domain_encoding = DomainEncoding(variant, beluga_problem)
        # domain_str = domain_encoding.domain.to_pddl("beluga")
        domain_str = copy.copy(self.domain_str)

        pddl_problem = encode(
            problem_name.replace(".json", ""),
            beluga_problem,
            domain_encoding.domain,
            variant,
            state=state,
        )
        name = "beluga-" + problem_name
        name = name.replace(".", "")
        problem_str = pddl_problem.to_pddl(name)

        # print('-' * 78)
        # print('DOMAIN PDDL')
        # print(domain_str)
        # print('-' * 78)
        # print('PROBLEM PDDL')
        # print(problem_str)

        return domain_str, problem_str
