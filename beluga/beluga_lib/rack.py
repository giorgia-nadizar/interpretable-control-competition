from .jigs import Jig

class Rack:

    def __init__(self, name: str, size : int, jigs: list[Jig] =[]) -> None:
        self.name: str = name
        self.size: int = size
        # 0: Beluga side
        # -1: factory side
        self.jigs: list[Jig] = jigs

    def is_empty(self) -> bool:
        return len(self.jigs) == 0

    def add_jig_factory_side(self, jig: Jig) -> None:
        self.jigs.append(jig)

    def add_jig_beluga_side(self, jig: Jig) -> None:
        self.jigs.insert(0,jig)

    def next_jig_factory_side(self) -> Jig:
        return self.jigs[-1]

    def next_jig_beluga_side(self) -> Jig:
        return self.jigs[0]

    def fits(self, jig) -> bool:
        return self.free_space() >= jig.size()
    
    def free_space(self) -> int:
        return self.size - self.occupied_space()
    
    def occupied_space(self) -> int:
        return sum([j.size() for j in self.jigs])
    
    def __repr__(self) -> str:
        return self.name 