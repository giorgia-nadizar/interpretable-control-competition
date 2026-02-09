import numpy as np
from gymnasium import Space
from gymnasium.core import ActType


class Controller:

    def control(self, observation: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class RandomController(Controller):

    def __init__(self, action_space: Space[ActType]) -> None:
        self.action_space = action_space

    def control(self, observation: np.ndarray) -> np.ndarray:
        return self.action_space.sample()

