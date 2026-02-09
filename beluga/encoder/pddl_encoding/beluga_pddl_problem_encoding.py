# from beluga_lib.problem_def import BelugaProblem
from beluga_lib.beluga_problem import BelugaProblem
from beluga_lib.rack import Rack
from beluga_lib.flight_schedule import Flight
from ..pddl.pddl_domain import PDDLDomain
from ..pddl.pddl_literal import PDDLComment
from ..pddl.pddl_param import PDDLNumericValue
from ..pddl import PDDLProblem, PDDLParam, PDDLNumericFluent
from .variant import Variant
import encoder.utils as utils
from beluga_lib.problem_state import BelugaProblemState
import copy

def _reorder_flights(flights, last_belugas):
    flight_map = {f.name : f for f in flights}
    processed = set([f.name for f in last_belugas])
    res = [flight_map[f.name] for f in last_belugas]
    for f in flights:
        if f.name not in processed:
            res.append(f)
    return res


def encode(
    name: str,
    beluga_problem: BelugaProblem,
    domain: PDDLDomain,
    variant: Variant,
    state : BelugaProblemState = None
) -> PDDLProblem:

    problem = PDDLProblem(name, "beluga")

    # Pick a state
    if state is None:
        state = BelugaProblemState(beluga_problem) # This should be identical to the initial state

    # Reorder flights according to the state content
    beluga_problem = copy.deepcopy(beluga_problem) # NOTE Michele's change
    # print([f.name for f in beluga_problem.flights])
    beluga_problem.flights = _reorder_flights(beluga_problem.flights, state.last_belugas)
    # print([f.name for f in beluga_problem.flights])

    jig_sizes = set(
        [j.size_loaded for j in beluga_problem.jig_types.values()]
        + [p.size_empty for p in beluga_problem.jig_types.values()]
    )
    max_num = max([r.size for r in beluga_problem.racks])

    if variant.classic:
        init_classic_sizes(beluga_problem, problem, domain, jig_sizes, max_num)

    init_trailers(state, problem, domain)
    init_racks(variant, state, problem, domain, max_num)
    init_jigs(variant, beluga_problem, state, problem, domain, max_num)
    init_hangar(beluga_problem, state, problem, domain)

    init_flight_schedule(variant, beluga_problem, state, problem, domain)
    init_incoming(beluga_problem, state, problem, domain)
    init_outgoing(variant, beluga_problem, state, problem, domain)

    init_production_schedule(beluga_problem, state, problem, domain)

    init_flight_history(variant, beluga_problem, problem, domain)

    def_goal(beluga_problem, problem, domain)

    problem.add_init(PDDLComment("Action cost:"))
    problem.add_init(
        PDDLNumericFluent(
            "=", domain.get_function("total-cost").inst(), PDDLNumericValue(0)
        )
    )

    return problem


def init_classic_sizes(
    beluga_problem: BelugaProblem,
    problem: PDDLProblem,
    domain: PDDLDomain,
    jig_sizes,
    max_num,
):

    numbers = set()
    num_t = domain.get_type("num")

    problem.add_init(PDDLComment("Number encoding"))
    fit = domain.get_predicate("fit")
    for rack in beluga_problem.racks:
        problem.add_init(PDDLComment("Sizes fitting rack: " + rack.name))
        for n1 in utils.get_necessary_rack_numbers(jig_sizes, rack.size):
            numbers.add(n1)
            for n2 in jig_sizes:
                if n1 - n2 >= 0:
                    problem.add_init(
                        fit.inst(
                            PDDLParam(
                                " n" + utils.format_number(n1 - n2, max_num), num_t
                            ),
                            PDDLParam(" n" + utils.format_number(n2, max_num), num_t),
                            PDDLParam(" n" + utils.format_number(n1, max_num), num_t),
                            PDDLParam(rack.name, domain.get_type("rack")),
                        )
                    )
    numbers.update(jig_sizes)
    problem.add_object(PDDLComment("Numbers: " + str(numbers)))
    numbers = list(numbers)
    numbers.sort()
    for n in numbers:
        problem.add_object(PDDLParam("n" + utils.format_number(n, max_num), num_t))


