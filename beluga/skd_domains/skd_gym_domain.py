from typing import Union
from ray.rllib.utils.typing import EnvConfigDict

from skdecide.hub.domain.gym import AsGymnasiumEnv
from skdecide.builders.domain.observability import FullyObservable
from skdecide import RLDomain, TransitionOutcome, Value, Space
from skdecide.hub.space.gym import GymSpace

from numpy.typing import ArrayLike

from .skd_base_domain import SkdBaseDomain
from .skd_pddl_domain import SkdPDDLDomain
from .skd_ppddl_domain import SkdPPDDLDomain
from .skd_spddl_domain import SkdSPDDLDomain


class D(RLDomain, FullyObservable):
    T_state = ArrayLike  # Type of states
    T_observation = T_state  # Type of observations
    T_event = ArrayLike  # Type of events
    T_value = float  # Type of transition values (rewards or costs)
    T_info = None  # Type of additional information in environment outcome


class BelugaGymCompatibleDomain(D):
    """This abstract scikit-decide domain allows the scikit-decide library to automatically
    transforms one of the Beluga scikit-decide domains into a gymnasium environment via the
    BelugaGymEnv class below. Indeed, the 3 Beluga scikit-decide domains, namely SkdPDDLDomain,
    SkdPPDDLDomain and SkdSPDDLDomain, use PDDL-style states and actions that cannot be readily
    understood by reinforcement learning algorithms. We must transform those states and actions
    in a vectorized form (e.g. numpy arrays), which is the intent of this BelugaGymCompatibleDomain
    class.

    Please note that there is no bias in the decision to model the problem using PDDL domains at first.
    The reason for this choice is that the industrial decision-making problem at stake is naturally
    structured using predicates and fluents as in PDDL, and so is the transition logics of the system.

    However, there are many good and poor ways to transform PDDL-style states and actions into tensors.
    This is why this domain class is abstract: it has to be specialized to implement the methods responsible
    for translating from PDDL semantics to tensors and vice versa. The generate_solve_rllib_test.py script
    provides a simplistic example of such a specialized domain class.
    """

    def __init__(
        self, skd_beluga_domain: Union[SkdPDDLDomain, SkdPPDDLDomain, SkdSPDDLDomain]
    ) -> None:
        """Initializes the class

        Args:
            skd_beluga_domain (Union[SkdPDDLDomain, SkdPPDDLDomain, SkdSPDDLDomain]): a Beluga scikit-domain, i.e.
            one of SkdPDDLDomain, SkdPPDDLDomain, or SkdSPDDLDomain
        """
        self.skd_beluga_domain: Union[SkdPDDLDomain, SkdPPDDLDomain, SkdSPDDLDomain] = (
            skd_beluga_domain
        )

    def _state_reset(self) -> D.T_state:
        return self.make_state_array(self.skd_beluga_domain._state_reset())

    def _state_step(
        self, action: D.T_event
    ) -> TransitionOutcome[D.T_state, Value[D.T_value], D.T_predicate, D.T_info]:
        outcome = self.skd_beluga_domain._state_step(self.make_pddl_action(action))
        return TransitionOutcome(
            state=self.make_state_array(outcome.state),
            value=outcome.value,
            termination=outcome.termination,
            info=outcome.info,
        )

    def _get_applicable_actions_from(self, memory: D.T_state) -> Space[D.T_event]:
        return self.skd_beluga_domain._get_applicable_actions_from(
            self.make_pddl_state(memory)
        )

    def make_state_array(self, pddl_state: SkdBaseDomain.T_state) -> ArrayLike:
        """Transform a PDDL state into a tensor state"""
        raise NotImplementedError()

    def make_pddl_state(self, state_array: ArrayLike) -> SkdBaseDomain.T_state:
        """Transform a tensor state into a PDDL state"""
        raise NotImplementedError()

    def make_action_array(self, pddl_action: SkdBaseDomain.T_event) -> ArrayLike:
        """Transform a PDDL action into a tensor action"""
        raise NotImplementedError()

    def make_pddl_action(self, action_array: ArrayLike) -> SkdBaseDomain.T_event:
        """Transform a tensor action into a PDDL action"""
        raise NotImplementedError()

    def _get_observation_space_(self) -> GymSpace[D.T_observation]:
        """Return the observation space whose elements are tensor states returned
        by the make_state_array() method above
        """
        raise NotImplementedError()

    def _get_action_space_(self) -> GymSpace[D.T_event]:
        """Return the action space whose elements are tensor actions returned
        by the make_action_array() method above
        """
        raise NotImplementedError()


class BelugaGymEnv(AsGymnasiumEnv):
    """The Beluga gymnasium environment whose methods are automatically populated
    by scikit-decide from a Gym-compatible Beluga scikit-decide domain passed to
    its constructors. This Gym-compatible Beluga scikit-decide domain must inherit
    from the BelugaGymCompatibleDomain class above.
    A simplistic example of such a inherited domain class can be found in the
    generate_solve_rllib_test.py script.
    """

    def __init__(self, env_config: EnvConfigDict):
        """The constructor of the Beluga gymnasium environment

        Args:
            env_config (EnvConfigDict): Environment configuration dictionary.
            This dictionary must at least contain the 'domain' key which points
            to a scikit-decide domain class inherited from BelugaGymCompatibleDomain.
            The dictionary can also optionally contain the 'unwrap_spaces' key which
            must be equal to True if the scikit-decide domain class uses scikit-decide's
            space classes (such as skdecide.hub.spaces.gym.GymBox) instead of gymnasium
            space classes (such as gym.Box).
        """
        assert "domain" in env_config and isinstance(
            env_config["domain"], BelugaGymCompatibleDomain
        )
        super().__init__(
            env_config["domain"],
            env_config["unwrap_spaces"] if "unwrap_spaces" in env_config else True,
        )
