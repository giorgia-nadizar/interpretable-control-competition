from beluga_lib.beluga_problem import BelugaProblem
from skd_domains.skd_base_domain import SkdBaseDomain
from skd_domains.skd_pddl_domain import SkdPDDLDomain
from skd_domains.skd_spddl_domain import SkdSPDDLDomain
from .planner_api import ProbabilisticPlannerAPI, ProbabilisticPlanningMetatada
from .planner_api import DeterministicPlannerAPI
from .planner_api import BelugaAction, BelugaPlan
from skd_domains.skd_base_domain import State
import json
from beluga_lib.problem_state import BelugaProblemState
import time
from .planner_api import LoadBeluga, UnloadBeluga
from .planner_api import PutDownRack, PickUpRack
from .planner_api import DeliverToHangar, GetFromHangar
from .planner_api import SwitchToNextBeluga
import os
import numpy as np

# ============================================================================
# Outcome classes
# ============================================================================

class SingleSimulationOutcome:

    def __init__(self,
                 plan_construction_time : float,
                 error_msg : str,
                 plan : BelugaPlan,
                 final_state : BelugaProblemState,
                 final_step : int,
                 goal_reached : bool,
                 abrupt_plan_end : bool,
                 invalid_plan : bool,
                 time_limit_reached : bool,
                 step_limit_reached : bool,
                 free_racks : int,
                 prb : BelugaProblem,
                 alpha : float,
                 beta : float
                 ):
        self.plan_construction_time = plan_construction_time
        self.error_msg = error_msg
        self.plan = plan
        self.final_state = final_state
        self.final_step = final_step
        self.goal_reached = goal_reached
        self.abrupt_plan_end = abrupt_plan_end
        self.invalid_plan = invalid_plan
        self.time_limit_reached = time_limit_reached
        self.step_limit_reached = step_limit_reached
        self.free_racks = free_racks
        self.score = compute_score_dict(self, prb, alpha, beta)

    def to_json_obj(self):
        return {
                'plan_construction_time': self.plan_construction_time,
                'error_msg': self.error_msg,
                'plan': self.plan.to_json_obj(),
                'final_state': self.final_state.to_json_obj() if self.final_state is not None else None,
                'final_step': self.final_step,
                'goal_reached': self.goal_reached,
                'abrupt_plan_end': self.abrupt_plan_end,
                'invalid_plan': self.invalid_plan,
                'time_limit_reached': self.time_limit_reached,
                'step_limit_reached': self.step_limit_reached,
                'free_racks': self.free_racks,
                'score': self.score
                }

    def to_json_str(self, **args):
        return json.dumps(self.to_json_obj(), **args)

    def __repr__(self):
        return self.to_json_str()

    def from_json_obj(json_obj, prb, alpha, beta):
        plan_construction_time = json_obj['plan_construction_time']
        error_msg = json_obj['error_msg']
        plan = BelugaPlan.from_json_obj(json_obj['plan'], prb)
        final_state = BelugaProblemState.from_json_obj(json_obj['final_state'], prb) if json_obj['final_state'] is not None else None
        final_step = json_obj['final_step']
        goal_reached = json_obj['goal_reached']
        abrupt_plan_end = json_obj['abrupt_plan_end']
        invalid_plan = json_obj['invalid_plan']
        time_limit_reached = json_obj['time_limit_reached']
        step_limit_reached = json_obj['step_limit_reached']
        free_racks = json_obj['free_racks']
        res = SingleSimulationOutcome(plan_construction_time, error_msg, plan, final_state, final_step, goal_reached, abrupt_plan_end, invalid_plan, time_limit_reached, step_limit_reached, free_racks, prb, alpha, beta)
        return res


def _none_to_nan(v):
    return v if v is not None else np.nan