def init_trailers(
    state : BelugaProblemState,
    problem: PDDLProblem, 
    domain: PDDLDomain,
):

    trailer_t = domain.get_type("trailer")
    jig_t = domain.get_type("jig")

    problem.add_object(PDDLComment("trailers:"))
    for trailer in state.trailer_location.keys():
        problem.add_object(PDDLParam(trailer, trailer_t))

    problem.add_init(PDDLComment("trailers (Beluga side):"))
    for trailer in state.trailer_map.values():
        trailer_loc, trailer_side = state.trailer_location[trailer.name]
        # if state.trailer_location[trailer.name][0] != 'beluga': # TODO changed by Michele
        if trailer_loc != 'beluga' and trailer_side != 'bside':
            continue

        if state.trailer_load[trailer.name] == None:
            problem.add_init(
                domain.get_predicate("empty").inst(PDDLParam(trailer.name, trailer_t))
            )
        else:
            problem.add_init(
                domain.get_predicate("in").inst(
                    PDDLParam(state.trailer_load[trailer.name], jig_t),
                    PDDLParam(trailer.name, trailer_t),
                )
            )

        problem.add_init(
            domain.get_predicate("at-side").inst(
                PDDLParam(trailer.name, trailer_t), domain.get_constant("bside")
            )
        )

    problem.add_init(PDDLComment("trailers (Factory side):"))
    for trailer in state.trailer_map.values():
        trailer_loc, trailer_side = state.trailer_location[trailer.name]
        # if state.trailer_location[trailer.name][0] == 'beluga': # TODO changed by Michele
        if trailer_loc == 'beluga' or trailer_side == 'bside':
            continue
        if state.trailer_load[trailer.name] == None:
            problem.add_init(
                domain.get_predicate("empty").inst(PDDLParam(trailer.name, trailer_t))
            )
        else:
            problem.add_init(
                domain.get_predicate("in").inst(
                     PDDLParam(state.trailer_load[trailer.name], jig_t),
                    PDDLParam(trailer.name, trailer_t)

                )
            )

        problem.add_init(
            domain.get_predicate("at-side").inst(
                PDDLParam(trailer.name, trailer_t), domain.get_constant("fside")
            )
        )


def init_hangar(
    beluga_problem: BelugaProblem,
    state : BelugaProblemState,
    problem: PDDLProblem, 
    domain: PDDLDomain
):

    hangar_t = domain.get_type("hangar")
    jig_t = domain.get_type("jig")

    problem.add_object(PDDLComment("hangars:"))
    for h in beluga_problem.hangars:
        problem.add_object(PDDLParam(h, hangar_t))

    problem.add_init(PDDLComment("hangars:"))
    for h in beluga_problem.hangars:
        if state.hangar_host[h] == None:
            problem.add_init(domain.get_predicate("empty").inst(PDDLParam(h, hangar_t)))
        else:
            problem.add_init(domain.get_predicate("in").inst(
                PDDLParam(state.hangar_host[h],jig_t),
                PDDLParam(h, hangar_t)) # TODO changed by Michele
            )


