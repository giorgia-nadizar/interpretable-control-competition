#!/usr/bin/env python

import json
import os

import argparse
import sys
import uuid

from generator.configurations.default_configuration import (
    DefaultProblemConfig,
)
from generator.configurations.configs import UnsolvabilityScenario

# from beluga_lib.problem_def import BelugaProblemDecoder
from beluga_lib.beluga_problem import BelugaProblemDecoder

from skd_domains.skd_pddl_domain import SkdPDDLDomain
from skd_domains.skd_ppddl_domain import SkdPPDDLDomain
from skd_domains.skd_spddl_domain import SkdSPDDLDomain

from generate_instance import ProbConfig, main as encode_json

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

    print("Generating JSON instance")
    _, problem_name = encode_json(problem_folder, problem_name, config, pconfig=pconfig)

    print("Generating PDDL instance")

    problem_out = os.path.join(problem_folder, problem_name)
    with open(problem_out, "r") as fp:
        inst = json.load(fp, cls=BelugaProblemDecoder)

    print("Creating Sk{}PDDLDomain".format("P" if args.probabilistic else ""))
    domain_factory = lambda: (
        SkdPPDDLDomain(inst, problem_name, problem_folder)
        if args.probabilistic and args.probabilistic_model == "ppddl"
        else (
            SkdSPDDLDomain(inst, problem_name, problem_folder)
            if args.probabilistic and args.probabilistic_model == "arrivals"
            else SkdPDDLDomain(inst, problem_name, problem_folder)
        )
    )
    domain = domain_factory()
    action_space = domain.get_action_space()
    observation_space = domain.get_observation_space()

    print("Simulating random actions")
    s = domain.reset()
    print(f"\nInitial state: {s}")
    step = 0
    while not domain._is_terminal(s) and step < (
        max_simulation_steps if max_simulation_steps else 100
    ):
        a = domain.get_applicable_actions(s).sample()
        print(f"\nApplying action: {a}")
        o = domain.step(a)
        s = o.observation
        print(f"\nCurrent state: {s}")
        step += 1
    domain.cleanup()
