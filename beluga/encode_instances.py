#!/usr/bin/env python

import os
import argparse

from json2PDDL import main as run
from encoder.pddl_encoding.variant import Variant

parser = argparse.ArgumentParser(description="Encode json problem in PDDL")

parser.add_argument('-n', dest="numeric", help="numeric encoding", action='store_true')
parser.add_argument('-p', dest="probabilistic", help="probabilistic encoding", action='store_true')
parser.add_argument('-i', help="inout folder of json problem definitions", default=None, required=True)
parser.add_argument('-o', help="output folder to store the domain file and problem files", default=None, required=True)
parser.add_argument('-y', dest="no_questions", help="just run", action='store_true' , required=False)

args = parser.parse_args()

variant = Variant()
variant.classic = not args.numeric
variant.probabilistic = args.probabilistic
input_folder = args.i
if not os.path.isdir(input_folder):
    print(f"Input folder {input_folder} does not exists or is not a folder.")
    exit(1)
out_folder = args.o
if not os.path.isdir(out_folder):
    print(f"Output folder {out_folder} does not exists or is not a folder.")
    exit(1)


final_num_instances = len(os.listdir(input_folder))

if not args.no_questions:
    print("Do you want to encode " + str(final_num_instances) + " instances? y/n")
    answer = input()

    if answer != "y":
        exit()

num_instances = 0

os.system("rm -f " + out_folder + "/*")

for problem in os.listdir(input_folder):
    if num_instances % 10 == 0 and num_instances > 0:
        print(str(num_instances) + "/" + str(final_num_instances))
    run(os.path.join(input_folder, problem), variant, out_folder)
    num_instances += 1

print("Number of encoded instances: " + str(num_instances))