class MultipleSimulationOutcome:

    def __init__(self,
                 individual_outcomes : list[SingleSimulationOutcome],
                 ):
        self.individual_outcomes = individual_outcomes

    def _avg_plan_construction_time(self):
        return np.nanmean([_none_to_nan(o.plan_construction_time) for o in self.individual_outcomes])

    def _avg_plan_length(self):
        return np.nanmean([np.nan if o.plan is None else len(o.plan.actions) for o in self.individual_outcomes])

    def _avg_free_racks(self):
        return np.nanmean([_none_to_nan(o.free_racks) for o in self.individual_outcomes])

    def _frac_goal_reached(self):
        return np.nanmean([_none_to_nan(o.goal_reached) for o in self.individual_outcomes])

    def _frac_invalid_plan(self):
        return np.nanmean([_none_to_nan(o.invalid_plan) for o in self.individual_outcomes])

    def _frac_time_limit_reached(self):
        return np.nanmean([_none_to_nan(o.time_limit_reached) for o in self.individual_outcomes])

    def _frac_step_limit_reached(self):
        return np.nanmean([_none_to_nan(o.step_limit_reached) for o in self.individual_outcomes])

    def _avg_score_dict(self):
        keys = self.individual_outcomes[0].score.keys()
        return {k:np.nanmean([o.score[k] for o in self.individual_outcomes]) for k in keys}

    def to_json_obj(self):
        return {
                    'individual_outcomes': [o.to_json_obj() for o in self.individual_outcomes],
                    'avg_plan_construction_time': self._avg_plan_construction_time(),
                    'avg_plan_length': self._avg_plan_length(),
                    'avg_free_racks': self._avg_free_racks(),
                    'frac_goal_reached': self._frac_goal_reached(),
                    'frac_invalid_plan': self._frac_invalid_plan(),
                    'frac_time_limit_reached': self._frac_time_limit_reached(),
                    'frac_step_limit_reached': self._frac_step_limit_reached(),
                    'avg_score': self._avg_score_dict()
                }

    def to_json_str(self, **args):
        return json.dumps(self.to_json_obj(), **args)

    def __repr__(self):
        return self.to_json_str()

    def from_json_obj(json_obj):
        individual_outcomes = [SingleSimulationOutcome.from_json_obj(o) for o in json_obj['individual_outcomes']]
        res = MultipleSimulationOutcome(individual_outcomes)
        return res

# ============================================================================
# Exception classes
# ============================================================================

class EvaluationException(Exception):

    def __init__(self, *largs, **kargs):
        super(EvaluationException, self).__init__(*largs, **kargs)


class InvalidActionException(EvaluationException):

    def __init__(self, *largs, **kargs):
        super(InvalidActionException, self).__init__(*largs, **kargs)

# ============================================================================
# Score computation
# ============================================================================

def compute_score_dict(outcome : SingleSimulationOutcome,
                       prb : BelugaProblem,
                       alpha : float,
                       beta : float):
    # First input term (goal reached)
    A = outcome.goal_reached
    # Second input term (relative plan length)
    B = 0
    if outcome.plan is not None and prb is not None:
        B = len(outcome.plan.actions) / len(prb.jigs)
    # Third input term (inverse of the relative number of free racks)
    C = 0
    if outcome.free_racks is not None and prb is not None:
        C = len(prb.racks) / (1 + outcome.free_racks)
    value = A * np.exp(- alpha * B - beta * C)
    # res = {'value': value, 'alpha': alpha, 'beta': beta}
    res = {'value': value, 'alpha': alpha, 'beta': beta,
           'A': A, 'B': B, 'C': C}
    return res

# ============================================================================
# Class factoring common evaluation functions
# ============================================================================

