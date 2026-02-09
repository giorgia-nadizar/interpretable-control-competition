from .pddl_literal import PDDLLiteral


class PDDLNumericFluent(PDDLLiteral):
    def __init__(self, operation: str, *args: PDDLLiteral):
        self.args = list(args)
        self.operation = operation

    def __repr__(self) -> str:
        return "(" + ",".join(p.to_pddl() for p in self.args) + ") " + self.operation

    def to_pddl(self) -> str:
        return (
            "("
            + self.operation
            + " "
            + " ".join([p.to_pddl() for p in self.args])
            + ")"
        )

    def __eq__(self, value) -> bool:
        return str(self) == str(value)

    def __hash__(self) -> int:
        return str(self).__hash__()

    def __lt__(self, __value: object) -> bool:
        if not type(__value) == PDDLNumericFluent:
            return False
        return self.to_pddl().__lt__(__value.to_pddl())
