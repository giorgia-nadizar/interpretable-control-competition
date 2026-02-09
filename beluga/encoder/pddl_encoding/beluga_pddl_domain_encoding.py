from .feature_action import FeatureAction
from .beluga_complete_action import BelugaCompleteAction
from .factory_actions import DeliverToHangarAction, GetFromHangarAction
from .rack_load_actions import (
    PickUpRackAction,
    PutDownRackAction,
    StackRackAction,
    UnStackRackAction,
)
from .beluga_actions import LoadBelugaAction, UnloadBelugaAction
from .probabilistic_actions import ProceedToNextBeluga
from ..pddl.pddl_domain import PDDLDomain
from .variant import Variant
# from beluga_lib.problem_def import BelugaProblem
from beluga_lib.beluga_problem import BelugaProblem


class DomainEncoding:

    def __init__(self, variant: Variant, beluga_problem: BelugaProblem) -> None:

        self.domain = PDDLDomain()

        if not variant.classic:
            self.domain.requirements.append(":fluents")

        if variant.probabilistic:
            self.domain.requirements.append(":probabilistic-effects")
            self.domain.requirements.append(":conditional-effects")
            self.domain.requirements.append(":negative-preconditions")

        self.constants = {}
        self.types = {}
        self.predicates = {}
        self.functions = {}

        feature_actions_collection = [
            LoadBelugaAction,
            UnloadBelugaAction,
            GetFromHangarAction,
            DeliverToHangarAction,
            PutDownRackAction,
            StackRackAction,
            PickUpRackAction,
            UnStackRackAction,
        ]

        if not variant.probabilistic:
            feature_actions_collection.append(BelugaCompleteAction)

        for feature_action_con in feature_actions_collection:
            fa: FeatureAction = feature_action_con(
                variant, self.types, self.constants, self.predicates, self.functions
            )
            self.domain.actions.append(fa.create_PDDL_action())

        if variant.probabilistic:
            fa = ProceedToNextBeluga(
                variant,
                beluga_problem,
                self.types,
                self.constants,
                self.predicates,
                self.functions,
            )
            self.domain.actions.extend(fa.create_PDDL_action())

        self.domain.types = self.types
        self.domain.constants = self.constants
        self.domain.predicates = self.predicates
        self.domain.functions = self.functions
