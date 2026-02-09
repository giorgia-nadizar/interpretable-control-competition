#!/usr/bin/env python

import os
import argparse
import csv

from generator.configurations.default_configuration import  \
    DefaultProblemConfig
from generate_instance import main as run, ProbConfig, UnsolvabilityScenario

parser = argparse.ArgumentParser(description="Generate collection of random Beluga instances")

parser.add_argument(
    '-c', 
    dest="configs_file", 
    help="cvs file with config parameters", 
    required=True
)

parser.add_argument(
    "-s",
    "--seed",
    type=int,
    required=False,
    help="initial seed for the random generator",
    default=1,
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

parser.add_argument(
    '-y', 
    dest="no_questions", 
    help="just run and do not asked for \
        permission after stating number of instances that will be generated", 
    action='store_true' , 
    required=False
    )

parser.add_argument(
    '-o', 
    help="output folder to store problem files", 
    default=None, 
    required=True
)

args = parser.parse_args()

problem_folder = args.o

if not os.path.isdir(problem_folder):
    print(f"Output folder {problem_folder} does not exists or is not a folder.")
    exit(1)

config_parameter_sets = []
with open(args.configs_file) as fp:
    reader = csv.reader(fp, delimiter=',')
    for i, row in enumerate(reader):
        assert(len(row) == 3)
        if i == 0:
            continue
        params = [int(float(s)) for s in row]
        params[0] = params[0] / 100
        config_parameter_sets.append(params)

final_num_instances = len(config_parameter_sets)

unsolvable_scenarios = (
    [] if args.unsolvable_scenario is None else [args.unsolvable_scenario]
)

if args.probabilistic:
    print(f'Generate probabilistic instances with model: {args.probabilistic_model}')

if not args.no_questions:
    print("Do you want to generate " + str(final_num_instances) + " instances? y/n")
    answer = input()

    if answer != "y":
        exit()

os.system("rm " + problem_folder + "/*")

num_instances = 0

print("Number of instances to generate: " + str(final_num_instances))

for i, config_params in enumerate(config_parameter_sets):

    c = DefaultProblemConfig(
        False, # verbose
        args.seed + i, 
        *config_params, 
        unsolvable_scenarios
    )

    if num_instances % 100 == 0 and num_instances > 0:
        print(str(num_instances) + "/" + str(final_num_instances))

    pconfig = None
    if args.probabilistic:
        pconfig = ProbConfig(
            args.probabilistic_model == "arrivals",
            1 # probabilistic window
        )

    valid_problem, name = run(
        problem_folder, 
        None, 
        c, 
        pconfig=pconfig, 
        skip_errors=True, 
        instance_id=num_instances
    )

    num_instances += 1 if valid_problem else 0

print("Number of valid instances: " + str(num_instances))