def init_racks(
    variant: Variant,
    state : BelugaProblemState,
    problem: PDDLProblem,
    domain: PDDLDomain,
    max_num,
):

    rack_t = domain.get_type("rack")

    problem.add_object(PDDLComment("Racks:"))
    for r in state.rack_map.values():
        problem.add_object(PDDLParam(r.name, rack_t))

    problem.add_init(PDDLComment("Racks " + str(len(state.rack_map))))
    for init_rack in state.rack_map.values():
        
        state_rack = Rack(init_rack.name, init_rack.size, state.rack_contents[init_rack.name])

        problem.add_init(PDDLComment("Rack:" + state_rack.name))
        if len(state_rack.jigs) == 0:
            problem.add_init(
                domain.get_predicate("empty").inst(PDDLParam(state_rack.name, rack_t))
            )

        problem.add_init(
            domain.get_predicate("at-side").inst(
                PDDLParam(state_rack.name, rack_t), domain.get_constant("bside")
            )
        )
        problem.add_init(
            domain.get_predicate("at-side").inst(
                PDDLParam(state_rack.name, rack_t), domain.get_constant("fside")
            )
        )

        free_space = state_rack.free_space()
        assert free_space >= 0, "Rack " + state_rack.name + " contains more jigs than fit!"

        if variant.classic:
            problem.add_init(
                domain.get_predicate("free-space").inst(
                    PDDLParam(state_rack.name, rack_t),
                    PDDLParam(
                        "n" + utils.format_number(free_space, max_num),
                        domain.get_type("num"),
                    ),
                )
            )
        else:
            problem.add_init(
                PDDLNumericFluent(
                    "=",
                    domain.get_function("free-space").inst(
                        PDDLParam(state_rack.name, rack_t)
                    ),
                    PDDLNumericValue(free_space),
                )
            )

        jig_t = domain.get_type("jig")

        for i, jig in enumerate(state_rack.jigs):
            problem.add_init(
                domain.get_predicate("in").inst(
                    PDDLParam(jig, jig_t), PDDLParam(state_rack.name, rack_t)
                )
            )
            if i == 0:
                problem.add_init(
                    domain.get_predicate("clear").inst(
                        PDDLParam(jig.name, jig_t), domain.get_constant("bside")
                    )
                )
            if i < len(state_rack.jigs) - 1:
                problem.add_init(
                    domain.get_predicate("next-to").inst(
                        PDDLParam(jig.name, jig_t),
                        PDDLParam(state_rack.jigs[i + 1], jig_t),
                        domain.get_constant("bside"),
                    )
                )
                problem.add_init(
                    domain.get_predicate("next-to").inst(
                        PDDLParam(state_rack.jigs[i + 1], jig_t),
                        PDDLParam(jig.name, jig_t),
                        domain.get_constant("fside"),
                    )
                )
            if i == len(state_rack.jigs) - 1:
                problem.add_init(
                    domain.get_predicate("clear").inst(
                        PDDLParam(jig.name, jig_t), domain.get_constant("fside")
                    )
                )


def init_jigs(
    variant: Variant,
    beluga_problem: BelugaProblem,
    state : BelugaProblemState,
    problem: PDDLProblem,
    domain: PDDLDomain,
    max_num,
):

    jig_t = domain.get_type("jig")
    jig_type_t = domain.get_type("type")

    problem.add_object(PDDLComment("Jigs:"))
    for j in beluga_problem.jigs.values():
        problem.add_object(PDDLParam(j.name, jig_t))

    for t in beluga_problem.jig_types.values():
        problem.add_object(PDDLParam(t.name, jig_type_t))

    problem.add_init(PDDLComment("Jigs (size):"))
    for jig in beluga_problem.jigs.values():

        problem.add_init(
            domain.get_predicate("is_type").inst(
                PDDLParam(jig.name, jig_t), PDDLParam(jig.type, jig_type_t)
            )
        )

        jig_size  = jig.type.size_empty if state.jig_empty[jig.name] else jig.type.size_loaded

        if variant.classic:
            num_t = domain.get_type("num")
            problem.add_init(
                domain.get_predicate("size").inst(
                    PDDLParam(jig.name, jig_t),
                    PDDLParam("n" + utils.format_number(jig_size, max_num), num_t),
                )
            )
            problem.add_init(
                domain.get_predicate("empty-size").inst(
                    PDDLParam(jig.name, jig_t),
                    PDDLParam(
                        "n" + utils.format_number(jig.type.size_empty, max_num), num_t
                    ),
                )
            )
        else:
            problem.add_init(
                PDDLNumericFluent(
                    "=",
                    domain.get_function("size").inst(PDDLParam(jig.name, jig_t)),
                    PDDLNumericValue(jig_size),
                )
            )
            problem.add_init(
                PDDLNumericFluent(
                    "=",
                    domain.get_function("empty-size").inst(PDDLParam(jig.name, jig_t)),
                    PDDLNumericValue(jig.type.size_empty),
                )
            )

        if state.jig_empty[jig.name]:
            problem.add_init(
                domain.get_predicate("empty").inst(PDDLParam(jig.name, jig_t))
            )


