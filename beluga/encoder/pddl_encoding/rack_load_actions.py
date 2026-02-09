from .feature_action import FeatureAction
from ..pddl.pddl_predicate_def import PDDLPredicateDef
from ..pddl.type import Type
from ..pddl import PDDLParam, PDDLNumericFluent, PDDLNumericValue
from .variant import Variant


class RackAction(FeatureAction):

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
        self.rack_t = self.register_type("rack", self.loc_t)
        self.side_t = self.register_type("side")
        self.production_line_t = self.register_type("production-line")

        self.jig = PDDLParam("?j", self.jig_t)
        self.next_jig = PDDLParam("?nj", self.jig_t)
        self.trailer = PDDLParam("?t", self.trailer_t)
        self.rack = PDDLParam("?r", self.rack_t)
        self.side = PDDLParam("?s", self.side_t)
        self.other_side = PDDLParam("?os", self.side_t)

        self.location = PDDLParam("?l", self.loc_t)

        self.fside = self.register_constant("fside", self.side_t)
        self.bside = self.register_constant("bside", self.side_t)

        self.inp = self.register_predicate("in", self.jig, self.location)
        self.empty = self.register_predicate("empty", self.location)
        self.at_loc_side = self.register_predicate("at-side", self.location, self.side)
        self.clear = self.register_predicate(
            "clear",
            self.jig,
            self.side,
            comment="there is no jig before "
            + self.jig.name
            + " on the rack when looking from "
            + self.side.name,
        )
        self.equal = PDDLPredicateDef("=", self.side, self.side)
        self.next_to = self.register_predicate(
            "next-to",
            self.jig,
            self.next_jig,
            self.side,
            comment="jig "
            + self.next_jig.name
            + " is before/next to jig "
            + self.jig.name
            + " on the rack when looking from "
            + self.side.name,
        )

        if variant.classic:
            num_t = self.register_type("num")
            num = PDDLParam("?n", num_t)

            self.jig_size = PDDLParam("?jsize", num_t)
            self.free_space_size = PDDLParam("?fspace", num_t)
            self.next_space_size = PDDLParam("?nspace", num_t)

            self.size = self.register_predicate("size", self.jig, num)
            self.free_space = self.register_predicate(
                "free-space",
                self.rack,
                num,
                comment="space available on rack " + self.rack.name,
            )
            self.fit = self.register_predicate(
                "fit",
                self.next_space_size,
                self.jig_size,
                self.free_space_size,
                self.rack,
                comment="on rack "
                + self.rack.name
                + ": "
                + self.next_space_size.name
                + " = "
                + self.jig_size.name
                + " + "
                + self.free_space_size.name,
            )

        else:
            self.size = self.register_function("size", self.jig)
            self.free_space = self.register_function("free-space", self.rack)


class PutDownRackAction(RackAction):

    def __init__(
        self,
        variant: Variant,
        types: dict[str:Type],
        constants: dict[str:PDDLParam],
        predicates: dict[str:PDDLPredicateDef],
        functions: dict[str:PDDLPredicateDef],
    ) -> None:
        super().__init__(variant, types, constants, predicates, functions)
        self.name = "put-down-rack"

    def add_basic(self, a):

        a.add_parameter(self.jig)
        a.add_parameter(self.trailer)
        a.add_parameter(self.rack)
        a.add_parameter(self.side)

        a.add_precondition(self.inp.inst(self.jig, self.trailer))
        a.add_precondition(self.empty.inst(self.rack))
        a.add_precondition(self.at_loc_side.inst(self.trailer, self.side))
        a.add_precondition(self.at_loc_side.inst(self.rack, self.side))

        a.add_effect(self.inp.inst(self.jig, self.rack))
        a.add_effect(self.inp.negated_inst(self.jig, self.trailer))
        a.add_effect(self.empty.inst(self.trailer))
        a.add_effect(self.empty.negated_inst(self.rack))
        a.add_effect(self.clear.inst(self.jig, self.bside))
        a.add_effect(self.clear.inst(self.jig, self.fside))

        a.add_effect(
            PDDLNumericFluent("increase", self.total_cost.inst(), PDDLNumericValue(1))
        )

    def add_classic(self, a):

        a.add_parameter(self.jig_size)
        a.add_parameter(self.free_space_size)
        a.add_parameter(self.next_space_size)

        a.add_precondition(self.size.inst(self.jig, self.jig_size))
        a.add_precondition(self.free_space.inst(self.rack, self.free_space_size))
        a.add_precondition(
            self.fit.inst(
                self.next_space_size, self.jig_size, self.free_space_size, self.rack
            )
        )

        a.add_effect(self.free_space.negated_inst(self.rack, self.free_space_size))
        a.add_effect(self.free_space.inst(self.rack, self.next_space_size))

    def add_numeric(self, a):

        a.add_precondition(
            PDDLNumericFluent(
                ">=",
                PDDLNumericFluent(
                    "-", self.free_space.inst(self.rack), self.size.inst(self.jig)
                ),
                PDDLNumericValue(0),
            )
        )

        a.add_effect(
            PDDLNumericFluent(
                "decrease", self.free_space.inst(self.rack), self.size.inst(self.jig)
            )
        )


