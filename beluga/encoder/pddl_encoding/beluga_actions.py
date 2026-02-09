from ..pddl.pddl_predicate_def import PDDLPredicateDef
from ..pddl.type import Type
from ..pddl_encoding.feature_action import FeatureAction
from ..pddl import PDDLParam, PDDLNumericFluent, PDDLNumericValue
from .variant import Variant


class BelugaAction(FeatureAction):

    def __init__(
        self,
        variant: Variant,
        types: dict[str:Type],
        constants: dict[str:PDDLParam],
        predicates: dict[str:PDDLPredicateDef],
        functions: dict[str:PDDLPredicateDef],
    ) -> None:
        super().__init__(variant, types, constants, predicates, functions)

        self.loc_t = self.register_type("location")
        self.jig_t = self.register_type("jig", self.loc_t)
        self.beluga_t = self.register_type("beluga", self.loc_t)
        self.trailer_t = self.register_type("trailer", self.loc_t)
        self.side_t = self.register_type("side")

        self.jig = PDDLParam("?j", self.jig_t)
        self.beluga = PDDLParam("?b", self.beluga_t)
        self.trailer = PDDLParam("?t", self.trailer_t)

        self.bside = self.register_constant("bside", self.side_t)
        self.side = PDDLParam("?s", self.side_t)
        self.location = PDDLParam("?l", self.loc_t)

        self.inp = self.register_predicate("in", self.jig, self.location)
        self.empty = self.register_predicate("empty", self.location)
        self.at_loc_side = self.register_predicate(
            "at-side",
            self.location,
            self.side,
            comment="location l? accessible from side ?s",
        )
        self.processed_flight = self.register_predicate(
            "processed-flight",
            self.beluga,
            comment="Beluga " + self.beluga.name + " is currently loaded/unloaded",
        )


class UnloadBelugaAction(BelugaAction):

    def __init__(
        self,
        variant: Variant,
        types: dict[str:Type],
        constants: dict[str:PDDLParam],
        predicates: dict[str:PDDLPredicateDef],
        functions: dict[str:PDDLPredicateDef],
    ) -> None:
        super().__init__(variant, types, constants, predicates, functions)
        self.name = "unload-beluga"

        self.next_jig = PDDLParam("?nj", self.jig_t)

    def add_basic(self, a):

        a.add_parameter(self.jig)
        a.add_parameter(self.next_jig)
        a.add_parameter(self.trailer)
        a.add_parameter(self.beluga)

        self.to_unload = self.register_predicate(
            "to_unload",
            self.jig,
            self.beluga,
            comment="jig "
            + self.jig.name
            + " must be next unload from Beluga "
            + self.beluga.name,
        )
        self.next_unload = self.register_predicate(
            "next_unload",
            self.jig,
            self.next_jig,
            comment=self.next_jig.name
            + " is successor "
            + self.jig.name
            + " in unload order",
        )

        a.add_precondition(self.inp.inst(self.jig, self.beluga))
        a.add_precondition(self.empty.inst(self.trailer))
        a.add_precondition(self.at_loc_side.inst(self.trailer, self.bside))
        a.add_precondition(self.processed_flight.inst(self.beluga))
        a.add_precondition(self.to_unload.inst(self.jig, self.beluga))
        a.add_precondition(self.next_unload.inst(self.jig, self.next_jig))

        a.add_effect(self.inp.negated_inst(self.jig, self.beluga))
        a.add_effect(self.inp.inst(self.jig, self.trailer))
        a.add_effect(self.empty.negated_inst(self.trailer))
        a.add_effect(self.to_unload.negated_inst(self.jig, self.beluga))
        a.add_effect(self.to_unload.inst(self.next_jig, self.beluga))

        a.add_effect(
            PDDLNumericFluent("increase", self.total_cost.inst(), PDDLNumericValue(1))
        )


class LoadBelugaAction(BelugaAction):

    def __init__(
        self,
        variant: Variant,
        types: dict[str:Type],
        constants: dict[str:PDDLParam],
        predicates: dict[str:PDDLPredicateDef],
        functions: dict[str:PDDLPredicateDef],
    ) -> None:
        super().__init__(variant, types, constants, predicates, functions)
        self.name = "load-beluga"

        self.type_t = self.register_type("type")
        self.slot_t = self.register_type("slot")
        self.side_t = self.register_type("side")

        self.jig_type = PDDLParam("?jt", self.type_t)
        self.next_jig_type = PDDLParam("?njt", self.type_t)

        self.slot = PDDLParam("?s", self.slot_t)
        self.next_slot = PDDLParam("?ns", self.slot_t)

        self.inp = self.register_predicate("in", self.jig, self.location)
        self.empty = self.register_predicate("empty", self.location)
        self.at_loc_side = self.register_predicate(
            "at-side",
            self.location,
            self.side,
            comment="self.location l? accessible from side ?s",
        )
        self.is_type = self.register_predicate("is_type", self.jig, self.jig_type)
        self.processed_flight = self.register_predicate(
            "processed-flight",
            self.beluga,
            comment="Beluga " + self.beluga.name + " is currently loaded/unloaded",
        )
        self.to_load = self.register_predicate(
            "to_load", self.jig_type, self.slot, self.beluga
        )
        self.next_load = self.register_predicate(
            "next_load", self.jig_type, self.slot, self.next_slot, self.beluga
        )

    def add_basic(self, a):

        a.add_parameter(self.jig)
        a.add_parameter(self.jig_type)
        a.add_parameter(self.next_jig_type)
        a.add_parameter(self.beluga)
        a.add_parameter(self.trailer)
        a.add_parameter(self.slot)
        a.add_parameter(self.next_slot)

        a.add_precondition(self.inp.inst(self.jig, self.trailer))
        a.add_precondition(self.empty.inst(self.jig))
        a.add_precondition(self.is_type.inst(self.jig, self.jig_type))
        a.add_precondition(self.processed_flight.inst(self.beluga))
        a.add_precondition(self.to_load.inst(self.jig_type, self.slot, self.beluga))
        a.add_precondition(
            self.next_load.inst(
                self.next_jig_type, self.slot, self.next_slot, self.beluga
            )
        )
        a.add_precondition(self.at_loc_side.inst(self.trailer, self.bside))

        a.add_effect(self.inp.inst(self.jig, self.beluga))
        a.add_effect(self.inp.negated_inst(self.jig, self.trailer))
        a.add_effect(self.empty.inst(self.trailer))
        a.add_effect(self.to_load.negated_inst(self.jig_type, self.slot, self.beluga))
        a.add_effect(self.to_load.inst(self.next_jig_type, self.next_slot, self.beluga))

        a.add_effect(
            PDDLNumericFluent("increase", self.total_cost, PDDLNumericValue(1))
        )
