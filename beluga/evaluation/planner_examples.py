from .planner_api import DeterministicPlannerAPI
from .planner_api import ProbabilisticPlannerAPI, ProbabilisticPlanningMetatada
from .planner_api import BelugaAction, BelugaPlan
from .planner_api import LoadBeluga, UnloadBeluga
from .planner_api import PutDownRack, PickUpRack
from .planner_api import DeliverToHangar, GetFromHangar
from .planner_api import SwitchToNextBeluga
from encoder.pddl_encoding.variant import Variant
from beluga_lib.beluga_problem import BelugaProblem
from beluga_lib.problem_state import BelugaProblemState
from encoder.pddl_encoding import DomainEncoding, encode
from skd_domains.skd_pddl_domain import SkdPDDLDomain
from skd_domains.skd_base_domain import Action, SkdBaseDomain
from skdecide.hub.solver.lazy_astar import LazyAstar
from skdecide.hub.solver.astar import Astar
from skdecide import utils
import json

# ============================================================================
# Utility functions
# ============================================================================

def _generate_pddl(
        beluga_problem: BelugaProblem,
        classic : bool = True,
        probabilistic : bool = False,
        state : BelugaProblemState = None,
    ):

    variant = Variant()
    variant.classic = classic
    variant.probabilistic = probabilistic

    domain_encoding = DomainEncoding(variant, beluga_problem)
    domain_str = domain_encoding.domain.to_pddl("beluga")

    problem_name = 'Internal Beluga Problem Instance'
    pddl_problem = encode(name=problem_name,
                          beluga_problem=beluga_problem,
                          domain=domain_encoding.domain,
                          variant=variant,
                          state=state)

    problem_str = pddl_problem.to_pddl(problem_name)

    return domain_str, problem_str


def _skd_action_to_beluga_action(action : Action,
                                 domain : SkdBaseDomain,
                                 classic : bool = False):

    # Retrieve action data
    action_name = domain.task.actions[action.action_id].name
    action_args = [domain.task.objects[o] for o in action.args]
    # Build the corresponding BelugaAction
    res = None
    if classic:
        if action_name == 'load-beluga':
            jig, _, _, flight, trailer, _, _ = action_args
            res = LoadBeluga(jig, flight, trailer)
        elif action_name == 'unload-beluga':
            jig, _, trailer, flight = action_args
            res = UnloadBeluga(jig, flight, trailer)
        elif action_name == 'deliver-to-hangar':
            jig, _, trailer, hangar, pl, _, _ = action_args
            res = DeliverToHangar(jig, hangar, trailer, pl)
        elif action_name == 'get-from-hangar':
            jig, hangar, trailer = action_args
            res = GetFromHangar(jig, hangar, trailer)
        elif action_name == 'put-down-rack':
            jig, trailer, rack, side, _, _, _ = action_args
            res = PutDownRack(jig, trailer, rack, side)
        elif action_name == 'stack-rack':
            jig, _, trailer, rack, side, _, _, _, _ = action_args
            res = PutDownRack(jig, trailer, rack, side)
        elif action_name == 'pick-up-rack':
            jig, trailer, rack, side, _, _, _, _ = action_args
            res = PickUpRack(jig, trailer, rack, side)
        elif action_name == 'unstack-rack':
            jig, _, trailer, rack, side, _, _, _, _ = action_args
            res = PickUpRack(jig, trailer, rack, side)
        elif action_name == 'beluga-complete':
            # _, flight = action_args
            # res = SwitchToBeluga(flight)
            _, _ = action_args
            res = SwitchToNextBeluga()
        else:
            raise ValueError(f'Invalid action name: {action_name}')
    else:
        if action_name == 'load-beluga':
            jig, _, _, flight, trailer, _, _ = action_args
            res = LoadBeluga(jig, flight, trailer)
        elif action_name == 'unload-beluga':
            jig, _, trailer, flight = action_args
            res = UnloadBeluga(jig, flight, trailer)
        elif action_name == 'deliver-to-hangar':
            jig, _, trailer, hangar, pl = action_args
            res = DeliverToHangar(jig, hangar, trailer, pl)
        elif action_name == 'get-from-hangar':
            jig, hangar, trailer = action_args
            res = GetFromHangar(jig, hangar, trailer)
        elif action_name == 'put-down-rack':
            jig, trailer, rack, side = action_args
            res = PutDownRack(jig, trailer, rack, side)
        elif action_name == 'stack-rack':
            jig, _, trailer, rack, side, _, = action_args
            res = PutDownRack(jig, trailer, rack, side)
        elif action_name == 'pick-up-rack':
            jig, trailer, rack, side, _ = action_args
            res = PickUpRack(jig, trailer, rack, side)
        elif action_name == 'unstack-rack':
            jig, _, trailer, rack, side, _, = action_args
            res = PickUpRack(jig, trailer, rack, side)
        elif action_name == 'beluga-complete':
            # _, flight = action_args
            # res = SwitchToBeluga(flight)
            _, _ = action_args
            res = SwitchToNextBeluga()
        else:
            raise ValueError(f'Invalid action name: {action_name}')
    return res

# ============================================================================
# A example of a deterministic planner (random action selection)
# ============================================================================

