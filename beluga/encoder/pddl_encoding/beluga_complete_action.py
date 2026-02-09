from ..pddl.pddl_predicate_def import PDDLPredicateDef
from ..pddl.type import Type
from ..pddl_encoding.feature_action import FeatureAction
from ..pddl import PDDLParam, PDDLNumericFluent, PDDLNumericValue
from .variant import Variant


class BelugaCompleteAction(FeatureAction):

    def __init__(
        self,
        variant: Variant,
        types: dict[str:Type],
        constants: dict[str:PDDLParam],
        predicates: dict[str:PDDLPredicateDef],
        functions: dict[str:PDDLPredicateDef],
    ) -> None:
        super().__init__(variant, types, constants, predicates, functions)
        self.name = "beluga-complete"

        self.loc_t = self.register_type("location")
        self.beluga_t = self.register_type("beluga", self.loc_t)
        self.jig_t = self.register_type("jig", self.loc_t)
        self.type_t = self.register_type("type")
        self.slot_t = self.register_type("slot")

        self.beluga = PDDLParam("?b", self.beluga_t)
        self.next_beluga = PDDLParam("?nb", self.beluga_t)
        self.jig = PDDLParam("?j", self.jig_t)
        self.jig_type = PDDLParam("?jt", self.type_t)
        self.slot = PDDLParam("?s", self.slot_t)

        self.dummy_jig = self.register_constant("dummy-jig", self.jig_t)
        self.dummy_type = self.register_constant("dummy-type", self.type_t)
        self.dummy_slot = self.register_constant("dummy-slot", self.slot_t)

        self.processed_flight = self.register_predicate(
            "processed-flight",
            self.beluga,
            comment="Beluga " + self.beluga.name + " is currently loaded/unloaded",
        )
        self.next_flight_to_process = self.register_predicate(
            "next-flight-to-process",
            self.beluga,
            self.next_beluga,
            comment=self.next_beluga.name + " is the next flight to be processed",
        )
        self.to_unload = self.register_predicate("to_unload", self.jig, self.beluga)
        self.to_load = self.register_predicate(
            "to_load",
            self.jig_type,
            self.slot,
            self.beluga,
            comment="jig of type "
            + self.jig_type.name
            + " must be loaded into slot "
            + self.slot.name
            + " Beluga "
            + self.beluga.name,
        )

    def add_basic(self, a):

        a.add_parameter(self.beluga)
        a.add_parameter(self.next_beluga)

        a.add_precondition(self.processed_flight.inst(self.beluga))
        a.add_precondition(
            self.next_flight_to_process.inst(self.beluga, self.next_beluga)
        )
        a.add_precondition(self.to_unload.inst(self.dummy_jig, self.beluga))
        a.add_precondition(
            self.to_load.inst(self.dummy_type, self.dummy_slot, self.beluga)
        )

        a.add_effect(self.processed_flight.negated_inst(self.beluga))
        a.add_effect(self.processed_flight.inst(self.next_beluga))

        a.add_effect(
            PDDLNumericFluent("increase", self.total_cost.inst(), PDDLNumericValue(1))
        )
