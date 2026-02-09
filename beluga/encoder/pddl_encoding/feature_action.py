from abc import ABC

from ..pddl.pddl_param import PDDLParam
from ..pddl.pddl_predicate_def import PDDLPredicateDef
from ..pddl.type import Type
from ..pddl.pddl_action import PDDLAction
from .variant import Variant


class FeatureAction(ABC):

    def __init__(
        self,
        variant: Variant,
        types: dict[str:Type],
        constants: dict[str:PDDLParam],
        predicates: dict[str:PDDLPredicateDef],
        functions: dict[str:PDDLPredicateDef],
    ) -> None:
        self.name = None

        self.variant = variant
        self.constants = constants
        self.types = types
        self.predicates = predicates
        self.functions = functions

        self.total_cost = self.register_function("total-cost")

    def create_PDDL_action(self) -> PDDLAction:
        pddl_action = PDDLAction(self.name)

        self.add_basic(pddl_action)

        if self.variant.classic:
            self.add_classic(pddl_action)
        else:
            self.add_numeric(pddl_action)

        return pddl_action

    def register_constant(self, name: str, type: Type) -> PDDLParam:
        if name not in self.constants:
            self.constants[name] = PDDLParam(name, type)

        c = self.constants[name]
        assert c.type == type, (
            'Redefinition of constant "'
            + name
            + '" with different type '
            + str(c.type)
            + " != "
            + str(type)
        )
        return c

    def register_type(self, name: str, base_type: Type = "object") -> Type:
        if name not in self.types:
            self.types[name] = Type(name, base_type)

        t = self.types[name]
        assert t.base_type == base_type, (
            'Redefinition of type "'
            + name
            + '" with different base type '
            + str(t.base_type)
            + " != "
            + str(base_type)
        )
        return t

    def register_predicate(
        self, name: str, *args: PDDLParam, comment=None
    ) -> PDDLPredicateDef:
        if name not in self.predicates:
            self.predicates[name] = PDDLPredicateDef(name, *args, comment=comment)

        p = self.predicates[name]
        assert [e.type for e in p.args] == [e.type for e in list(args)], (
            'Redefinition of predicate "'
            + name
            + '" with different arguments '
            + str(p.args)
            + " != "
            + str(args)
        )

        if p.comment is None:
            p.comment = comment

        return p

    def register_function(
        self, name: str, *args: PDDLParam, comment=None
    ) -> PDDLPredicateDef:
        if name not in self.functions:
            self.functions[name] = PDDLPredicateDef(name, *args, comment=comment)

        f = self.functions[name]
        assert f.args == list(args), (
            'Redefinition of function "'
            + name
            + '" with different arguments '
            + str(f.args)
            + " != "
            + str(args)
        )
        return f

    def add_basic(self, a):
        pass

    def add_classic(self, a):
        pass

    def add_numeric(self, a):
        pass