class LazyAstarDeterministicPlanner(DeterministicPlannerAPI):

    def __init__(self,
                 classic : bool = True):
        self.classic = classic

    def setup(self):
        pass

    def build_plan(self, prb : BelugaProblem):
        # Build a SKD domain
        domain = SkdPDDLDomain(prb, problem_name='server_side_domain',
                               classic=self.classic)
        action_space = domain.get_action_space()
        observation_space = domain.get_observation_space()


        with LazyAstar(domain_factory = lambda: domain) as slv:
            slv.solve()
            plan = slv.get_plan()

        # Cleanup
        domain.cleanup()

        if len(plan) == 0:
            return None

        # Translate the plan
        res = BelugaPlan()
        for a in plan:
            ba = _skd_action_to_beluga_action(action=a, domain=domain, classic=self.classic)
            res.append(ba)

        # Return the result
        return res


class RandomDeterministicPlanner(DeterministicPlannerAPI):

    def __init__(self,
                 max_steps : int = 100,
                 classic : bool = False):
        self.classic = classic
        self.max_steps = max_steps

    def setup(self):
        pass

    def build_plan(self, prb : BelugaProblem):
        # Build a SKD domain
        domain = SkdPDDLDomain(prb, problem_name='server_side_domain',
                               classic=self.classic)
        action_space = domain.get_action_space()
        observation_space = domain.get_observation_space()

        res = BelugaPlan()
        s = domain.reset()
        scaled_max_steps = len(prb.jigs) * self.max_steps
        for step in range(scaled_max_steps):
            # Stop the process if the goal has been reached
            if domain._is_terminal(s):
                break
            # Determine applicable actions
            actions = domain.get_applicable_actions(s)
            # Stop the process if a dead-end has been reached
            if len(actions.get_elements()) == 0:
                break
            # Sample an applicable action
            a = actions.sample()
            # Convert the action in the competition format
            ba = _skd_action_to_beluga_action(action=a, domain=domain, classic=self.classic)
            # Store the action in the plan
            res.append(ba)
            # Apply the action and move to the next state
            o = domain.step(a)
            s = o.observation

        # # Return the plan
        # return res

        # Cleanup
        domain.cleanup()

        # Return the result
        return res


class FixedPlanDeterministicPlanner(DeterministicPlannerAPI):

    def __init__(self, plan_file):
        self.plan_file = plan_file
        self.plan = None

    def setup(self):
        pass

    def build_plan(self, prb : BelugaProblem):
        # Read the plan from the input file
        json_plan = json.load(self.plan_file)
        plan = BelugaPlan.from_json_obj(json_plan, prb)
        # Return the plan
        return plan


# ============================================================================
# A trivial example of a probabilistic planner (random action selection)
# ============================================================================

class LazyAstarProbabilisticPlanner(ProbabilisticPlannerAPI):

    def __init__(self, classic : bool = False):
        self.prb = None
        self.classic = classic

    def setup(self, prb: BelugaProblem):
        self.prb = prb

    def setup_episode(self):
        pass

    def next_action(self,
                    state : BelugaProblemState,
                    metadata : ProbabilisticPlanningMetatada):
        # Build a SKD domain
        domain = SkdPDDLDomain(self.prb, problem_name='server_side_domain',
                               classic=self.classic, initial_state=state)
        action_space = domain.get_action_space()
        observation_space = domain.get_observation_space()

        # try:
        with LazyAstar(domain_factory = lambda: domain) as slv:
            # print(f'>>> solving planning problem at step {metadata.current_step}')
            slv.solve()
            plan = slv.get_plan()

        # Cleanup
        domain.cleanup()

        if len(plan) == 0:
            return None

        # Translate the first action in the plan
        res = _skd_action_to_beluga_action(action=plan[0], domain=domain, classic=self.classic)

        # Return the result
        return res



class RandomProbabilisticPlanner(ProbabilisticPlannerAPI):

    def __init__(self, classic : bool = False):
        self.prb = None
        self.classic = classic

    def setup(self, prb: BelugaProblem):
        self.prb = prb

    def setup_episode(self):
        pass

    def next_action(self,
                    state : BelugaProblemState,
                    metadata : ProbabilisticPlanningMetatada):
        # Build a SKD domain
        domain = SkdPDDLDomain(self.prb, problem_name='server_side_domain',
                               classic=self.classic, initial_state=state)
        action_space = domain.get_action_space()
        observation_space = domain.get_observation_space()

        # Get the SKD version of the current state
        s = domain.reset()

        # print('-' * 78)
        # print('PLANNER STATE')
        # print(s)

        # If the goal has been reached, return no action
        # NOTE this event should never happen
        if domain._is_terminal(s):
            return None

        # Determine applicable actions
        actions = domain.get_applicable_actions(s)

        # print('-' * 78)
        # print('PLANNER APPLICABLE ACTIONS')
        # for a in actions.get_elements():
        #     print(str(a))

        # If a dead-end has been reached, return no action
        if len(actions.get_elements()) == 0:
            return None

        # Sample an applicable action
        a = actions.sample()
        # Convert the action in the competition format
        ba = _skd_action_to_beluga_action(action=a, domain=domain, classic=self.classic)

        # Cleanup
        domain.cleanup()

        # Return the action
        return ba
