#!/usr/bin/env python

import sys
from typing import Tuple

# sys.path.insert(0, "..")
import argparse
import json
import os

from generator.random_generator import BelugaRandomGenerator
from generator.random_generator import ProbabilisticModelGenerator
from beluga_lib import BelugaProblem, BelugaProblemEncoder

from generator.configurations.default_configuration import (
    DefaultProblemConfig,
)

from generator.configurations.configs import ProblemConfig, UnsolvabilityScenario
from utils.uncertainty import add_reference_arrivals, add_abstract_uncertainty_model

# Specific dependencies for the probabilistic model
from collections import namedtuple

ProbConfig = namedtuple("ProbConfig", ["arrivals", "window"])


def main(
    problem_folder,
    problem_name,
    config: ProblemConfig,
    skip_errors=False,
    instance_id=None,
    pconfig: ProbConfig = None,
    return_instance = False,
    no_show = False
) -> Tuple[bool, str]:

    generator = BelugaRandomGenerator(config)

    try:
        inst: BelugaProblem = generator.generate()
    except Exception as exp:
        if skip_errors:
            if not return_instance:
                return False, None
            else:
                return False, None, None
        else:
            if problem_name:
                print(problem_name)
            raise Exception(exp)

    if not config.check_problem(inst):
        if skip_errors:
            if not return_instance:
                return False, None
            else:
                return False, None, None
        else:
            if problem_name:
                print(problem_name)
            raise Exception("Check failed, not a valid instance!")

    # Generate arrival times, if requested (arrivals probabilistic model)
    if pconfig is not None:
        add_reference_arrivals(inst, config.seed)

    # Add probabilstic information, if requested (PPDDL probabilistic model)
    if pconfig is not None and not pconfig.arrivals:
        # Build the transition tables
        add_abstract_uncertainty_model(prb=inst,
                                       history_len=pconfig.window,
                                       seed=config.seed) # by default, this uses 10,000 samples

    # Obtain the problem json representation
    problem_json = json.dumps(inst, cls=BelugaProblemEncoder, indent=4)

    if problem_name is None:
        problem_name = "problem_" + "_".join(
            filter(
                lambda e: e is not None,
                [
                    (str(instance_id) if instance_id is not None else None),
                    "s" + str(config.seed),
                    "j" + str(len(inst.jigs)),
                    "r" + str(len(inst.racks)),
                    "oc"
                    + ("0" if inst.occupancy_rate() < 0.1 else "")
                    + str(int(inst.occupancy_rate() * 100)),
                    "f" + str(len(inst.flights)),
                    (
                        str(config.unsolvable_scenario[0])
                        if len(config.unsolvable_scenario) > 0
                        else None
                    ),
                ],
            )
        )
        if pconfig is not None:
            problem_name += '_pp'
            if not pconfig.arrivals:
                problem_name += f"_pw{pconfig.window}"
        if problem_folder is not None:
            problem_name += ".json"

    # Output the generated problem (stdout)
    if problem_folder is None:
        if not no_show:
            sys.stdout.write(problem_json + '\n')
        if not return_instance:
            return True, problem_name
        else:
            return True, problem_name, inst

    # Output the generated problem (file)
    problem_out = os.path.join(problem_folder, problem_name)

    with open(problem_out, "w") as out_file:
        out_file.write(problem_json)
        # json.dump(inst, out_file, cls=BelugaProblemEncoder, indent=4)

    # Prepare the result to be returned
    if not return_instance:
        return True, problem_name
    else:
        return True, problem_name, inst



def _setup_argument_parser(parser):
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
        "-or",
        "--occupancy-rate-racks",
        dest="occupancy_rate_racks",
        type=float,
        required=False,
        default=0,
        help="fraction of rack space that is initially occupied",
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
        help="Controls the type of probabilistic model, if the `-pp` option is \
        enabled. If the `arrivals` options is used (the default), then the \
        instance will contain only arrival times and will be suitable for a more \
        realistic uncertainty semantic where flights are subject to stochastic \
        delay; if the `ppddl` option is used, the instance will include \
        information on uncertainty, specified in terms of probabilities of \
        transition between abstract states. Every abstract state is identified \
        by the last flight",
    )


def _process_arguments(args):
    # Obtain unsolvable scenarios
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
    pconfig = None
    if args.probabilistic:
        pconfig = ProbConfig(
            args.probabilistic_model == "arrivals",
            1 # window
        )
        if args.probabilistic_model == "ppddl":
            if pconfig.window < 0 or pconfig.window > args.num_flights - 1:
                print(
                    "The length of the state sequece must be strictly positive and cannot be \
                larger than the number of flights, minus one"
                )
                sys.exit(1)

    # Parameters for the script output
    problem_folder = args.out
    if problem_folder is not None and not os.path.isdir(problem_folder):
        print(f"Output folder {problem_folder} does not exists or is not a folder.")
        exit(1)
    problem_name = args.out_name

    res = {
            'config': config,
            'pconfig': pconfig,
            'problem_folder': problem_folder,
            'problem_name': problem_name
            }

    return res



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Beluga random instance generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    _setup_argument_parser(parser)

    # Parse command line arguments
    args = parser.parse_args()

    # Process argument to obtain the problem generator parameters
    gen_params = _process_arguments(args)

    # Start the generation process
    main(gen_params['problem_folder'],
         gen_params['problem_name'],
         gen_params['config'],
         pconfig=gen_params['pconfig'])