class EvaluationSupport:

    def __init__(self,
                 prb : BelugaProblem,
                 domain : SkdBaseDomain
                 ):
        # Configuration fields
        self.prb = prb
        self.domain = domain
        # Internal fields
        self.action_space = None
        self.observation_space = None
        self.objects = None
        self.predicates = None

    def refresh_cache(self):
        # Cached problem data
        self.trailer_names = [t.name for t in self.prb.trailers_beluga]
        self.trailer_names += [t.name for t in self.prb.trailers_factory]
        self.rack_names = [r.name for r in self.prb.racks]
        self.hangar_names = [h for h in self.prb.hangars]
        self.jig_names = [j for j in self.prb.jigs]
        self.pl_names = [pl.name for pl in self.prb.production_lines]
        self.flight_names = [f.name for f in self.prb.flights]
        self.flight_map = {f.name : f for f in self.prb.flights}

        # Store and initialize the domain
        self.action_space = self.domain.get_action_space()
        self.observation_space = self.domain.get_observation_space()

        # Cache references to some useful fields
        self.objects = self.domain.task.objects
        self.predicates = self.domain.task.predicates
        self.actions = self.domain.task.actions

    def _process_pred_clear(self, args : list[str],
                            state : BelugaProblemState,
                            clear_jigs : set[str]):
        arg1, arg2 = args
        if arg2 == 'bside':
            clear_jigs.add(arg1)

    def _process_pred_empty(self, args : list[str], state : BelugaProblemState):
        arg = args[0]
        if arg in self.trailer_names:
            state.sfs_trailer_load(trailer=arg, jig=None)
        elif arg in self.rack_names:
            state.sfs_rack_contents(rack=arg, jigs=[])
        elif arg in self.hangar_names:
            state.sfs_hangar_host(arg, None)
        elif arg in self.jig_names:
            state.jig_empty[arg] = True

    def _process_pred_in(self, args : list[str],
                         state : BelugaProblemState,
                         flight_content : dict[str, set[str]],
                         rack_content : dict[str, set[str]]):
        arg1, arg2 = args
        if arg2 in self.flight_names:
            flight_content[arg2].add(arg1)
        elif arg2 in self.trailer_names:
            state.sfs_trailer_load(arg2, arg1)
        elif arg2 in self.rack_names:
            rack_content[arg2].add(arg1)
        elif arg2 in self.hangar_names:
            state.sfs_hangar_host(arg2, arg1)

    def _process_pred_processed_flight(self, args : list[str], state : BelugaProblemState):
        arg = args[0]
        state.sfs_current_beluga(arg)

    def _process_to_deliver(self, args : list[str],
                            state : BelugaProblemState,
                            current_pl_jigs : dict[str, str]):
        arg1, arg2 = args
        current_pl_jigs[arg2] = arg1

    def _process_next_to(self, args : list[str],
                            state : BelugaProblemState,
                            next_jig : dict[str, str]):
        arg1, arg2, arg3 = args
        if arg3 != 'bside':
            return
        next_jig[arg1] = arg2

    def _reconstruct_rack_content(self, rname, content, clear_jigs, next_jig):
        # Handle empty racks
        if len(content) == 0:
            return []
        # Find the starting jig
        head = None
        for jig in content:
            if jig in clear_jigs:
                head = jig
        if head is None:
            raise EvaluationException(f'Cannot identify the starting jig for rack {rname}')
        # Sort the jigs
        sorted_jigs = [head]
        cur_jig = head
        while cur_jig in next_jig:
            sorted_jigs.append(next_jig[cur_jig])
            cur_jig = next_jig[cur_jig]
        if len(set(sorted_jigs) - content) > 0 or len(content - set(sorted_jigs)) > 0:
            raise EvaluationException(f'"in" predicates are inconsistent with "next" predicates for {rname}')
        # Return the result
        return sorted_jigs

    def _skd_state_to_beluga_state(self,
                                   state : State,
                                   beluga_seq : list[str] = [],
                                   trailer_location : dict[str, tuple[str, str]] = {}):

        # # TODO for debugging
        # for k, flist in enumerate(state.fluents):
        #     function_name = self.domain.task.functions[k].name
        #     if function_name == 'free-space':
        #         for (oid, ), val in flist:
        #             if val < 0:
        #                 raise Exception('KABOOM')

        # Build a competition state object
        res = BelugaProblemState(self.prb)
        # Store the sequence of belugas
        res.sfs_last_belugas(beluga_seq)
        # Store the trailer locations
        for trailer, (loc, side) in trailer_location.items():
            res.sfs_trailer_location(trailer, loc, side)
        # Temporary fields
        flight_content = {fname : set() for fname in self.flight_names}
        next_jig = {}
        clear_jigs = set()
        rack_content = {rname : set() for rname in self.rack_names}
        current_pl_jigs = {plname : None for plname in self.pl_names}
        # Loop over all atom types (i.e. predicates)
        for pid, atom_list in enumerate(state.atoms):
            # Retrieve predicate and arguments
            pred = self.predicates[pid].name
            # Loop over atoms for this predicate
            for args_ids in atom_list:
                args = [self.objects[k] for k in args_ids]
                # Update the state
                if pred == 'clear':
                    self._process_pred_clear(args, res, clear_jigs)
                elif pred == 'empty':
                    self._process_pred_empty(args, res)
                elif pred == 'in':
                    self._process_pred_in(args, res, flight_content, rack_content)
                elif pred == 'processed-flight':
                    self._process_pred_processed_flight(args, res)
                elif pred == 'to_deliver':
                    self._process_to_deliver(args, res, current_pl_jigs)
                elif pred == 'next-to':
                    self._process_next_to(args, res, next_jig)
        # Set the beluga content
        res.sfs_beluga_contents(flight_content[res.current_beluga.name])
        # Reconstruct the rack content
        for rname, content in rack_content.items():
            sorted_jigs = self._reconstruct_rack_content(rname, content, clear_jigs, next_jig)
            res.sfs_rack_contents(rname, sorted_jigs)
        # Update the production line schedule
        for pl in self.prb.production_lines:
            schedule = [j.name for j in pl.schedule]
            try:
                cur_jig_idx = schedule.index(current_pl_jigs[pl.name])
                res.sfs_production_line_deliveries(pl.name, schedule[:cur_jig_idx])
            except ValueError:
                res.sfs_production_line_deliveries(pl.name, schedule)
        # Return the converted state
        return res

    def _find_valid_action(self, ba : BelugaAction, state : State, beluga_seq : list[str]):
        # Retrieve applicable actions
        applicable_actions_space = self.domain.get_applicable_actions(state)
        applicable_actions = applicable_actions_space.get_elements()

        # print('-' * 78)
        # print('BELUGA ACTION:')
        # print(ba)
        # print('EVALUATOR APPLICABLE ACTIONS')
        # for a in applicable_actions:
        #     print(str(a))

        # Determine whether there's any applicable action
        if len(applicable_actions) == 0:
            raise EvaluationException('No applicable actions from this state')
        for a in applicable_actions:
            action_name = self.actions[a.action_id].name
            action_args = [self.objects[o] for o in a.args]
            # Determine whethere there's a match
            if action_name == 'load-beluga' and ba.name == LoadBeluga.name:
                jig, _, _, flight, trailer, _, _ = action_args
                if jig == ba.jig and trailer == ba.trailer and flight == ba.flight:
                    return a
            elif action_name == 'unload-beluga' and ba.name == UnloadBeluga.name:
                jig, _, trailer, flight = action_args
                if jig == ba.jig and trailer == ba.trailer and flight == ba.flight:
                    return a
            elif action_name == 'deliver-to-hangar' and ba.name == DeliverToHangar.name:
                jig, _, trailer, hangar, pl = action_args
                if jig == ba.jig and trailer == ba.trailer and hangar == ba.hangar and pl == ba.pl:
                    return a
            elif action_name == 'get-from-hangar' and ba.name == GetFromHangar.name:
                jig, hangar, trailer = action_args
                if jig == ba.jig and trailer == ba.trailer and hangar == ba.hangar:
                    return a
            elif action_name == 'put-down-rack' and ba.name == PutDownRack.name :
                jig, trailer, rack, side = action_args
                if jig == ba.jig and trailer == ba.trailer and rack == ba.rack and side == ba.side:
                    return a
            elif action_name == 'stack-rack' and ba.name == PutDownRack.name :
                jig, _, trailer, rack, side, _ = action_args
                if jig == ba.jig and trailer == ba.trailer and rack == ba.rack and side == ba.side:
                    return a
            elif action_name == 'pick-up-rack' and ba.name == PickUpRack.name:
                jig, trailer, rack, side, _ = action_args
                if jig == ba.jig and trailer == ba.trailer and rack == ba.rack and side == ba.side:
                    return a
            elif action_name == 'unstack-rack' and ba.name == PickUpRack.name:
                jig, _, trailer, rack, side, _ = action_args
                if jig == ba.jig and trailer == ba.trailer and rack == ba.rack and side == ba.side:
                    return a
            elif action_name == 'beluga-complete' and ba.name == SwitchToNextBeluga.name:
                # prev_flight, flight = action_args
                # if prev_flight == beluga_seq[-1] and flight == ba.flight:
                #     return a
                prev_flight, _ = action_args # No check on the next flight, since in the probabilisti case it cannot be known in advance
                if prev_flight == beluga_seq[-1]:
                    return a
        # If no matching action is found, return None
        raise InvalidActionException(f'No matching applicable action found for {ba}')


    def _get_current_beluga(self, state):
        # Find the correct predicate
        for pid, atoms in enumerate(state.atoms):
            if self.predicates[pid].name == 'processed-flight':
                # Check that there's a single atom
                if len(atoms) > 1:
                    raise EvaluationException('There cannot be more than one processed beluga')
                elif len(atoms) == 0:
                    return None
                arg = atoms[0][0]
                return self.objects[arg]
        raise EvaluationException('No "processed-flight" predicate found in the state')

    def _update_trailer_location(self,
                                 ba : BelugaAction,
                                 trailer_location : dict[str, tuple[str, str]]):
        if isinstance(ba, LoadBeluga) or isinstance(ba, UnloadBeluga):
            trailer_location[ba.trailer] = ('beluga', None)
        elif isinstance(ba, GetFromHangar) or isinstance(ba, DeliverToHangar):
            trailer_location[ba.trailer] = (ba.hangar, None)
        elif isinstance(ba, PutDownRack) or isinstance(ba, PickUpRack):
            trailer_location[ba.trailer] = (ba.rack, ba.side)

    def _get_free_racks(self, state: BelugaProblemState):
        return len([r for r, j in state.rack_contents.items() if len(j) == 0])

    def _dump_to_json_file(self, out_file, obj):
        with open(out_file, 'w') as fp:
            json.dump(obj.to_json_obj(), fp, indent=4)


