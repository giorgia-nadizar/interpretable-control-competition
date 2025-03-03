import time

import gymnasium as gym
import ale_py
gym.register_envs(ale_py)

from controller import RandomController


def main():
    # Possible Observation Types: ['ram', 'rgb', 'grayscale'].
    # Possible Modes: [0, 1] - Possible Difficulties: [0, 1, 2, 3].
    # Possible Render Modes: [human, rgb_array]
    # The gym environment parameters are fixed to these values for the competition.
    env = gym.make("Pong-v4", mode=0, difficulty=0, obs_type='rgb', render_mode='human', full_action_space=False)

    # random controller: it picks random actions at every step.
    controller = RandomController(env.action_space)
    
    # evaluation loop: first reset, then iteration until the end of the game.
    observation, info = env.reset(seed=0)
    total_reward = 0

    start_time = time.time()

    while True: # The first agent scoring 21 goals wins
        action = controller.control(observation)
        observation, reward, terminated, truncated, info = env.step(action)
        env.render()

        total_reward += reward

        if terminated or truncated:
            break

    env.close()

    end_time = time.time()
    print(f"Game Time:\t{round(end_time - start_time, 4)} seconds.")
    print(f"Total Reward:\t{total_reward}.")


if __name__ == '__main__':
    main()