def init_flight_schedule(
    variant: Variant,
    beluga_problem: BelugaProblem,
    state : BelugaProblemState,
    problem: PDDLProblem,
    domain: PDDLDomain,
):

    if variant.probabilistic:
        return

    beluga_t = domain.get_type("beluga")

    problem.add_object(PDDLComment("Beluga flights:"))
    for flight in beluga_problem.flights:
        problem.add_object(PDDLParam(flight.name, beluga_t))

    problem.add_init(PDDLComment("Flight schedule initial phase:"))
    problem.add_init(
        domain.get_predicate("processed-flight").inst(
            PDDLParam(state.current_beluga, beluga_t)
        )
    )

    problem.add_init(PDDLComment("Flight order:"))
    for i in range(len(beluga_problem.flights) - 1):
        problem.add_init(
            domain.get_predicate("next-flight-to-process").inst(
                PDDLParam(beluga_problem.flights[i].name, beluga_t),
                PDDLParam(beluga_problem.flights[i + 1].name, beluga_t),
            )
        )


def init_incoming(
    beluga_problem: BelugaProblem, 
    state : BelugaProblemState,
    problem: PDDLProblem, 
    domain: PDDLDomain
):

    problem.add_init(
        PDDLComment("Number of flights: " + str(len(beluga_problem.flights)))
    )
    problem.add_init(PDDLComment("Incoming jigs unload order:"))

    beluga_t = domain.get_type("beluga")
    jig_t = domain.get_type("jig")

    current_beluga = state.current_beluga
    # current_beluga_index = beluga_problem.flights.index(current_beluga)
    beluga_problem_flights = [f.name for f in beluga_problem.flights] # NOTE changed by Michele
    current_beluga_index = beluga_problem_flights.index(current_beluga.name)

    finished_flights: list[Flight] = beluga_problem.flights[0:current_beluga_index]
    to_process_flights: list[Flight] = beluga_problem.flights[current_beluga_index + 1:] \
        if current_beluga_index < len(beluga_problem.flights) - 1 else []

    problem.add_init(PDDLComment("Finished Flights"))

    if len(finished_flights) == 0:
        problem.add_init(PDDLComment("No already completely finished Flights"))

    for flight in finished_flights:

        problem.add_init(PDDLComment("Flight: " + flight.name))
        problem.add_init(
            PDDLComment(
                " ".join(
                    [str(i) + ": " + j.name for i, j in enumerate(flight.incoming)]
                )
            )
            if len(flight.incoming) > 0
                else 
                    PDDLComment("No jigs")
        )

        problem.add_init(
            domain.get_predicate("to_unload").inst(
                domain.get_constant("dummy-jig"), PDDLParam(flight.name, beluga_t)
            )
        )

        for i, jig in enumerate(flight.incoming):
            if i < len(flight.incoming) - 1:
                problem.add_init(
                    domain.get_predicate("next_unload").inst(
                        PDDLParam(jig.name, jig_t),
                        PDDLParam(flight.incoming[i + 1], jig_t),
                    )
                )
            else:
                problem.add_init(
                    domain.get_predicate("next_unload").inst(
                        PDDLParam(jig.name, jig_t), domain.get_constant("dummy-jig")
                    )
                )

    problem.add_init(PDDLComment("Current Flight: " + current_beluga.name))
    problem.add_init(
            PDDLComment(
                " ".join(
                    [
                        (str(i) + ": " + j.name if 
                        j.name not in state.beluga_contents else 
                        '(' + str(i) + ": " + j.name + ')' )
                        for i, j in enumerate(current_beluga.incoming)
                    ]
                )
            )
            if len(current_beluga.incoming) > 0
            else 
                PDDLComment("No jigs")
            
    )

    remaining_incoming_jigs = [j for j in current_beluga.incoming if j in state.beluga_contents]

    if len(remaining_incoming_jigs) > 0:
        problem.add_init(
            domain.get_predicate("to_unload").inst(
                PDDLParam(remaining_incoming_jigs[0].name, jig_t),
                PDDLParam(current_beluga.name, beluga_t),
            )
        )
    else:
        problem.add_init(
            domain.get_predicate("to_unload").inst(
                domain.get_constant("dummy-jig"), PDDLParam(current_beluga.name, beluga_t)
            )
        )

    for i, jig in enumerate(current_beluga.incoming):

        if jig in remaining_incoming_jigs:
            problem.add_init(
                domain.get_predicate("in").inst(
                    PDDLParam(jig.name, jig_t), PDDLParam(current_beluga.name, beluga_t)
                )
            )

        if i < len(current_beluga.incoming) - 1:
            problem.add_init(
                domain.get_predicate("next_unload").inst(
                    PDDLParam(jig.name, jig_t),
                    PDDLParam(current_beluga.incoming[i + 1], jig_t),
                )
            )
        else:
            problem.add_init(
                domain.get_predicate("next_unload").inst(
                    PDDLParam(jig.name, jig_t), domain.get_constant("dummy-jig")
                )
            )




    problem.add_init(PDDLComment("To Process Flights"))
    for flight in to_process_flights:

        problem.add_init(PDDLComment("Flight: " + flight.name))
        problem.add_init(
            PDDLComment(
                " ".join(
                    [str(i) + ": " + j.name for i, j in enumerate(flight.incoming)]
                )
            )
            if len(flight.incoming) > 0
            else 
                PDDLComment("No jigs")
        )

        if len(flight.incoming) > 0:
            problem.add_init(
                domain.get_predicate("to_unload").inst(
                    PDDLParam(flight.incoming[0], jig_t),
                    PDDLParam(flight.name, beluga_t),
                )
            )
        else:
            problem.add_init(
                domain.get_predicate("to_unload").inst(
                    domain.get_constant("dummy-jig"), PDDLParam(flight.name, beluga_t)
                )
            )

        for i, jig in enumerate(flight.incoming):
            problem.add_init(
                domain.get_predicate("in").inst(
                    PDDLParam(jig.name, jig_t), PDDLParam(flight.name, beluga_t)
                )
            )

            if i < len(flight.incoming) - 1:
                problem.add_init(
                    domain.get_predicate("next_unload").inst(
                        PDDLParam(jig.name, jig_t),
                        PDDLParam(flight.incoming[i + 1], jig_t),
                    )
                )
            else:
                problem.add_init(
                    domain.get_predicate("next_unload").inst(
                        PDDLParam(jig.name, jig_t), domain.get_constant("dummy-jig")
                    )
                )