class StackRackAction(RackAction):

    def __init__(
        self,
        variant: Variant,
        types: dict[str:Type],
        constants: dict[str:PDDLParam],
        predicates: dict[str:PDDLPredicateDef],
        functions: dict[str:PDDLPredicateDef],
    ) -> None:
        super().__init__(variant, types, constants, predicates, functions)
        self.name = "stack-rack"

    def add_basic(self, a):

        a.add_parameter(self.jig)
        a.add_parameter(self.next_jig)
        a.add_parameter(self.trailer)
        a.add_parameter(self.rack)
        a.add_parameter(self.side)
        a.add_parameter(self.other_side)

        a.add_precondition(self.equal.negated_inst(self.side, self.other_side))
        a.add_precondition(self.inp.inst(self.jig, self.trailer))
        a.add_precondition(self.inp.inst(self.next_jig, self.rack))
        a.add_precondition(self.at_loc_side.inst(self.trailer, self.side))
        a.add_precondition(self.at_loc_side.inst(self.rack, self.side))
        a.add_precondition(self.clear.inst(self.next_jig, self.side))

        a.add_effect(self.inp.inst(self.jig, self.rack))
        a.add_effect(self.inp.negated_inst(self.jig, self.trailer))
        a.add_effect(self.empty.inst(self.trailer))
        a.add_effect(self.clear.negated_inst(self.next_jig, self.side))
        a.add_effect(self.clear.inst(self.jig, self.side))
        a.add_effect(self.next_to.inst(self.jig, self.next_jig, self.side))
        a.add_effect(self.next_to.inst(self.next_jig, self.jig, self.other_side))

        a.add_effect(
            PDDLNumericFluent("increase", self.total_cost.inst(), PDDLNumericValue(1))
        )

    def add_classic(self, a):

        a.add_parameter(self.jig_size)
        a.add_parameter(self.free_space_size)
        a.add_parameter(self.next_space_size)

        a.add_precondition(self.size.inst(self.jig, self.jig_size))
        a.add_precondition(self.free_space.inst(self.rack, self.free_space_size))
        a.add_precondition(
            self.fit.inst(
                self.next_space_size, self.jig_size, self.free_space_size, self.rack
            )
        )

        a.add_effect(self.free_space.negated_inst(self.rack, self.free_space_size))
        a.add_effect(self.free_space.inst(self.rack, self.next_space_size))

    def add_numeric(self, a):

        a.add_precondition(
            PDDLNumericFluent(
                ">=",
                PDDLNumericFluent(
                    "-", self.free_space.inst(self.rack), self.size.inst(self.jig)
                ),
                PDDLNumericValue(0),
            )
        )

        a.add_effect(
            PDDLNumericFluent(
                "decrease", self.free_space.inst(self.rack), self.size.inst(self.jig)
            )
        )


