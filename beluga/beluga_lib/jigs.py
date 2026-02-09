class JigType:

    def __init__(self, name: str, size_empty: int, size_loaded: int) -> None:
        self.name = name
        self.size_empty = size_empty
        self.size_loaded = size_loaded

    def __repr__(self):
        return  self.name + " (" + str(self.size_empty) + \
        "/" + str(self.size_loaded) + ")" 

    def __str__(self):
        return self.name


class Jig:

    def __init__(self, name: str, type: JigType, empty=False) -> None:
        self.name = name
        self.type = type
        self.empty = empty

    def size(self) -> int:
        return self.type.size_empty if self.empty else self.type.size_loaded

    def __repr__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if isinstance(other, Jig):
            return self.name == other.name
        return False