def init_outgoing(
    variant: Variant,
    beluga_problem: BelugaProblem,
    state : BelugaProblemState,
    problem: PDDLProblem,
    domain: PDDLDomain,
):

    beluga_t = domain.get_type("beluga")
    slot_t = domain.get_type("slot")
    type_t = domain.get_type("type")

    current_beluga = state.current_beluga
    # current_beluga_index = beluga_problem.flights.index(current_beluga)
    beluga_problem_flights = [f.name for f in beluga_problem.flights] # NOTE changed by Michele
    current_beluga_index = beluga_problem_flights.index(current_beluga.name)

    finished_flights: list[Flight] = beluga_problem.flights[0:current_beluga_index]
    to_process_flights: list[Flight] = beluga_problem.flights[current_beluga_index + 1:] \
        if current_beluga_index < len(beluga_problem.flights) - 1 else []

    max_slots = max([len(f.outgoing) for f in beluga_problem.flights])
    problem.add_object(PDDLComment("Slots for outgoing flights:"))
    for i in range(max_slots):
        problem.add_object(PDDLParam("slot" + str(i), slot_t))

    problem.add_init(PDDLComment("Outgoing jigs load order:"))
    problem.add_init(PDDLComment("Finished Flights"))     

    if len(finished_flights) == 0:
        problem.add_init(PDDLComment("No already completely finished Flights"))   

    for flight in finished_flights:
        problem.add_init(
            PDDLComment(
                " ".join(
                    [str(i) + ": " + j.name for i, j in enumerate(flight.outgoing)]
                )
            )
            if len(flight.outgoing) > 0
            else 
                PDDLComment("No jigs")
        )

        problem.add_init(
            domain.get_predicate("to_load").inst(
                domain.get_constant("dummy-type"),
                domain.get_constant("dummy-slot"),
                PDDLParam(flight.name, beluga_t),
            )
        )

        for i, _ in enumerate(flight.outgoing):
            if i < len(flight.outgoing) - 1:
                problem.add_init(
                    domain.get_predicate("next_load").inst(
                        PDDLParam(flight.outgoing[i + 1], type_t),
                        PDDLParam("slot" + str(i), slot_t),
                        PDDLParam("slot" + str(i + 1), slot_t),
                        PDDLParam(flight.name, beluga_t),
                    )
                )
            else:
                problem.add_init(
                    domain.get_predicate("next_load").inst(
                        domain.get_constant("dummy-type"),
                        PDDLParam("slot" + str(i), slot_t),
                        domain.get_constant("dummy-slot"),
                        PDDLParam(flight.name, beluga_t),
                    )
                )


    problem.add_init(PDDLComment("Current Flight: " + current_beluga.name))
    problem.add_init(
        PDDLComment(
            " ".join(
                [
                    (str(i) + ": " + j.name if 
                    j.name in state.beluga_contents else 
                    '(' + str(i) + ": " + j.name + ')' )
                    for i, j in enumerate(current_beluga.outgoing)
                ]
            )
        )
        if len(current_beluga.outgoing) > 0
            else 
                PDDLComment("No jigs")
    )

    remaining_outgoing_jigs = [j for j in current_beluga.outgoing if j not in state.beluga_contents]

    if len(remaining_outgoing_jigs) > 0:
        problem.add_init(
            domain.get_predicate("to_load").inst(
                PDDLParam(remaining_outgoing_jigs[0], type_t),
                PDDLParam("slot0", slot_t),
                PDDLParam(current_beluga.name, beluga_t),
            )
        )
    else:
        problem.add_init(
            domain.get_predicate("to_load").inst(
                domain.get_constant("dummy-type"),
                domain.get_constant("dummy-slot"),
                PDDLParam(current_beluga.name, beluga_t),
            )
        )

    for i, jig in enumerate(current_beluga.outgoing):

        if i < len(current_beluga.outgoing) - 1:
            problem.add_init(
                domain.get_predicate("next_load").inst(
                    # PDDLParam(flight.outgoing[i + 1], type_t), # TODO changed by Michele
                    PDDLParam(current_beluga.outgoing[i + 1], type_t),
                    PDDLParam("slot" + str(i), slot_t),
                    PDDLParam("slot" + str(i + 1), slot_t),
                    PDDLParam(current_beluga.name, beluga_t),
                )
            )
        else:
            problem.add_init(
                domain.get_predicate("next_load").inst(
                    domain.get_constant("dummy-type"),
                    PDDLParam("slot" + str(i), slot_t),
                    domain.get_constant("dummy-slot"),
                    PDDLParam(current_beluga.name, beluga_t),
                )
            )

    problem.add_init(PDDLComment("To Process Flights"))
    for flight in to_process_flights:
        problem.add_init(
            PDDLComment(
                " ".join(
                    [str(i) + ": " + j.name for i, j in enumerate(flight.outgoing)]
                )
            )
            if len(flight.outgoing) > 0
            else 
                PDDLComment("No jigs")
        )

        if len(flight.outgoing) > 0:
            problem.add_init(
                domain.get_predicate("to_load").inst(
                    PDDLParam(flight.outgoing[0], type_t),
                    PDDLParam("slot0", slot_t),
                    PDDLParam(flight.name, beluga_t),
                )
            )
        else:
            problem.add_init(
                domain.get_predicate("to_load").inst(
                    domain.get_constant("dummy-type"),
                    domain.get_constant("dummy-slot"),
                    PDDLParam(flight.name, beluga_t),
                )
            )

        for i, _ in enumerate(flight.outgoing):
            if i < len(flight.outgoing) - 1:
                problem.add_init(
                    domain.get_predicate("next_load").inst(
                        PDDLParam(flight.outgoing[i + 1], type_t),
                        PDDLParam("slot" + str(i), slot_t),
                        PDDLParam("slot" + str(i + 1), slot_t),
                        PDDLParam(flight.name, beluga_t),
                    )
                )
            else:
                problem.add_init(
                    domain.get_predicate("next_load").inst(
                        domain.get_constant("dummy-type"),
                        PDDLParam("slot" + str(i), slot_t),
                        domain.get_constant("dummy-slot"),
                        PDDLParam(flight.name, beluga_t),
                    )
                )