class DeterministicEvaluator:

    def __init__(self,
                 prb : BelugaProblem,
                 problem_name : str,
                 problem_folder : str,
                 planner : DeterministicPlannerAPI,
                 max_steps : int = None,
                 time_limit : int = None,
                 alpha : float = 0.7,
                 beta : float = 0.0004
                 ):
        # Check arguments
        if max_steps is not None and max_steps <= 0:
            raise Exception('The number of steps should be None or strictly positive')
        if time_limit is not None and time_limit <= 0:
            raise Exception('The time limit should be None or strictly positive')
        # Configuration fields
        self.prb = prb
        self.problem_name = problem_name
        self.problem_folder = problem_folder
        self.planner = planner
        self.max_steps = max_steps
        self.time_limit = time_limit
        self.alpha = alpha
        self.beta = beta
        # Internal fields
        self.es = None
        self.domain = None

    def setup(self):
        # Build an SKD domain
        self.domain = SkdPDDLDomain(self.prb, self.problem_name, classic=False)
        # Build an support object
        self.es = EvaluationSupport(self.prb, self.domain)
        self.es.refresh_cache()
        # Setup the planner
        self.planner.setup()

    def evaluate(self):
        # Define the stem for all output files
        out_stem = None
        if self.problem_folder is not None:
            out_stem = self.problem_folder
            if self.problem_name is not None:
                out_stem = os.path.join(out_stem, self.problem_name)

        # Prepare to collect time statistics
        elapsed_time = 0

        # Build a plan (and measure time)
        tstart = time.time()
        plan = self.planner.build_plan(self.prb)
        elapsed_time += time.time() - tstart

        # Handle the case where no plan has been built
        no_plan = (plan is None or len(plan.actions) == 0)
        timeout = (self.time_limit is not None and elapsed_time > self.time_limit)
        if no_plan or timeout:
            msg = 'No plan was produced' if no_plan else 'Plan not accepted (time limit reached)'
            outcome = SingleSimulationOutcome(plan_construction_time=elapsed_time,
                                              error_msg=msg,
                                              plan=plan,
                                              final_state=None,
                                              final_step=None,
                                              goal_reached=False,
                                              abrupt_plan_end=False,
                                              invalid_plan=False,
                                              time_limit_reached=timeout,
                                              step_limit_reached=False,
                                              free_racks=None,
                                              prb=self.prb,
                                              alpha=self.alpha,
                                              beta=self.beta)
            if out_stem is not None:
                self.es._dump_to_json_file(out_stem + '_outcome.json', outcome)
            return outcome

        # State fields that cannot be computed based on predicates
        beluga_seq = []
        trailer_location = {}

        # Planning process stats
        goal_reached = False
        abrupt_plan_end = False

        # Retrieve the initial state
        state = self.domain.reset()

        # Start plan execution
        scaled_max_steps = len(self.prb.jigs) * self.max_steps
        for step in range(scaled_max_steps):
            try:
                # Determine the currently processed flight
                cbeluga = self.es._get_current_beluga(state)
                if len(beluga_seq) == 0 or beluga_seq[-1] != cbeluga:
                    beluga_seq.append(cbeluga)

                # # TODO for debugging
                # bstate = self.es._skd_state_to_beluga_state(state=state,
                #                                             beluga_seq=beluga_seq,
                #                                             trailer_location=trailer_location)
                # with open(f'problem_and_state_test/new_test_instances2/ba_state_{step}.json', 'w') as fp:
                #     json.dump(bstate.to_json_obj(), fp)
                # with open(f'problem_and_state_test/new_test_instances2/skd_state_{step}.txt', 'w') as fp:
                #     fp.write(str(state))
                # print('-' * 78)
                # print(state)
                # print('-' * 78)
                # for k, v in bstate.to_json_obj().items():
                #     print(f'"{k}": {v}')
                # print(bstate.to_json_str(indent=2))

                # Check whether the goal has been reached
                if self.domain._is_terminal(state):
                    goal_reached = True
                    break

                # Check whether the plan has already ended
                if step >= len(plan.actions):
                    abrupt_plan_end = True
                    break

                # Retrive current action
                ba = plan.actions[step]
                # Determine valid actions for the current state
                action = self.es._find_valid_action(ba, state, beluga_seq)

                # print('=' * 78)
                # print(action)

                # Apply the action and move to the next state
                o = self.domain.step(action)
                state = o.observation

                # Update the trailer location
                self.es._update_trailer_location(ba, trailer_location)

            except EvaluationException as e:
                final_state = self.es._skd_state_to_beluga_state(state=state,
                                                            beluga_seq=beluga_seq,
                                                            trailer_location=trailer_location)
                outcome = SingleSimulationOutcome(plan_construction_time=elapsed_time,
                                                  error_msg=e.args[0],
                                                  plan=plan,
                                                  final_state=final_state,
                                                  final_step=step,
                                                  goal_reached=False,
                                                  abrupt_plan_end=False,
                                                  invalid_plan=isinstance(e, InvalidActionException),
                                                  time_limit_reached=False,
                                                  step_limit_reached=False,
                                                  free_racks=self.es._get_free_racks(final_state),
                                                  prb=self.prb,
                                                  alpha=self.alpha,
                                                  beta=self.beta)
                if out_stem is not None:
                    self.es._dump_to_json_file(out_stem + '_outcome.json', outcome)
                return outcome

        # The evaluation proceeded normally
        final_state = self.es._skd_state_to_beluga_state(state=state,
                                                    beluga_seq=beluga_seq,
                                                    trailer_location=trailer_location)
        outcome = SingleSimulationOutcome(plan_construction_time=elapsed_time,
                                          error_msg=None,
                                          plan=plan,
                                          final_state=final_state,
                                          final_step=step,
                                          goal_reached=goal_reached,
                                          abrupt_plan_end=abrupt_plan_end,
                                          invalid_plan=False,
                                          time_limit_reached=False,
                                          step_limit_reached= (step == self.max_steps-1),
                                          free_racks=self.es._get_free_racks(final_state),
                                          prb=self.prb,
                                          alpha=self.alpha,
                                          beta=self.beta)
        if out_stem is not None:
            self.es._dump_to_json_file(out_stem + '_outcome.json', outcome)

        # Return the outcome
        return outcome

    def __del__(self):
        if self.domain is not None:
            self.domain.cleanup()



