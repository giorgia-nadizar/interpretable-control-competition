#!/usr/bin/env python

import json
from math import exp
import os

import argparse
import sys
from typing import Union
import uuid

import numpy as np
from numpy.typing import ArrayLike

from skdecide import TransitionOutcome, Value
from skdecide.hub.space.gym import GymSpace, BoxSpace

from ray.rllib.models.modelv2 import flatten, restore_original_dimensions
from ray.rllib.algorithms.ppo import PPOConfig

from generator.configurations.default_configuration import (
    DefaultProblemConfig,
)
from generator.configurations.configs import UnsolvabilityScenario
from beluga_lib.beluga_problem import BelugaProblemDecoder

from skd_domains.skd_base_domain import SkdBaseDomain, PladoState
from skd_domains.skd_pddl_domain import SkdPDDLDomain
from skd_domains.skd_ppddl_domain import SkdPPDDLDomain
from skd_domains.skd_spddl_domain import SkdSPDDLDomain
from skd_domains.skd_gym_domain import BelugaGymCompatibleDomain, BelugaGymEnv

from generate_instance import ProbConfig, main as encode_json


class ExampleBelugaGymCompatibleDomain(BelugaGymCompatibleDomain):
    """This is an example specialization of the BelugaGymCompatibleDomain class
    which transforms PDDL-style states and actions from the original Beluga
    scikit-decide domains to tensors to be used with deep reinforcement learning
    algorithms. As shown at the bottom of this script, an instance of this class
    must be passed to the BelugaGymEnv class, which will automatically populate
    the gymnasium environment methods expected by deep reinforcement learning
    solvers.

    Please note that this class does not provide efficient tensor representations
    for states and actions. It is only intended as exemplifying the transformation
    from PDDL-style states and actions to tensors, and vice-versa.

    State representation.
    The PDDL-style state is composed of a set of predicates - and also fluents in the
    case of the numeric PDDL encoding. Predicate and fluents take the form
    (head obj1 ... objn), e.g. (at-side trailer1 fside). While a predicate can only be
    true or false, a fluent can take a numeric value. For the tensor representation,
    we treat predicates and fluents in the same way, assuming that a predicate is a fluent
    taking Boolean values only. Our tensor representation is a fixed-size tensor,
    but sufficiently large to handle problems of different sizes, using padding to disregard
    the unused tensor entries. The observation space is a matrix NxM where each line
    encodes a fluent and each column encodes the fluent's objects. Since fluents can
    have a different number of arguments, we have as many columns as the the maximum
    number of arguments across all the fluents, and we use padding to disregard entries
    corresponding to unused arguments. It means that a fluent f, whose integer ID is f-id,
    and whose arguments integer IDs are arg1-id, arg2-id, ..., and whose value if f-value,
    is represented as a row vector in the form [f-id arg1-id arg2-id ... argn-id fvalue].
    The arguments which are not used are equal to -1. For instance, if all the fluents
    in the domain use at most 4 arguments, we would encode the Boolean predicate
    (at-side trailer1 fside) taking a true value with a row vector in the form
    [at-side-id trailer1-id f-side-id -1 -1 1].
    IMPORTANT NOTE: in fact, PDDL-style states only enumerate Boolean predicates which
    are true, for memory efficiency reasons. Our tensor representation does the same,
    by listing only the rows corresponding to Boolean predicates that take a true value.
    However, all the integer and float fluents are listed, as in PDDL.

    Action representation.
    The PDDL-style action takes the form of (head obj1 ... objn), e.g.
    (get-from-hangar jig1 hangar1 trailer1). The tensor action is represented as a
    1-dimensional tensor, i.e. a vector, in the form [action-id arg1-id ... argn-id]
    where action-id, arg1-id, ..., argn-id are all integers. The number of argument
    entries is equal to the maximum number of action arguments across all the actions
    in the domain, meaning that unused argument entries for some actions are equal to -1.
    For instance, if the maximum number of action arguments across all the actions in
    the domain is equal to 5, the PDDL action (get-from-hangar jig1 hangar1 trailer1)
    would be encoded as a vector [get-from-hangar-id jig1-ig hangar1-id trailer1-id -1 -1].

    Applicable actions pitfall.
    Whereas only a few actions are application in each possible given state, the number
    of potential actions is huge (exponential in the number of action arguments). This
    prevents from using standard masking techniques in deep reinforcement learning to
    mask inapplicable actions in a given observation, because it would require first to
    build a vector of size equal to the number of potential actions in the problem - which
    is intractable for the Beluga problem. Finding a reasonable way to mask the inapplicable
    actions in the Beluga environment is part of the challenge. In this simplistic
    environment, we assume that all the actions are potentially applicable in each state,
    but we penalize the inapplicable ones (see the reward signal description below). An
    episode systematically ends when an action is applied in the current state where it is
    not applicable.

    Reward signal.
    The objective of the Beluga environment is to find a policy which reaches a goal state
    with a minimum number of steps. In this example environment, we propose to model the
    reward signal as a function between 0 and 1, which is equal to 0 for all steps but the
    terminal step which is equal to:
    - 0 if the goal is not reached in the terminal step (meaning that this terminal step
    corresponds to having applied an inapplicable action in the previous step or to having
    exhausted the step budget)
    - exp(-nb_of_steps) if the terminal step corresponds to a goal situation
    That way, reaching the goal is always better than not reaching it, and it is better to
    reach the goal with the fewest possible number of steps.
    """

    def __init__(
        self,
        skd_beluga_domain: Union[SkdPDDLDomain, SkdPPDDLDomain, SkdSPDDLDomain],
        max_fluent_value: np.int32 = 1000,
        max_nb_atoms_or_fluents: np.int32 = 1000,
        max_nb_steps: np.int32 = 1000,
    ) -> None:
        """The constructor of the example Gym-compatible Beluga domain. For simplicity reasons, we
        construct states as a 3-dimensional tensor (x, y, z) where we store (y, z) as described in
        the summary presentation of the class but for 3 different categories represented as x:
        static facts (x=0), atoms (x=1), fluents (x=2). It is especially useful because the number
        of atoms, whose only the ones which are true are stored in the state, is state-dependent
        contrary to static facts and fluents. Then, we flatten the tensor before transferring it
        to the external world in the reset() and step() methods.

        Args:
            skd_beluga_domain (Union[SkdPDDLDomain, SkdPPDDLDomain, SkdSPDDLDomain]): the original
            Beluga scikit-decide domain, i.e. one of SkdPDDLDomain, SkdPPDDLDomain,or  SkdSPDDLDomain
            max_fluent_value (np.int32, optional): The maximum value that can take a fluent. Defaults to 1000.
            max_nb_atoms_or_fluents (np.int32, optional): The maximum number of static facts, or predicates,
            or fluents. Each of those categories will have max_nb_atoms_or_fluents entries in the tensor. Defaults to 1000.
            max_nb_steps (np.int32, optional): Maximum number of steps per simulation episode. Defaults to 1000.
        """
        super().__init__(skd_beluga_domain)
        if isinstance(skd_beluga_domain, SkdSPDDLDomain):
            # The SkdSPDDLDomain creates the PDDL task at each reset so that
            # we must reset it (i.e. creates PDDL problem and sample initial state)
            # in order for skd_beluga_domain.task to be created (required below)
            skd_beluga_domain.reset()
        self.max_fluent_value: np.int32 = max_fluent_value
        self.max_nb_atoms_or_fluents: np.int32 = max_nb_atoms_or_fluents
        self.max_nb_steps: np.int32 = max_nb_steps
        self.true_observation_space = BoxSpace(
            low=np.ones(
                shape=[
                    3,
                    self.max_nb_atoms_or_fluents,
                    2
                    + max(
                        len(p.parameters)
                        for p in self.skd_beluga_domain.task.predicates
                    ),
                ],
                dtype=np.int32,
            )
            * (-1),
            high=np.array(
                [
                    [
                        [
                            len(self.skd_beluga_domain.task.predicates),
                        ]
                        + (
                            [len(self.skd_beluga_domain.task.objects)]
                            * max(
                                len(p.parameters)
                                for p in self.skd_beluga_domain.task.predicates
                            )
                        )
                        + [
                            (
                                1
                                if len(self.skd_beluga_domain.task.functions) == 0
                                else self.max_fluent_value
                            )
                        ]
                    ]
                    * self.max_nb_atoms_or_fluents
                ]
                * 3,
                dtype=np.int32,
            ),
        )
        self.observation_space = BoxSpace(
            self.true_observation_space.unwrapped().low.flatten(),
            self.true_observation_space.unwrapped().high.flatten(),
            dtype=self.true_observation_space.unwrapped().dtype,
        )
        self.action_space = BoxSpace(
            low=np.array(
                [0]
                + (
                    [-1]
                    * max(p.parameters for p in self.skd_beluga_domain.task.actions)
                ),
                dtype=np.int32,
            ),
            high=np.array(
                [
                    len(self.skd_beluga_domain.task.actions),
                ]
                + (
                    [len(self.skd_beluga_domain.task.objects)]
                    * max(a.parameters for a in self.skd_beluga_domain.task.actions)
                ),
                dtype=np.int32,
            ),
        )
        self.current_pddl_state: SkdBaseDomain.T_state = None
        self.nb_steps: int = 0

    def make_state_array(self, pddl_state: SkdBaseDomain.T_state) -> ArrayLike:
        state_array: ArrayLike = np.ones(
            shape=self.true_observation_space.shape, dtype=np.int32
        ) * (-1)
        i = 0
        for p, atom in enumerate(self.skd_beluga_domain.task.static_facts):
            for args in atom:
                if i >= self.max_nb_atoms_or_fluents:
                    raise RuntimeError(
                        "Too many static atoms to store them in the state tensor; "
                        "please increase max_nb_atoms_or_fluents"
                    )
                state_array[0][i][0] = p
                state_array[0][i][1 : 1 + len(args)] = args
                state_array[0][i][-1] = 1
                i += 1
        i = 0
        for p, atom in enumerate(pddl_state.atoms):
            for args in atom:
                if i >= self.max_nb_atoms_or_fluents:
                    raise RuntimeError(
                        "Too many state atoms to store them in the state tensor; "
                        "please increase max_nb_atoms_or_fluents"
                    )
                state_array[1][i][0] = p
                state_array[1][i][1 : 1 + len(args)] = args
                state_array[1][i][-1] = 1
                i += 1
        i = 0
        for f, fluent in enumerate(pddl_state.fluents):
            for args, val in fluent:
                if i >= self.max_nb_atoms_or_fluents:
                    raise RuntimeError(
                        "Too many state fluents to store them in the state tensor; "
                        "please increase max_nb_atoms_or_fluents"
                    )
                state_array[2][i][0] = f
                state_array[2][i][1 : 1 + len(args)] = args
                state_array[2][i][-1] = val
                i += 1
        return state_array.flatten()

    def make_pddl_state(self, state_array: ArrayLike) -> SkdBaseDomain.T_state:
        plado_state = PladoState(
            num_predicates=len(self.skd_beluga_domain.task.predicates),
            num_functions=len(self.skd_beluga_domain.task.functions),
        )
        restored_state_array: ArrayLike = state_array.reshape(
            self.true_observation_space.shape
        )
        for atom in range(self.max_nb_atoms_or_fluents):
            if (
                restored_state_array[1][atom][0] >= 0
                and restored_state_array[1][atom][-1] >= 0
            ):
                plado_state.atoms[restored_state_array[1][atom][0]].add(
                    tuple(
                        int(arg)
                        for arg in restored_state_array[1][atom][1:-1]
                        if arg >= 0
                    )
                )
        for fluent in range(self.max_nb_atoms_or_fluents):
            if restored_state_array[2][fluent][0] >= 0:
                plado_state.fluents[restored_state_array[2][fluent][0]].update(
                    {
                        [
                            int(arg)
                            for arg in restored_state_array[2][fluent][1:-1]
                            if arg >= 0
                        ]: restored_state_array[2][fluent][-1]
                    }
                )
        return SkdBaseDomain.T_state(
            domain=self.skd_beluga_domain,
            state=plado_state,
            cost_function=self.skd_beluga_domain.cost_functions,
        )

    def make_action_array(self, pddl_action: SkdBaseDomain.T_event) -> ArrayLike:
        action_array: ArrayLike = np.ones(
            shape=self.action_space.shape, dtype=np.int32
        ) * (-1)
        action_array[0] = pddl_action.action_id
        action_array[1 : 1 + len(pddl_action.args)] = pddl_action.args
        return action_array

    def make_pddl_action(self, action_array: ArrayLike) -> SkdBaseDomain.T_event:
        return SkdBaseDomain.T_event(
            domain=self.skd_beluga_domain,
            action_id=int(action_array[0]),
            args=tuple([int(arg) for arg in action_array[1:] if arg >= 0]),
        )

    def _state_reset(self) -> BelugaGymCompatibleDomain.T_state:
        self.nb_steps = 0
        self.current_pddl_state = self.skd_beluga_domain._state_reset()
        return self.make_state_array(self.current_pddl_state)

    def _state_step(
        self, action: BelugaGymCompatibleDomain.T_event
    ) -> TransitionOutcome[
        BelugaGymCompatibleDomain.T_state,
        Value[BelugaGymCompatibleDomain.T_value],
        BelugaGymCompatibleDomain.T_predicate,
        BelugaGymCompatibleDomain.T_info,
    ]:
        self.nb_steps += 1
        pddl_action: SkdBaseDomain.T_event = self.make_pddl_action(action)
        if self.skd_beluga_domain._get_applicable_actions_from(
            self.current_pddl_state
        ).contains(pddl_action):
            outcome = self.skd_beluga_domain._state_step(pddl_action)
            outcome.state = self.make_state_array(outcome.state)
            return TransitionOutcome(
                state=outcome.state,
                value=Value(reward=exp(-self.nb_steps) if outcome.termination else 0),
                termination=outcome.termination or self.nb_steps >= self.max_nb_steps,
                info=outcome.info,
            )
        else:
            return TransitionOutcome(
                state=self.make_state_array(self.current_pddl_state),
                value=Value(reward=0),
                termination=True,
                info=None,
            )

    def _get_observation_space_(
        self,
    ) -> GymSpace[BelugaGymCompatibleDomain.T_observation]:
        return self.observation_space

    def _get_action_space_(self) -> GymSpace[BelugaGymCompatibleDomain.T_event]:
        return self.action_space


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Beluga random instance generator and simulator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Main parameters
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        required=False,
        help="seed for the random generator",
        default=1,
    )

    parser.add_argument(
        "-t",
        "--jig-type-distribution",
        dest="jig_t_dist",
        type=int,
        required=False,
        default=1,
        help="distribution of jigs types: (0) uniform, \
            (1) small jigs preferred, (2) large jigs preferred",
    )

    parser.add_argument(
        "-or",
        "--occupancy-rate-racks",
        dest="occupancy_rate_racks",
        type=float,
        required=False,
        default=0,
        help="fraction of rack space that is initially occupied",
    )

    parser.add_argument(
        "-f",
        "--num-flights",
        dest="num_flights",
        type=int,
        required=False,
        default=3,
        help="number of incoming and outgoing Beluga flights",
    )

    parser.add_argument(
        "-us",
        "--unsolvable",
        dest="unsolvable_scenario",
        default=None,
        type=UnsolvabilityScenario.argparse,
        choices=list(UnsolvabilityScenario),
        help="scenario based on which the generator tries to generate an unsolvable instance",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        required=False,
        help="print debug output",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-o",
        "--out",
        type=str,
        required=False,
        help="output folder for the problem, if no folder is given, \
                        the problem is printed onto stdout",
    )

    parser.add_argument(
        "-on",
        "--out-name",
        dest="out_name",
        type=str,
        required=False,
        help="name for the problem, if no name \
                        is defined, a name based on the number of jigs, jig types, \
                        racks, the exact occupancy rate, the number of flights, \
                        the seed and potentially the unsolvability scenarios is \
                        generated",
    )

    # Parameters for the probabilistic model
    parser.add_argument(
        "-pp",
        "--probabilistic",
        action="store_true",
        help="Enables the probabilistic model, triggering the generation \
            of probabilistic instances",
    )

    parser.add_argument(
        "-pm",
        "--probabilistic-model",
        type=str,
        required=False,
        choices=["arrivals", "ppddl"],
        default="arrivals",
        help="Probabilistic model, one of ['arrivals'; 'ppddl']; \
                'arrivals' mode: triggers the generation of scheduled arrival times for all flights; \
                'ppddl' mode: generate next arrival flight based on the history of landed Beluga flights",
    )

    # parser.add_argument(
    #     "-pt",
    #     "--probabilistic-type",
    #     type=argparse.FileType("r"),
    #     default=None,
    #     help="Configuration file for the chosen type of Potential in \
    #                     the probabilistic model; by default, a uniform potential is \
    #                     used. This parameter is ignored unless 'ppddl' probabilistic mode \
    #                     if enabled",
    # )

    parser.add_argument(
        "-pw",
        "--probabilistic-window",
        type=int,
        default=1,
        help="Length of the swapping window for the probabilistic \
                        model; e.g. passing 1 guarantees that flights cannot move \
                        more than 1 step away from the position initially assigned \
                        by the generation process. This parameter is ignored unless \
                        'ppddl' probabilistic mode is enabled",
    )

    parser.add_argument(
        "-n",
        dest="numeric",
        help="numeric encoding, otherwise classic encoding",
        action="store_true",
    )

    parser.add_argument(
        "-ms",
        dest="max_simulation_steps",
        help="maximum number of simulation steps unless the goal is reached before",
        type=int,
        required=False,
    )

    # Parse command line arguments
    args = parser.parse_args()

    unsolvable_scenarios = (
        [] if args.unsolvable_scenario is None else [args.unsolvable_scenario]
    )

    # Build and validate the deterministic configuration
    config = DefaultProblemConfig(
        args.verbose,
        args.seed,
        args.occupancy_rate_racks,
        args.jig_t_dist,
        args.num_flights,
        unsolvable_scenarios,
    )

    config.check_config()

    # Obtain arguments for the probabilistic model generation
    if args.probabilistic:
        pconfig = ProbConfig(
            args.probabilistic_model == "arrivals",
            # args.probabilistic_type,
            args.probabilistic_window,
        )
        if args.probabilistic_model == "ppddl":
            if pconfig.window < 0 or pconfig.window > args.num_flights - 1:
                print(
                    "The length of the state sequence must be strictly positive and cannot be \
                larger than the number of flights, minus one"
                )
                sys.exit(1)
    else:
        pconfig = None

    if args.out is None:
        args.out = "__tmp_out_" + uuid.uuid4().hex + "__"
        os.makedirs(args.out)
    elif not os.path.exists(args.out):
        os.makedirs(args.out)

    problem_folder = args.out
    problem_name = args.out_name
    classic = not args.numeric
    max_simulation_steps = args.max_simulation_steps

    if args.probabilistic and args.probabilistic_model == "ppddl" and not classic:
        print(
            "Error: SkdPPDDLDomain does not support numeric encoding. Please select a different encoding or model."
        )
        sys.exit(1)

    print("Generating JSON instance")
    _, problem_name = encode_json(problem_folder, problem_name, config, pconfig=pconfig)

    print("Generating PDDL instance")

    problem_out = os.path.join(problem_folder, problem_name)
    with open(problem_out, "r") as fp:
        inst = json.load(fp, cls=BelugaProblemDecoder)

    print(
        "Creating Sk{}PDDLDomain".format(
            "P"
            if args.probabilistic and args.probabilistic_model == "ppddl"
            else (
                "S"
                if args.probabilistic and args.probabilistic_model == "arrivals"
                else ""
            )
        )
    )
    domain_factory = lambda: (
        SkdPPDDLDomain(inst, problem_name, problem_folder)
        if args.probabilistic and args.probabilistic_model == "ppddl"
        else (
            SkdSPDDLDomain(inst, problem_name, problem_folder, classic=classic)
            if args.probabilistic and args.probabilistic_model == "arrivals"
            else SkdPDDLDomain(inst, problem_name, problem_folder, classic=classic)
        )
    )
    domain = domain_factory()

    print(
        "Creating Gym-compatible domain, i.e. containing array-like spaces for actions and states"
    )
    gym_compatible_domain = ExampleBelugaGymCompatibleDomain(
        skd_beluga_domain=domain,
        max_fluent_value=1000,
        max_nb_atoms_or_fluents=1000,
        max_nb_steps=1000,
    )

    print("Creating the RLlib training agent, learning on the exported BelugaGymEnv")
    # IMPORTANT NOTE: we show here how to use RLlib on BelugaGymEnv which relies on scikit-decide's
    # automated mechanism to cast scikit-decide domains to gymnasium environments. However, the connection
    # to RLlib can also be done automatically by scikit-decide via scikit-decide's RayRLlib solver without
    # explicitly creating the exported BelugaGymEnv (not demonstrated here since most RL people will most
    # probably train the Beluga environment on their own RL agent outside scikit-decide or even RLlib).
    # If you just want to have a gymnasium environment on which to train your RL agent,
    # do the 2 following tasks: 1) specialize the BelugaGymCompatibleDomain class to your tensor representation
    # needs; 2) pass this specialized class to the BelugaGymEnv class, which is your gym environment.
    config = (
        PPOConfig()
        .api_stack(
            enable_rl_module_and_learner=False,
            enable_env_runner_and_connector_v2=False,
        )
        .environment(
            env=BelugaGymEnv,
            env_config={"domain": gym_compatible_domain},
        )
        .env_runners(num_env_runners=1)
    )

    algo = config.build()
    algo.train()

    print("Simulating RL learned policy")
    s = domain.reset()
    print(f"\nInitial state: {s}")
    step = 0
    while not domain._is_terminal(s) and step < (
        max_simulation_steps if max_simulation_steps else 100
    ):
        a = gym_compatible_domain.make_pddl_action(
            algo.compute_single_action(gym_compatible_domain.make_state_array(s))
        )
        if domain.get_applicable_actions(s).contains(a):
            print(f"\nApplying action: {a}")
            o = domain.step(a)
            s = o.observation
            print(f"\nCurrent state: {s}")
            step += 1
        else:
            try:  # inferred action's integer args might correspond to non-existing PDDL objects
                print(f"\nInapplicable action: {a} - exiting")
            except IndexError:
                print(
                    f"\nInapplicable action: {gym_compatible_domain.make_action_array(a)} - exiting"
                )
            break
    domain.cleanup()
