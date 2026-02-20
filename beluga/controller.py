import random
from skd_domains.skd_base_domain import State, Action
from skd_domains.skd_spddl_domain import SkdSPDDLDomain


class Controller:
    def __init__(self, domain: SkdSPDDLDomain) -> None:
        self._domain = domain
        self._action_space = self._domain.get_action_space()
        self._observation_space = self._domain.get_observation_space()
        
    def domain(self):
        return self._domain
    
    def get_available_actions(self, observation: State) -> list[Action]:
        return self._domain.get_applicable_actions(observation).get_elements()
    
    def action_space(self):
        return self._action_space
    
    def observation_space(self):
        return self._observation_space

    def control(self, observation: State) -> Action:
        raise NotImplementedError


class RandomController(Controller):

    def __init__(self, domain: SkdSPDDLDomain, seed: int) -> None:
        super().__init__(domain=domain)
        self._rng = random.Random(seed)

    def control(self, observation: State) -> Action:
        possible_actions = self.get_available_actions(observation)
        sampled_action = self._rng.choice(possible_actions)
        return sampled_action
    

class MedianIndexController(Controller):
    def __init__(self, domain: SkdSPDDLDomain) -> None:
        super().__init__(domain=domain)

    def control(self, observation: State) -> Action:
        possible_actions = self.get_available_actions(observation)
        median_index = len(possible_actions) // 2
        return possible_actions[median_index]
    

class CustomController(Controller):
    def __init__(self, domain: SkdSPDDLDomain, seed: int) -> None:
        super().__init__(domain=domain)
        self._rng = random.Random(seed)
        # Initialize any additional parameters or state for your custom controller here

    def control(self, observation: State) -> Action:
        # Implement your custom control logic here
        possible_actions = self.get_available_actions(observation)
        # For demonstration, we will just return the first action
        return possible_actions[0]
