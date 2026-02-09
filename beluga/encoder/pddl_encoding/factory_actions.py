from ..pddl.pddl_predicate_def import PDDLPredicateDef
from ..pddl.type import Type
from ..pddl.pddl_predicate import PDDLPredicate
from ..pddl_encoding.feature_action import FeatureAction
from ..pddl import PDDLParam, PDDLNumericFluent, PDDLNumericValue
from .variant import Variant


class hangarAction(FeatureAction):

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
        self.hangar_t = self.register_type("hangar", self.loc_t)
        self.trailer_t = self.register_type("trailer", self.loc_t)
        self.side_t = self.register_type("side")

        self.jig = PDDLParam("?j", self.jig_t)
        self.hangar = PDDLParam("?h", self.hangar_t)
        self.trailer = PDDLParam("?t", self.trailer_t)

        self.location = PDDLParam("?l", self.loc_t)
        self.side = PDDLParam("?s", self.side_t)
        self.fside = self.register_constant("fside", self.side_t)

        self.inp = self.register_predicate("in", self.jig, self.location)
        self.empty = self.register_predicate("empty", self.location)
        self.at_loc_side = self.register_predicate("at-side", self.location, self.side)


class GetFromHangarAction(hangarAction):

    def __init__(
        self,
        variant: Variant,
        types: dict[str:Type],
        constants: dict[str:PDDLParam],
        predicates: dict[str:PDDLPredicateDef],
        functions: dict[str:PDDLPredicateDef],
    ) -> None:
        super().__init__(variant, types, constants, predicates, functions)
        self.name = "get-from-hangar"

    def add_basic(self, a):

        a.add_parameter(self.jig)
        a.add_parameter(self.hangar)
        a.add_parameter(self.trailer)

        a.add_precondition(self.inp.inst(self.jig, self.hangar))
        a.add_precondition(self.empty.inst(self.trailer))
        a.add_precondition(self.at_loc_side.inst(self.trailer, self.fside))

        a.add_effect(self.inp.negated_inst(self.jig, self.hangar))
        a.add_effect(self.inp.inst(self.jig, self.trailer))
        a.add_effect(self.empty.negated_inst(self.trailer))
        a.add_effect(self.empty.inst(self.hangar))

        a.add_effect(
            PDDLNumericFluent("increase", self.total_cost.inst(), PDDLNumericValue(1))
        )


class DeliverToHangarAction(hangarAction):

    def __init__(
        self,
        variant: Variant,
        types: dict[str:Type],
        constants: dict[str:PDDLParam],
        predicates: dict[str:PDDLPredicateDef],
        functions: dict[str:PDDLPredicateDef],
    ) -> None:
        super().__init__(variant, types, constants, predicates, functions)
        self.name = "deliver-to-hangar"

        self.production_line_t = self.register_type("production-line")

        self.production_line = PDDLParam("?pl", self.production_line_t)
        self.next_jig = PDDLParam("?jn", self.jig_t)

    def add_basic(self, a):

        a.add_parameter(self.jig)
        a.add_parameter(self.next_jig)
        a.add_parameter(self.trailer)
        a.add_parameter(self.hangar)
        a.add_parameter(self.production_line)

        self.inp = self.register_predicate("in", self.jig, self.location)
        self.empty = self.register_predicate("empty", self.location)
        self.at_loc_side = self.register_predicate("at-side", self.location, self.side)
        self.to_deliver = self.register_predicate(
            "to_deliver",
            self.jig,
            self.production_line,
            comment="jig "
            + self.jig.name
            + " must be delivered to production line "
            + self.production_line.name,
        )
        self.next_deliver = self.register_predicate(
            "next_deliver",
            self.jig,
            self.next_jig,
            comment=self.next_jig.name
            + " is successor of "
            + self.jig.name
            + " in delivery order to the production line",
        )

        a.add_precondition(self.inp.inst(self.jig, self.trailer))
        a.add_precondition(self.empty.inst(self.hangar))
        a.add_precondition(self.at_loc_side.inst(self.trailer, self.fside))
        a.add_precondition(self.to_deliver.inst(self.jig, self.production_line))
        a.add_precondition(self.next_deliver.inst(self.jig, self.next_jig))

        a.add_effect(self.empty.inst(self.trailer))
        a.add_effect(self.empty.inst(self.jig))
        a.add_effect(self.inp.inst(self.jig, self.hangar))
        a.add_effect(self.inp.negated_inst(self.jig, self.trailer))
        a.add_effect(self.empty.negated_inst(self.hangar))
        a.add_effect(self.to_deliver.negated_inst(self.jig, self.production_line))
        a.add_effect(self.to_deliver.inst(self.next_jig, self.production_line))

        a.add_effect(
            PDDLNumericFluent("increase", self.total_cost.inst(), PDDLNumericValue(1))
        )

    def add_classic(self, a):

        num_t = self.register_type("num")

        num_s = PDDLParam("?s", num_t)
        num_es = PDDLParam("?es", num_t)
        a.add_parameter(num_s)
        a.add_parameter(num_es)

        size = self.register_predicate(
            "size", self.jig, num_s, comment="current size of jig " + self.jig.name
        )
        empty_size = self.register_predicate(
            "empty-size",
            self.jig,
            num_es,
            comment="size of jig "
            + self.jig.name
            + " when it was unloaded in an hangar",
        )

        a.add_precondition(size.inst(self.jig, num_s))
        a.add_precondition(empty_size.inst(self.jig, num_es))

        a.add_effect(size.negated_inst(self.jig, num_s))
        a.add_effect(size.inst(self.jig, num_es))

    def add_numeric(self, a):

        size = self.register_function("size", self.jig)
        empty_size = self.register_function("empty-size", self.jig)

        a.add_effect(
            PDDLNumericFluent("assign", size.inst(self.jig), empty_size.inst(self.jig))
        )