def init_production_schedule(
    beluga_problem: BelugaProblem, 
    state : BelugaProblemState,
    problem: PDDLProblem, 
    domain: PDDLDomain
):

    production_line_t = domain.get_type("production-line")
    jig_t = domain.get_type("jig")

    problem.add_object(PDDLComment("Production lines:"))
    for pl in beluga_problem.production_lines:
        problem.add_object(PDDLParam(pl.name, production_line_t))

    problem.add_init(PDDLComment("Production schedule:"))
    for pl in beluga_problem.production_lines:

        remaining_jigs = [j for j in pl.schedule if j not in state.production_line_deliveries[pl.name]]

        problem.add_init(PDDLComment("Production line: " + pl.name))
        problem.add_init(
            PDDLComment(
                " ".join([
                    str(i) + ": " + j.name 
                    if j in remaining_jigs else  
                    '(' + str(i) + ": " + j.name  + ')'
                    for i, j in enumerate(pl.schedule)
                ])
            )
        )

        if len(remaining_jigs) > 0:
            problem.add_init(
                domain.get_predicate("to_deliver").inst(
                    PDDLParam(remaining_jigs[0].name, jig_t),
                    PDDLParam(pl.name, production_line_t),
                )
            )
        else:
            problem.add_init(
                domain.get_predicate("to_deliver").inst(
                    domain.get_constant("dummy-jig"),
                    PDDLParam(pl.name, production_line_t),
                )
            )

        for i, jig in enumerate(pl.schedule):
            if i < len(pl.schedule) - 1:
                problem.add_init(
                    domain.get_predicate("next_deliver").inst(
                        PDDLParam(jig.name, jig_t),
                        PDDLParam(pl.schedule[i + 1].name, jig_t),
                    )
                )
            else:
                problem.add_init(
                    domain.get_predicate("next_deliver").inst(
                        PDDLParam(jig.name, jig_t), domain.get_constant("dummy-jig")
                    )
                )


