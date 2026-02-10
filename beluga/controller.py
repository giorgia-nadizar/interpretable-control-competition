from __future__ import annotations

import numpy as np

from skdecide.core import D
from skd_domains.skd_spddl_domain import SkdSPDDLDomain


class Controller:
    def __init__(self, domain: SkdSPDDLDomain) -> None:
        self._domain = domain
        self._action_space = self._domain.get_action_space()
        self._observation_space = self._domain.get_observation_space()

    def control(self, observation: D.T_agent[D.T_observation]) -> D.T_agent[D.T_concurrency[D.T_event]]: # type: ignore
        raise NotImplementedError


class RandomController(Controller):

    def __init__(self, domain: SkdSPDDLDomain, seed: int) -> None:
        super().__init__(domain)
        self._rng = np.random.default_rng(seed)

    def control(self, observation: D.T_agent[D.T_observation]) -> D.T_agent[D.T_concurrency[D.T_event]]: # type: ignore
        possible_actions = self._domain.get_applicable_actions(observation).get_elements()
        sampled_action = self._rng.choice(possible_actions)
        return sampled_action
