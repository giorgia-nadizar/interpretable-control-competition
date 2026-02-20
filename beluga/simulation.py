import argparse
import json
import os
import time

from beluga_lib.beluga_problem import BelugaProblemDecoder
from skd_domains.skd_spddl_domain import SkdSPDDLDomain

from controller import CustomController, RandomController, MedianIndexController


def save_reward_to_file(total_reward, max_steps, domain_seed, controller_seed, problem_name, controller_name):
    """
    Save the final reward to a text file with naming convention based on parameters.
    If file exists, append trailing index.
    """
    # Create final_rewards directory if it doesn't exist
    reward_folder = 'final_rewards'
    if not os.path.exists(reward_folder):
        os.makedirs(reward_folder, exist_ok=True)
    
    # Remove .json extension from problem_name if present for the filename
    problem_base = problem_name.replace('.json', '')
    
    # Base filename format: steps_dseed_cseed_problem_controller.txt
    base_filename = f"steps{max_steps}_ds{domain_seed}_cs{controller_seed}_{problem_base}_{controller_name}.txt"
    
    filepath = os.path.join(reward_folder, base_filename)
    
    # If file exists, add trailing index
    if os.path.exists(filepath):
        index = 1
        while True:
            filename_with_index = f"steps{max_steps}_ds{domain_seed}_cs{controller_seed}_{problem_base}_{controller_name}_{index}.txt"
            filepath = os.path.join(reward_folder, filename_with_index)
            if not os.path.exists(filepath):
                break
            index += 1
    
    # Write only the total reward value to the file
    with open(filepath, 'w') as f:
        f.write(f"{total_reward}")
    
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Beluga simulation with controller",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Mandatory arguments
    parser.add_argument(
        "--max_simulation_steps",
        type=int,
        help="Maximum number of simulation steps"
    )
    
    parser.add_argument(
        "--domain_seed",
        type=int,
        help="Seed for the domain/environment"
    )
    
    parser.add_argument(
        "--controller_seed",
        type=int,
        help="Seed for the controller"
    )
    
    parser.add_argument(
        "--problem_name",
        type=str,
        help="Name of the problem JSON file (will append .json if not present)"
    )
    
    parser.add_argument(
        "--controller_name",
        type=str,
        choices=["random", "median", "custom"],
        help="Controller to use: 'random' for RandomController, 'median' for MedianIndexController, 'custom' for CustomController"
    )
    
    # Optional flags
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--save-final-reward",
        action="store_true",
        help="Save the final reward to a text file in the final_rewards folder"
    )
    
    args = parser.parse_args()
    
    # Process problem_name: add .json if not present
    problem_name = args.problem_name
    if not problem_name.endswith('.json'):
        problem_name = problem_name + '.json'
    
    # Setup problem paths
    problem_folder = 'problems'
    problem_out = os.path.join(problem_folder, problem_name)
    
    # Load problem instance
    with open(problem_out, "r") as fp:
        inst = json.load(fp, cls=BelugaProblemDecoder)

    # Initialize domain
    domain = SkdSPDDLDomain(inst, problem_name, problem_folder, seed=args.domain_seed, classic=True) # type: ignore
    action_space = domain.get_action_space()
    observation_space = domain.get_observation_space()

    # Initialize controller based on controller_name
    if args.controller_name == "random":
        controller = RandomController(domain, seed=args.controller_seed)
        controller_display = "RandomController"
    elif args.controller_name == "median":
        controller = MedianIndexController(domain)
        controller_display = "MedianIndexController"
    elif args.controller_name == "custom":
        controller = CustomController(domain, seed=args.controller_seed)
        controller_display = "CustomController"
    else:
        raise ValueError(f"Unknown controller: {args.controller_name}")

    if args.verbose:
        print(f"Simulating with {controller_display}")
        print(f"Domain seed: {args.domain_seed}, Controller seed: {args.controller_seed}")
        print(f"Problem: {problem_name}, Max steps: {args.max_simulation_steps}")
    
    s = domain.reset()
    if args.verbose:
        print(f"\nInitial state: {s}")
    
    total_reward = 0
    step = 0
    
    start_time = time.time()
    
    while not domain._is_terminal(s) and step < args.max_simulation_steps:
        a = controller.control(s)
        if args.verbose:
            print(f"\nApplying action: {a}")
        
        o = domain.step(a)
        is_terminated = o.termination
        s = o.observation
        r = o.value.reward
        
        if args.verbose:
            print(f"\nCurrent state: {s}")
            print(f"Reward: {r}")
        
        step += 1
        total_reward += r

        if is_terminated:
            if args.verbose:
                print("\nEpisode terminated.")
            break
    
    domain.cleanup()
    
    end_time = time.time()
    
    if args.verbose:
        print(f"Simulation completed in {end_time - start_time:.2f} seconds")
    
    print(f"Total reward: {total_reward}")
    
    # Save final reward if requested
    if args.save_final_reward:
        filepath = save_reward_to_file(
            total_reward,
            args.max_simulation_steps,
            args.domain_seed,
            args.controller_seed,
            problem_name,
            args.controller_name
        )
        print(f"Final reward saved to: {filepath}")


if __name__ == "__main__":
    main()
