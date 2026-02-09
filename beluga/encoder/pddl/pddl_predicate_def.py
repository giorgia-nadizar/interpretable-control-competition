from typing import List
from .pddl_predicate import PDDLPredicate
from .pddl_literal import PDDLLiteral
from .pddl_param import PDDLParam


class PDDLPredicateDef(PDDLLiteral):
    def __init__(self, name: str, *args: PDDLParam, comment=None):
        self.name = name
        self.args: list[PDDLParam] = list(args)
        self.comment = comment

    def __repr__(self) -> str:
        return f"({self.name} {' '.join(arg.to_pddl() for arg in self.args)})"

    def to_pddl(self) -> str:
        if self.comment:
            return f"({self.name} {' '.join(arg.to_pddl() for arg in self.args)}) ; {self.comment}"
        return f"({self.name} {' '.join(arg.to_pddl() for arg in self.args)})"

    def inst(self, *args: PDDLParam):
        for i, arg in enumerate(args):
            assert arg.type.is_subtype(self.args[i].type), (
                "Parameter "
                + str(arg.name)
                + " does not have matching type: "
                + str(arg.type)
                + " != "
                + str(self.args[i].type)
            )
        return PDDLPredicate(self.name, *args)

    def negated_inst(self, *args: PDDLParam):
        for i, arg in enumerate(args):
            assert arg.type.is_subtype(self.args[i].type), (
                "Parameter "
                + str(arg.name)
                + " does not have matching type: "
                + str(arg.type)
                + " != "
                + str(self.args[i].type)
            )
        return PDDLPredicate(self.name, *args, negated=True)

    def __eq__(self, __value: object) -> bool:
        return self.name == __value.name and self.args == __value.args

    def __lt__(self, __value: object) -> bool:
        return self.to_pddl().__lt__(__value.to_pddl())