class ProbabilisticEvaluator:

    def __init__(self,
                 prb : BelugaProblem,
                 problem_name : str,
                 problem_folder : str,
                 planner : ProbabilisticPlannerAPI,
                 nsamples : int = 1,
                 max_steps : int = None,
                 time_limit : int = None,
                 seed : int = None,
                 alpha : float = 0.7,
                 beta : float = 0.0004
                 ):
        # Check arguments
        if nsamples <= 0:
            raise Exception('The number of samples should be strictly positive')
        if max_steps is not None and max_steps <= 0:
            raise Exception('The number of steps should be None or strictly positive')
        if time_limit is not None and time_limit <= 0:
            raise Exception('The time limit should be None or strictly positive')
        # Configuration fields
        self.prb = prb
        self.problem_name = problem_name
        self.problem_folder = problem_folder
        self.planner = planner
        self.nsamples = nsamples
        self.max_steps = max_steps
        self.time_limit = time_limit
        self.seed = seed
        self.alpha = alpha
        self.beta = beta
        # Internal fields
        self.es = None
        self.domain = None

    def setup(self):
        # Build an SKD domain
        self.domain = SkdSPDDLDomain(self.prb,
                                     self.problem_name,
                                     seed=self.seed,
                                     classic=False)
        # Build a support object
        self.es = EvaluationSupport(self.prb, self.domain)
        # Setup the planner
        self.planner.setup(self.prb)

    def _run_simulation(self, past_elapsed_time):
        # Tell the planner that another episode is starting
        try:
            self.planner.setup_episode()
        except EvaluationException as e:
            res = SingleSimulationOutcome(plan_construction_time=None,
                                          error_msg=f'Error while setting up an episode: {e.args[0]}',
                                          plan=None,
                                          final_state=None,
                                          final_step=None,
                                          goal_reached=False,
                                          abrupt_plan_end=False,
                                          invalid_plan=False,
                                          time_limit_reached=False,
                                          step_limit_reached=False,
                                          free_racks=None,
                                          prb=self.prb,
                                          alpha=self.alpha,
                                          beta=self.beta)
            return res

        # Reset the domain state
        state = self.domain.reset() # This regenerates a PDDL file
        self.es.refresh_cache() # ...And therefore all translation maps need to be reloaded

        # State fields that cannot be computed based on predicates
        beluga_seq = []
        trailer_location = {}

        # Prepare to collect time statistics
        # elapsed_time = 0
        elapsed_time = 0
        goal_reached = False
        time_limit_reached = False

        # Build a plan dynamically
        plan = BelugaPlan()
        for current_step in range(self.max_steps):
            try:
                # Determine the currently processed flight
                cbeluga = self.es._get_current_beluga(state)
                if len(beluga_seq) == 0 or beluga_seq[-1] != cbeluga:
                    beluga_seq.append(cbeluga)

                # Convert the state
                bstate = self.es._skd_state_to_beluga_state(state, beluga_seq, trailer_location)

                # Obtain the current metadata
                metadata = ProbabilisticPlanningMetatada(current_step, elapsed_time)

                # DEBUG plot the current state
                # print('=' * 78)
                # print('METADATA')
                # print(metadata.to_json_str())
                # print('-' * 78)
                # print('EVALUATOR STATE')
                # print(state)
                # print('-' * 78)
                # print('EVALUATOR CONVERTED STATE')
                # for k, v in bstate.to_json_obj().items():
                #     print(f'"{k}": {v}')

                # Check whether the goal has been reached
                if self.domain._is_terminal(state):
                    goal_reached = True
                    break

                # First time limit check: this might be triggered in case the time spent
                # on past iterations already exceeds the limit
                if self.time_limit is not None and past_elapsed_time + elapsed_time > self.time_limit:
                    time_limit_reached = True
                    raise EvaluationException('Time limit exceeded')

                # Retrive current action
                start_time = time.time()
                ba = self.planner.next_action(bstate, metadata)
                elapsed_time += time.time() - start_time

                # Add the action to the plan
                plan.actions.append(ba)

                # print('-' * 78)
                # print('PLANNER ACTION')
                # print(ba)

                # Second time limit check. This refers to the current simulation.
                if self.time_limit is not None and past_elapsed_time + elapsed_time > self.time_limit:
                    time_limit_reached = True
                    raise EvaluationException('Time limit exceeded')

                # Determine whether an action was actually returned
                if ba is None:
                    raise EvaluationException('No action returned by the planner')

                # Attempt to match the BelugaAction on a valid SKD action
                action = self.es._find_valid_action(ba, state, beluga_seq)

                # Apply the action and move to the next state
                o = self.domain.step(action)
                state = o.observation

                # Update the trailer location
                self.es._update_trailer_location(ba, trailer_location)

            except EvaluationException as e:
                res = SingleSimulationOutcome(plan_construction_time=elapsed_time,
                                              error_msg=e.args[0],
                                              plan=plan,
                                              final_state=bstate,
                                              final_step=current_step,
                                              goal_reached=goal_reached,
                                              abrupt_plan_end=False,
                                              invalid_plan=False,
                                              time_limit_reached=time_limit_reached,
                                              step_limit_reached=False,
                                              free_racks=self.es._get_free_racks(bstate),
                                              prb=self.prb,
                                              alpha=self.alpha,
                                              beta=self.beta)
                return res

        # Return the result of the simulation
        res = SingleSimulationOutcome(plan_construction_time=elapsed_time,
                                      error_msg=None,
                                      plan=plan,
                                      final_state=bstate,
                                      final_step=current_step,
                                      goal_reached=goal_reached,
                                      abrupt_plan_end=False,
                                      invalid_plan=False,
                                      time_limit_reached=time_limit_reached,
                                      step_limit_reached=(current_step == self.max_steps-1),
                                      free_racks=self.es._get_free_racks(bstate),
                                      prb=self.prb,
                                      alpha=self.alpha,
                                      beta=self.beta)
        return res


    def evaluate(self):
        # Define the stem for all output files
        out_stem = None
        if self.problem_folder is not None:
            out_stem = self.problem_folder
            if self.problem_name is not None:
                out_stem = os.path.join(out_stem, self.problem_name)

        # Run simulations
        sim_outcomes = []
        total_elapsed_time = 0
        for sample_num in range(self.nsamples):
            # Run a simulation
            sim_outcome = self._run_simulation(total_elapsed_time)
            # Update the total elapsed time
            total_elapsed_time += sim_outcome.plan_construction_time
            # Store the outcome
            sim_outcomes.append(sim_outcome)
        # Compute an aggregated outcome
        outcome = MultipleSimulationOutcome(sim_outcomes)

        # Save the outcome to a file
        if out_stem is not None:
            self.es._dump_to_json_file(out_stem + '_outcome.json', outcome)

        # Return the result
        return outcome

    # def __del__(self): # TODO this one does not work when an output folder is specified: ask Florent about it
    #     if self.domain is not None:
    #         self.domain.cleanup()

