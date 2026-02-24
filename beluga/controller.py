import random
from plado.semantics.task import Task
from plado.pddl.arguments import ArgumentDefinition
from skd_domains.skd_base_domain import State, Action, ActionSpace, ObservationSpace
from skd_domains.skd_spddl_domain import SkdSPDDLDomain


class Predicate:
    def __init__(
        self,
        predicate_id: int,
        predicate_name: str,
        param_definitions: tuple[ArgumentDefinition, ...],
        param_ids: tuple[int, ...],
        param_values: tuple[str, ...]
    ) -> None:
        self._predicate_id = predicate_id
        self._predicate_name = predicate_name
        self._param_definitions = param_definitions
        self._param_ids = param_ids
        self._param_values = param_values
    
    def predicate_id(self) -> int:
        return self._predicate_id
    
    def predicate_name(self) -> str:
        return self._predicate_name
    
    def param_definitions(self) -> tuple[ArgumentDefinition, ...]:
        return self._param_definitions
    
    def param_ids(self) -> tuple[int, ...]:
        return self._param_ids
    
    def param_values(self) -> tuple[str, ...]:
        return self._param_values
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Predicate):
            return False
        return (self.predicate_id() == value.predicate_id() and
                self.param_ids() == value.param_ids() and
                self.param_values() == value.param_values() and self.predicate_name() == value.predicate_name())

    def __hash__(self) -> int:
        return hash((self.predicate_id(), self.predicate_name(), self.param_ids(), self.param_values()))
    
    def __str__(self) -> str:
        param_str = ", ".join(f"{defn.name}={val}" for defn, val in zip(self.param_definitions(), self.param_values()))
        return f"{self.predicate_name()}({param_str})"


class Controller:
    def __init__(self, domain: SkdSPDDLDomain) -> None:
        self._domain = domain
        self._action_space = self._domain.get_action_space()
        self._observation_space = self._domain.get_observation_space()
        self._task = self._domain.task
        
    def domain(self) -> SkdSPDDLDomain:
        return self._domain
    
    def get_available_actions(self, observation: State) -> list[Action]:
        return self._domain.get_applicable_actions(observation).get_elements()
    
    def get_true_predicates(self, observation: State) -> list[Predicate]:
        res = []
        atoms = observation.atoms
        predicates = self._task.predicates
        objects = self._task.objects
        for p in range(len(atoms)):
            predicate_name = predicates[p].name
            param_definitions = predicates[p].parameters
            predicate_id = p
            for args in atoms[p]:
                param_ids = args
                param_values = tuple(objects[o] for o in args)
                res.append(Predicate(predicate_id, predicate_name, param_definitions, param_ids, param_values))
        return res

    def action_space(self) -> ActionSpace:
        return self._action_space
    
    def observation_space(self) -> ObservationSpace:
        return self._observation_space
    
    def task(self) -> Task:
        return self._task

    def control(self, observation: State) -> Action:
        raise NotImplementedError


class RandomController(Controller):

    def __init__(self, domain: SkdSPDDLDomain, seed: int) -> None:
        super().__init__(domain=domain)
        self._rng = random.Random(seed)

    def control(self, observation: State) -> Action:
        possible_actions = self.get_available_actions(observation)
        sampled_action = self._rng.choice(possible_actions)
        return sampled_action
    

class MedianIndexController(Controller):
    def __init__(self, domain: SkdSPDDLDomain) -> None:
        super().__init__(domain=domain)

    def control(self, observation: State) -> Action:
        possible_actions = self.get_available_actions(observation)
        median_index = len(possible_actions) // 2
        return possible_actions[median_index]
    

class CustomController(Controller):
    def __init__(self, domain: SkdSPDDLDomain, seed: int) -> None:
        super().__init__(domain=domain)
        self._rng = random.Random(seed)
        # Initialize any additional parameters or state for your custom controller here

    def control(self, observation: State) -> Action:
        # Implement your custom control logic here
        possible_actions = self.get_available_actions(observation)
        # For demonstration, we will just return the first action
        return possible_actions[0]
