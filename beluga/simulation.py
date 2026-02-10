#!/usr/bin/env python

import json
import os
import time

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

from controller import RandomController

def main():
    seed = 42
    max_simulation_steps = 100
    problem_folder = 'problem'
    problem_name = 'instance.json'
    problem_out = os.path.join(problem_folder, problem_name)
    with open(problem_out, "r") as fp:
        inst = json.load(fp, cls=BelugaProblemDecoder)

    domain = SkdSPDDLDomain(inst, problem_name, problem_folder, seed=seed) # type: ignore
    action_space = domain.get_action_space()
    observation_space = domain.get_observation_space()

    print("Simulating random actions")
    controller = RandomController(domain, seed=seed)
    s = domain.reset()
    print(f"\nInitial state: {s}")
    total_reward = 0
    step = 0
    
    start_time = time.time()
    
    while not domain._is_terminal(s) and step < (
        max_simulation_steps if max_simulation_steps else 100
    ):
        a = controller.control(s)
        print(f"\nApplying action: {a}")
        o = domain.step(a)
        s = o.observation
        r = o.value.reward
        c = o.value.cost # ignored if reward is used as the optimization criterion, better account for reward only
        print(f"\nCurrent state: {s}")
        print(f"Reward: {r}, Cost: {c}")
        step += 1
        total_reward += r
    print(f"\nTotal reward: {total_reward}")
    domain.cleanup()
    
    end_time = time.time()
    print(f"Simulation completed in {end_time - start_time:.2f} seconds")
    

if __name__ == "__main__":
    main()