def init_flight_history(
    variant: Variant,
    beluga_problem: BelugaProblem,
    problem: PDDLProblem,
    domain: PDDLDomain,
):
    if not variant.probabilistic:
        return
    assert (
        len(beluga_problem.tt_last) > 0
    ), "Requiring transition table to generate probabilistic instances"
    max_hist_len = max((len(h) for h in beluga_problem.tt_last))
    beluga_t = domain.get_type("beluga")
    jig_t = domain.get_type("jig")
    slot_t = domain.get_type("slot")
    type_t = domain.get_type("type")
    # problem.add_object(PDDLComment("Dummy object to represent empty flight history"))
    # problem.add_object(PDDLParam("dummy-beluga", beluga_t))
    problem.add_init(
        domain.get_predicate("flight-history").inst(
            *(PDDLParam(f"dummy-beluga-{i+1}", beluga_t) for i in reversed(range(max_hist_len)))
        )
    )
    problem.add_init(
        domain.get_predicate("processed-flight").inst(
            PDDLParam("dummy-beluga-1", beluga_t)
        )
    )
    problem.add_init(
        domain.get_predicate("to_unload").inst(
            PDDLParam("dummy-jig", jig_t), PDDLParam("dummy-beluga-1", beluga_t)
        )
    )
    problem.add_init(
        domain.get_predicate("to_load").inst(
            PDDLParam("dummy-type", type_t),
            PDDLParam("dummy-slot", slot_t),
            PDDLParam("dummy-beluga-1", beluga_t),
        )
    )


def def_goal(beluga_problem: BelugaProblem, problem: PDDLProblem, domain: PDDLDomain):
    problem.add_goal(
        PDDLComment("All jigs empty (order defined by production schedule)")
    )
    for pl in beluga_problem.production_lines:
        for jig in pl.schedule:
            problem.add_goal(
                domain.get_predicate("empty").inst(
                    PDDLParam(jig, domain.get_type("jig"))
                )
            )

    beluga_t = domain.get_type("beluga")

    problem.add_goal(PDDLComment("all Belugas fully unloaded:"))
    for flight in beluga_problem.flights:
        problem.add_goal(
            domain.get_predicate("to_unload").inst(
                domain.get_constant("dummy-jig"), PDDLParam(flight.name, beluga_t)
            )
        )

    problem.add_goal(PDDLComment("all Belugas fully loaded:"))
    for flight in beluga_problem.flights:
        problem.add_goal(
            domain.get_predicate("to_load").inst(
                domain.get_constant("dummy-type"),
                domain.get_constant("dummy-slot"),
                PDDLParam(flight.name, beluga_t),
            )
        )
