from .beluga_problem import BelugaProblem
import json

class BelugaProblemState:

    def __init__(self, prb : BelugaProblem):
        self.prb = prb
        # Internal cached fields
        self.trailer_map = {t.name : t for t in prb.trailers_beluga}
        self.trailer_map.update({t.name : t for t in prb.trailers_factory})
        self.rack_map = {r.name : r for r in prb.racks}
        self.jig_map = prb.jigs
        self.pl_map = {pl.name : pl for pl in prb.production_lines}
        self.flight_map = {f.name : f for f in prb.flights}
        self.hangars = prb.hangars
        # Init all state fields
        self.current_beluga = prb.flights[0]
        self.last_belugas = [self.current_beluga]
        self.beluga_contents = [j for j in prb.flights[0].incoming]
        self.production_line_deliveries = {pl.name: [] for pl in prb.production_lines}
        self.rack_contents = {r.name : r.jigs for r in prb.racks}
        self.trailer_load = {t.name : None for t in prb.trailers_beluga}
        self.trailer_load.update({t.name : None for t in prb.trailers_factory})
        self.jig_empty = {jname : j.empty for jname, j in prb.jigs.items()}
        self.trailer_location = {t.name : ('beluga', None) for t in prb.trailers_beluga}
        self.trailer_location.update({t.name : ('hangar', None) for t in prb.trailers_factory})
        self.hangar_host = {h: None for h in prb.hangars}

    def sfs_current_beluga(self, current_beluga : str):
        if current_beluga not in self.flight_map:
            raise ValueError(f'Invalid current beluga "{current_beluga}"')
        self.current_beluga = self.flight_map[current_beluga]

    def sfs_last_belugas(self, flights : list[str]):
        for f in flights:
            if f not in self.flight_map:
                raise ValueError(f'Invalid flight "{f}"')
        self.last_belugas = [self.flight_map[f] for f in flights]

    def sfs_trailer_load(self, trailer : str, jig : str):
        if trailer not in self.trailer_map:
            raise ValueError(f'Invalid trailer "{trailer}"')
        if jig is not None and jig not in self.jig_map:
            raise ValueError(f'Invalid jig "{jig}"')
        if jig is None:
            self.trailer_load[trailer] = None
        else:
            self.trailer_load[trailer] = self.jig_map[jig]

    def sfs_rack_contents(self, rack : str, jigs : list[str]):
        if rack not in self.rack_map:
            raise ValueError(f'Invalid rack "{rack}"')
        for jig in jigs:
            if jig not in self.jig_map:
                raise ValueError(f'Invalid jig "{jig}"')
        self.rack_contents[rack] = [self.jig_map[j] for j in jigs]

    def sfs_beluga_contents(self, jigs : list[str]):
        for jig in jigs:
            if jig not in self.jig_map:
                raise ValueError(f'Invalid jig "{jig}"')
        self.beluga_contents = [self.jig_map[j] for j in jigs]

    def sfs_production_line_deliveries(self, pl : str, jigs : list[str]):
        if pl not in self.pl_map:
            raise ValueError(f'Invalid production line "{pl}"')
        for jig in jigs:
            if jig not in self.jig_map:
                raise ValueError(f'Invalid jig "{jig}"')
        self.production_line_deliveries[pl] = [self.jig_map[j] for j in jigs]

    def sfs_jig_empty(self, jig: str, empty : bool):
        if jig not in self.jig_map:
            raise ValueError(f'Invalid jig "{jig}"')
        self.jig_empty[jig] = empty

    def sfs_trailer_location(self, trailer : str, loc : str, side : str):
        #TODO fix this
        # if trailer not in self.trailer_map:
        #     raise ValueError(f'Invalid trailer "{trailer}"')
        # if loc != 'beluga' and loc not in self.hangars and loc not in self.rack_map:
        #     raise ValueError(f'Invalid location "{loc}"')
        # if side is not None and side not in ('bside', 'fside'):
        #     raise ValueError(f'Invalid side "{side}"')
        self.trailer_location[trailer] = (loc, side)

    def sfs_hangar_host(self, hangar : str, jig : str):
        if hangar not in self.hangars:
            raise ValueError(f'Invalid hangar "{hangar}"')
        if jig is not None and jig not in self.jig_map:
            raise ValueError(f'Invalid jig "{jig}"')
        self.hangar_host[hangar] = jig

    def from_json_obj(json_obj : dict, prb : BelugaProblem):
        # Start with an initial state
        res = BelugaProblemState(prb)
        # Set current_beluga
        if 'current_beluga' not in json_obj:
            raise ValueError('Invalid state, missing "current_beluga"')
        res.sfs_current_beluga(json_obj['current_beluga'])
        # Set last_belugas
        if 'last_belugas' not in json_obj:
            raise ValueError('Invalid state, missing "last_belugas"')
        res.sfs_last_belugas(json_obj['last_belugas'])
        # Set beluga_contents
        if 'beluga_contents' not in json_obj:
            raise ValueError('Invalid state, missing "beluga_contents"')
        res.sfs_beluga_contents(json_obj['beluga_contents'])
        # Set production_line_deliveries
        if 'production_line_deliveries' not in json_obj:
            raise ValueError('Invalid state, missing "production_line_deliveries"')
        for pl, jigs in json_obj['production_line_deliveries'].items():
            res.sfs_production_line_deliveries(pl, jigs)
        # Set rack_contents
        if 'rack_contents' not in json_obj:
            raise ValueError('Invalid state, missing "rack_contents"')
        for rack, jigs in json_obj['rack_contents'].items():
            res.sfs_rack_contents(rack, jigs)
        # Set trailer_load
        if 'trailer_load' not in json_obj:
            raise ValueError('Invalid state, missing "trailer_load"')
        for trailer, jig in json_obj['trailer_load'].items():
            res.sfs_trailer_load(trailer, jig)
        # Set jig_empty
        if 'jig_empty' not in json_obj:
            raise ValueError('Invalid state, missing "jig_empty"')
        for jig, empty in json_obj['jig_empty'].items():
            res.sfs_jig_empty(jig, empty)
        # Set trailer_location
        if 'trailer_location' not in json_obj:
            raise ValueError('Invalid state, missing "trailer_location"')
        for trailer, (loc, side) in json_obj['trailer_location'].items():
            res.sfs_trailer_location(trailer, loc, side)
        if 'hangar_host' not in json_obj:
            raise ValueError('Invalid state, missing "hangar_host"')
        for hangar, trailer in json_obj['hangar_host'].items():
            res.sfs_hangar_host(hangar, trailer)
        # Return the result
        return res

    def from_json_str(s : str, prb : BelugaProblem):
        return BelugaProblemState.from_json_obj(json.loads(s), prb)

    def to_json_obj(self):
        res = {}
        res['current_beluga'] = self.current_beluga.name
        res['last_belugas'] = [f.name for f in self.last_belugas]
        res['beluga_contents'] = [j.name for j in self.beluga_contents]
        res['production_line_deliveries'] = {plname: [j.name for j in sched] for plname, sched in self.production_line_deliveries.items()}
        res['rack_contents'] = {rname : [j.name for j in jigs] for rname, jigs in self.rack_contents.items()}
        res['trailer_load'] = {tname : (None if not j else j.name) for tname, j in self.trailer_load.items()}
        res['jig_empty'] = {jname : empty for jname, empty in self.jig_empty.items()}
        res['trailer_location'] = {tname : loc for tname, loc in self.trailer_location.items()}
        res['hangar_host'] = {hangar : trailer for hangar, trailer in self.hangar_host.items()}
        return res

    def to_json_str(self, **args):
        return json.dumps(self.to_json_obj(), **args)

    def __repr__(self):
        return self.to_json_str()
