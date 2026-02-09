#!/usr/bin/env python

import sys
import json
import argparse
import os

from beluga_lib.beluga_problem import BelugaProblem
from encoder.pddl_encoding import DomainEncoding
from encoder.pddl_encoding import encode
from beluga_lib.beluga_problem import BelugaProblemDecoder
from encoder.pddl_encoding.variant import Variant


def generate_domain(variant: Variant, problem_out, inst=None, domain_name="domain.pddl"):
    domain_encoding = DomainEncoding(variant, inst)
    name = 'beluga'
    if problem_out:
        with open(os.path.join(problem_out, domain_name), 'w') as out_file:
            out_file.write(domain_encoding.domain.to_pddl(name))
    else:
        print(domain_encoding.domain.to_pddl(name))

    return domain_encoding


def generate_problem( variant: Variant, inst: BelugaProblem, problem_name: str, domain_encoding: DomainEncoding, problem_out):
    pddl_problem = encode(problem_name, inst, domain_encoding.domain, variant)

    name = "beluga-" + problem_name
    name = name.replace(".","")
    if problem_out:
        with open(os.path.join(problem_out, problem_name + ".pddl"), 'w') as out_file:
            out_file.write(pddl_problem.to_pddl(name))
    else:
        print(pddl_problem.to_pddl(name))


def main(instance_file, variant: Variant, problem_out):

    with open(instance_file, 'r') as fp:
        inst = json.load(fp, cls=BelugaProblemDecoder)

    problem_name = os.path.basename(instance_file).replace(".json","")
    instance_name = problem_name.replace('problem_', '')

    if variant.probabilistic:
        domain_encoding = generate_domain(variant, problem_out, inst, 'domain_' + problem_name + ".pddl")
    else:
        domain_encoding = generate_domain(variant, problem_out)

    generate_problem(variant, inst, problem_name, domain_encoding, problem_out)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-o', '--problem-out', dest="problem_out", type=str, 
                        required=False, 
                        help='output folder for the problem/domain, the problem \
                        keeps its name, if no folder is specified the pddl \
                        encoding is printed onto stdout')
    parser.add_argument('-i', '--instance', help='JSON file of instance to encode', 
                        required=True)
    parser.add_argument('-n', dest="numeric", 
                        help="numeric encoding, otherwise classic encoding", 
                        action='store_true')
    parser.add_argument('-p', dest="probabilistic", 
                        help="probabilistic encoding", 
                        action='store_true')


    args = parser.parse_args()

    instance_file = args.instance

    problem_out = args.problem_out
    variant = Variant()
    variant.classic = not args.numeric
    variant.probabilistic = args.probabilistic

    main(instance_file, variant, problem_out)