class PickUpRackAction(RackAction):

    def __init__(
        self,
        variant: Variant,
        types: dict[str:Type],
        constants: dict[str:PDDLParam],
        predicates: dict[str:PDDLPredicateDef],
        functions: dict[str:PDDLPredicateDef],
    ) -> None:
        super().__init__(variant, types, constants, predicates, functions)
        self.name = "pick-up-rack"

    def add_basic(self, a):
        a.add_parameter(self.jig)
        a.add_parameter(self.trailer)
        a.add_parameter(self.rack)
        a.add_parameter(self.side)
        a.add_parameter(self.other_side)

        a.add_precondition(self.equal.negated_inst(self.side, self.other_side))
        a.add_precondition(self.empty.inst(self.trailer))
        a.add_precondition(self.inp.inst(self.jig, self.rack))
        a.add_precondition(self.at_loc_side.inst(self.trailer, self.side))
        a.add_precondition(self.at_loc_side.inst(self.rack, self.side))

        a.add_precondition(self.clear.inst(self.jig, self.bside))
        a.add_precondition(self.clear.inst(self.jig, self.fside))

        a.add_effect(self.inp.inst(self.jig, self.trailer))
        a.add_effect(self.inp.negated_inst(self.jig, self.rack))
        a.add_effect(self.empty.inst(self.rack))
        a.add_effect(self.empty.negated_inst(self.trailer))

        a.add_effect(self.clear.negated_inst(self.jig, self.bside))
        a.add_effect(self.clear.negated_inst(self.jig, self.fside))

        a.add_effect(
            PDDLNumericFluent("increase", self.total_cost.inst(), PDDLNumericValue(1))
        )

    def add_classic(self, a):

        a.add_parameter(self.jig_size)
        a.add_parameter(self.free_space_size)
        a.add_parameter(self.next_space_size)

        a.add_precondition(self.size.inst(self.jig, self.jig_size))
        a.add_precondition(self.free_space.inst(self.rack, self.free_space_size))
        a.add_precondition(
            self.fit.inst(
                self.free_space_size, self.jig_size, self.next_space_size, self.rack
            )
        )

        a.add_effect(self.free_space.inst(self.rack, self.next_space_size))
        a.add_effect(self.free_space.negated_inst(self.rack, self.free_space_size))

    def add_numeric(self, a):

        a.add_effect(
            PDDLNumericFluent(
                "increase", self.free_space.inst(self.rack), self.size.inst(self.jig)
            )
        )


class UnStackRackAction(RackAction):

    def __init__(
        self,
        variant: Variant,
        types: dict[str:Type],
        constants: dict[str:PDDLParam],
        predicates: dict[str:PDDLPredicateDef],
        functions: dict[str:PDDLPredicateDef],
    ) -> None:
        super().__init__(variant, types, constants, predicates, functions)
        self.name = "unstack-rack"

    def add_basic(self, a):

        a.add_parameter(self.jig)
        a.add_parameter(self.next_jig)
        a.add_parameter(self.trailer)
        a.add_parameter(self.rack)
        a.add_parameter(self.side)
        a.add_parameter(self.other_side)

        a.add_precondition(self.equal.negated_inst(self.side, self.other_side))
        a.add_precondition(self.empty.inst(self.trailer))
        a.add_precondition(self.inp.inst(self.jig, self.rack))
        a.add_precondition(self.inp.inst(self.next_jig, self.rack))
        a.add_precondition(self.at_loc_side.inst(self.trailer, self.side))
        a.add_precondition(self.at_loc_side.inst(self.rack, self.side))
        a.add_precondition(self.clear.inst(self.jig, self.side))
        a.add_precondition(self.next_to.inst(self.jig, self.next_jig, self.side))
        a.add_precondition(self.next_to.inst(self.next_jig, self.jig, self.other_side))

        a.add_effect(self.inp.inst(self.jig, self.trailer))
        a.add_effect(self.inp.negated_inst(self.jig, self.rack))
        a.add_effect(self.empty.negated_inst(self.trailer))
        a.add_effect(self.next_to.negated_inst(self.jig, self.next_jig, self.side))
        a.add_effect(
            self.next_to.negated_inst(self.next_jig, self.jig, self.other_side)
        )
        a.add_effect(self.clear.inst(self.next_jig, self.side))

        a.add_effect(
            PDDLNumericFluent("increase", self.total_cost.inst(), PDDLNumericValue(1))
        )

    def add_classic(self, a):

        a.add_parameter(self.jig_size)
        a.add_parameter(self.free_space_size)
        a.add_parameter(self.next_space_size)

        a.add_precondition(self.size.inst(self.jig, self.jig_size))
        a.add_precondition(self.free_space.inst(self.rack, self.free_space_size))
        a.add_precondition(
            self.fit.inst(
                self.free_space_size, self.jig_size, self.next_space_size, self.rack
            )
        )

        a.add_effect(self.free_space.inst(self.rack, self.next_space_size))
        a.add_effect(self.free_space.negated_inst(self.rack, self.free_space_size))

    def add_numeric(self, a):

        a.add_effect(
            PDDLNumericFluent(
                "increase", self.free_space.inst(self.rack), self.size.inst(self.jig)
            )
        )
