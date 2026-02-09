from .pddl_param import PDDLParam
from .pddl_numeric_fluent import PDDLNumericFluent
from .pddl_literal import PDDLLiteral


class PDDLPredicate(PDDLLiteral):
    def __init__(self, name: str, *args: PDDLParam, negated: bool = False):
        self.name = name
        self.args = list(args)
        self.negated = negated

    def to_pddl(self) -> str:
        s = ""
        if self.negated:
            s += "(not "
        s += f"({self.name} {' '.join([str(a.name) for a in self.args])})"
        if self.negated:
            s += ")"
        return s

    def to_prefix(self) -> str:
        if self.negated:
            exit(1)
        return f"{self.name}({','.join([str(a) for a in self.args])})"

    def __repr__(self) -> str:
        s = ""
        if self.negated:
            s += "(not "
        s += f"({self.name} {' '.join([str(a) for a in self.args])})"
        if self.negated:
            s += ")"
        return s

    def __hash__(self) -> int:
        return str(self).__hash__()

    def __eq__(self, __value: object) -> bool:
        return (
            self.name == __value.name
            and self.args == __value.args
            and self.negated == __value.negated
        )

    def __lt__(self, __value: object) -> bool:
        if type(__value) == PDDLNumericFluent:
            return True

        if self.negated and type(__value) == PDDLPredicate:
            return False
        if not self.negated and type(__value) == PDDLPredicate and __value.negated:
            return True
        return self.to_pddl().__lt__(__value.to_pddl())
