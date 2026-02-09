from .jigs import Jig, JigType

class Flight:

    def __init__(self, name, incoming: list[Jig] = [], outgoing: list[JigType] =[]) -> None:
        self.name = name
        self.incoming : list[Jig] = incoming
        self.outgoing : list[JigType] = outgoing
        self.scheduled_arrival = None


    def add_incoming_jig(self, jigs: list[Jig]):
        self.incoming.append(type)

    def add_outgoing_type(self, type: list[JigType]):
        self.outgoing.append(type)


    def update_incoming(self, jigs: list[Jig]):
        self.incoming = jigs

    def update_outgoing(self, jigs_types: list[JigType]):
        self.outgoing = jigs_types


    def jig_types_fitting_incoming(self, beluga_size: int, jigs_types: list[JigType]) -> bool:
        free_space_in_beluga = beluga_size - sum([j.size() for j in self.incoming])
        return [jt for jt in jigs_types if jt.size_loaded < free_space_in_beluga]

    def incoming_full(self, beluga_size: int, jigs_types: list[JigType]) -> bool:
        free_space_in_beluga = beluga_size - sum([j.size() for j in self.incoming])
        return any([jt.size_loaded < free_space_in_beluga for jt in jigs_types])

    def outgoing_full(self, beluga_size: int, jigs_types: list[JigType]) -> bool:
        free_space_in_beluga = beluga_size - sum([j.size() for j in self.outgoing])
        return any([jt.size_loaded < free_space_in_beluga for jt in jigs_types])

    def fits_outgoing(self, beluga_size: int, jig: Jig) -> bool:
        free_space_in_beluga = beluga_size - sum([j.size() for j in self.outgoing])
        return jig.size() <= free_space_in_beluga

    def __repr__(self):
        return self.name
