from .type import Type


class PDDLParam:
    def __init__(self, name: str, type: Type):
        self.name = name
        self.type = type

    def __repr__(self) -> str:
        return f"{self.name} - {self.type}"

    def to_pddl(self) -> str:
        return f"{self.name} - {self.type.name}"

    def __eq__(self, __value: object) -> bool:
        return self.name == __value.name and self.type == __value.type

    def __lt__(self, __value: object) -> bool:
        return self.to_pddl().__lt__(__value.to_pddl())

    def __hash__(self) -> int:
        return str(self).__hash__()


class PDDLNumericValue:
    def __init__(self, value: int):
        self.value = value

    def to_pddl(self) -> str:
        return f"{str(self.value)}"

    def __repr__(self) -> str:
        return f"{str(self.value)}"
