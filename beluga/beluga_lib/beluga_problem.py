from typing import Dict
import json

from .jigs import Jig, JigType
from .rack import Rack
from .trailer import Trailer
from .production_line import ProductionLine
from .flight_schedule import Flight

class BelugaProblem:

    def __init__(self):

        self.trailers_beluga : list[Trailer] = []
        self.trailers_factory : list[Trailer] = []
        self.hangars : list[str] =  []

        self.racks : list[Rack] = []

        self.jigs : Dict[str, Jig] = {}
        self.jig_types: Dict[str, JigType] = {}

        self.flights : list[Flight] = []

        self.production_lines : list[ProductionLine] = []

        # self.transition_tables: dict[tuple[str], dict[str, Fraction]] = {}
        # self.transition_tables: dict[tuple[str], dict[str, float]] = {}
        self.tt_last : list[tuple[str]] = None
        self.tt_next : list[str] = None
        self.tt_prob : list[float] = None


    def occupancy_rate(self) -> float:
        ocr = []
        for rack in self.racks:
            o = rack.occupied_space()
            ocr.append(o/rack.size)
        return sum(ocr)/len(ocr)




class BelugaProblemEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (Rack, JigType, ProductionLine, Trailer)):
            return obj.__dict__
        if isinstance(obj, Jig):
            return obj.name
        if isinstance(obj, BelugaProblem):
            res = {
                'trailers_beluga': obj.trailers_beluga,
                'trailers_factory': obj.trailers_factory,
                'hangars': obj.hangars,
                'jig_types': obj.jig_types,
                'racks': obj.racks,
                'jigs': {j.name:
                        {
                            'name': j.name,
                            'type': j.type.name,
                            'empty': j.empty,
                        }
                        for j in obj.jigs.values()
                },
                'production_lines': obj.production_lines,
                'flights': [
                    {
                        'name': f.name,
                        'incoming': [j.name for j in f.incoming],
                        'outgoing': [t.name for t in f.outgoing],
                    }
                    for f in obj.flights
                ]
                # **({
                #     'transition_tables':  [
                #         {
                #             "last": [
                #                 list(h) + [None] * (max(
                #                     (len(h) + 1 for h in obj.transition_tables)
                #                 ) - len(h) - h_len)
                #                 for h in obj.transition_tables if len(h) == h_len
                #                 for _ in obj.transition_tables[h]
                #             ],
                #             "next": [
                #                 n 
                #                 for h in obj.transition_tables if len(h) == h_len
                #                 for n in obj.transition_tables[h]
                #             ],
                #             "prob": [
                #                 str(obj.transition_tables[h][n])
                #                 for h in obj.transition_tables if len(h) == h_len
                #                 for n in obj.transition_tables[h]
                #             ]
                #         }
                #         for h_len in range(0, max((len(h) + 1 for h in obj.transition_tables)))
                #     ]
                # } if len(obj.transition_tables) > 0 else {})
            }
            # Add arrival times, if specified
            for k, f in enumerate(obj.flights):
                if f.scheduled_arrival is not None:
                    res['flights'][k]['scheduled_arrival'] = f.scheduled_arrival
            # Add trasition table data, if specified
            if obj.tt_last is not None:
                if obj.tt_next is None:
                    raise ValueError('Inconsistent transition information in the problem object ("tt_next" is None)')
                if obj.tt_prob is None:
                    raise ValueError('Inconsistent transition information in the problem object ("tt_prob" is None)')
                if len(obj.tt_next) != len(obj.tt_last) or len(obj.tt_prob) != len(obj.tt_last):
                    raise ValueError('Inconsistent lengths of transition information lists in the problem object')
                res['tt_last'] = obj.tt_last
                res['tt_next'] = obj.tt_next
                res['tt_prob'] = [float(p) for p in obj.tt_prob]
            # Return the result
            return res
        print(obj)
        return super().default(obj)


class BelugaProblemDecoder(json.JSONDecoder):

    def decode(self, json_str) -> BelugaProblem:
        obj = json.loads(json_str)
        beluga_problem = BelugaProblem()

        beluga_problem.jig_types = {key: JigType(**t) for key, t in obj.get('jig_types', {}).items()}
        beluga_problem.jigs = {
            key:
            Jig(jig["name"], beluga_problem.jig_types[jig['type']], jig['empty']) 
            for key, jig in obj.get('jigs', {}).items()
        }

        beluga_problem.trailers_beluga = [Trailer(**trailer) for trailer in obj.get('trailers_beluga', [])]
        beluga_problem.trailers_factory = [Trailer(**trailer) for trailer in obj.get('trailers_factory', [])]

        beluga_problem.hangars = [h for h in obj.get('hangars', [])]

        beluga_problem.racks = [
            Rack(rack['name'], rack['size'], [beluga_problem.jigs[j] for j in rack['jigs']]) 
            for rack in obj.get('racks', [])\
        ]

        beluga_problem.flights = [
            Flight(
                flight['name'], 
                [beluga_problem.jigs[j] for j in flight['incoming']],
                [beluga_problem.jig_types[j] for j in flight['outgoing']],
            )
            for flight in obj.get('flights', [])
        ]

        # Add scheduled arrivals, if present
        for k, flight in enumerate(obj.get('flights', [])):
            if 'scheduled_arrival' in flight:
                beluga_problem.flights[k].scheduled_arrival = flight['scheduled_arrival']


        beluga_problem.production_lines = [
            ProductionLine(line['name'], [beluga_problem.jigs[j] for j in line['schedule']]) 
            for line in obj.get('production_lines', [])
        ]

        if 'tt_last' in obj:
            if 'tt_next' not in obj:
                raise ValueError('Inconsistent transition information in the problem file (missing "tt_next")')
            if 'tt_prob' not in obj:
                raise ValueError('Inconsistent transition information in the problem file (missing "tt_prob")')
            if len(obj['tt_next']) != len(obj['tt_last']) or len(obj['tt_prob']) != len(obj['tt_last']):
                raise ValueError('Inconsistent lengths of transition information lists in the problem object')
            beluga_problem.tt_last = [tuple(v for v in t) for t in obj['tt_last']]
            beluga_problem.tt_next = [v for v in obj['tt_next']]
            beluga_problem.tt_prob = [float(v) for v in obj['tt_prob']]

        # if 'transition_tables' in obj:
        #     for group in obj['transition_tables']:
        #         for i, h in enumerate(group.get('last', [])):
        #             assert i < len(group.get('next', [])), ("Invalid JSON. "
        #                 "Entry in transition table whose last and next lengths don't match.")
        #             assert i < len(group.get("prob", [])), ("Invalid JSON. "
        #                 "Entry in transition table whose prob and next lengths don't match.")
        #             h = tuple(flight for flight in h if flight is not None)
        #             n = group['next'][i]
        #             p = group['prob'][i]
        #             # beluga_problem.transition_tables.setdefault(h, {})[n] = Fraction(p)
        #             beluga_problem.transition_tables.setdefault(h, {})[n] = float(p)

        return beluga_problem
