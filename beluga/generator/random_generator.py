from beluga_lib import (
    Jig,
    JigType,
    Rack,
    Trailer,
    Flight,
    ProductionLine,
    BelugaProblem,
)
from .configurations.configs import (
    ProblemConfig,
    UnsolvabilityScenario,
    UnsolvableGenerationError,
)
import generator.utils as utils
import numpy as np


class BelugaRandomGenerator:

    def __init__(self, config: ProblemConfig):
        self.config: ProblemConfig = config

        self.jig_types: list[JigType] = []

        self.rack_sizes = []

        self.jigs_initially_on_racks: list[Jig] = []

        # used to constrain the number of jigs on site
        self.jigs_currently_on_site: list[Jig] = []

        # jigs that can be scheduled in an outgoing flight
        self.can_be_outgoing: dict[str, Jig] = {}
        # jigs that have already been scheduled in an outgoing
        self.have_been_outgoing: set[Jig] = set()

        # index corresponds to number of flights the jigs is waiting in the racks
        self.jig_waiting_for_factory = [
            [] for _ in range(self.config.max_delivery_buffer + 1)
        ]

        self.linear_production_schedule: list[Jig] = []

        # when should the schedule fail
        if (
            UnsolvabilityScenario.OUTGOING_FLIGHT_NOT_SAT
            in self.config.unsolvable_scenario
        ):
            # ONLY FOR UNSOLVABLE
            self.blocking_outgoing_flight = (
                self.config.random_state.get_discrete_truncated_uniform_sample(
                    0, self.config.num_flights - 1
                )
            )
            self.flight_containing_missing_jigs = (
                self.config.random_state.get_discrete_truncated_uniform_sample(
                    self.blocking_outgoing_flight, self.config.num_flights
                )
            )
            self.missing_jigs = None

            if config.log:
                print(
                    "blocking flight (to many jigs): "
                    + str(self.blocking_outgoing_flight)
                )
                print(
                    "flight with missing jigs: "
                    + str(self.flight_containing_missing_jigs)
                )

    def greedy_num_fit_racks(self, instance, jig_type: JigType):

        dummy_racks = [rack.size for rack in instance.racks]

        # fit all on site jigs onto racks
        for j in self.jigs_currently_on_site:
            no_space = True
            for i, r in enumerate(dummy_racks):
                if r >= j.size():
                    dummy_racks[i] -= j.size()
                    no_space = False
                    break
            if no_space:
                return 0

        # check how many jigs of type <jig_type> fit additionally onto racks
        add_jigs = 0
        while True:
            no_space = True
            for i, r in enumerate(dummy_racks):
                if r >= jig_type.size_loaded:
                    dummy_racks[i] -= jig_type.size_loaded
                    no_space = False
                    add_jigs += 1
                    break
            if no_space:
                return add_jigs

    def gen_jig_types(self, instance: BelugaProblem):

        self.jig_types = self.config.jig_types

        if self.config.jig_types is None:
            self.jig_types = []
            for i in range(self.config.num_jig_types):
                loaded_size = self.config.distribution_size_loaded_jig(max([r.size for r in instance.racks]))
                self.jig_types.append(
                    JigType(
                        "type" + str(i),
                        self.config.distribution_size_empty_jig(loaded_size),
                        loaded_size,
                    )
                )

        instance.jig_types = {t.name: t for t in self.jig_types}

        self.can_be_outgoing = {t.name: [] for t in self.jig_types}

    def trailers(self, instance: BelugaProblem):

        for n in range(self.config.num_beluga_trailers):
            instance.trailers_beluga.append(Trailer("beluga_trailer_" + str(n + 1)))

        for n in range(self.config.num_factory_trailers):
            instance.trailers_factory.append(Trailer("factory_trailer_" + str(n + 1)))

    def hangars(self, instance: BelugaProblem):

        for n in range(self.config.num_craning_hangars):
            instance.hangars.append("hangar" + str(n + 1))

    def racks(self, instance: BelugaProblem):

        self.rack_sizes = self.config.rack_sizes

        if self.rack_sizes is None:
            self.rack_sizes = []
            for i in range(self.config.num_racks):
                self.rack_sizes.append(self.config.distribution_rack_size())

        if self.config.log:
            print("Rack sizes:")
            print(self.rack_sizes)

        for i, size in enumerate(self.rack_sizes):
            instance.racks.append(
                Rack(f"rack{utils.format_number(i, self.config.num_racks)}", size, [])
            )

    def jigs_on_racks(self, instance: BelugaProblem):

        while instance.occupancy_rate() < self.config.occupancy_rate_racks:

            max_free_space_on_rack = max([rack.free_space() for rack in instance.racks])
            fitting_jig_types = [
                jt for jt in self.jig_types if jt.size_loaded <= max_free_space_on_rack
            ]

            if len(fitting_jig_types) == 0:
                break

            jig_type = self.config.distribution_jig_types(fitting_jig_types)
            name = f"jig{utils.format_number(len(instance.jigs) + 1, 1000)}"
            jig = Jig(name, jig_type)
            jig.empty = self.config.distribution_initial_jig_state()

            racks_with_sufficient_space = [
                rack for rack in instance.racks if rack.free_space() >= jig.size()
            ]

            rack: Rack = self.config.random_state.get_random_element_uniform(
                racks_with_sufficient_space
            )
            assert rack.fits(jig)

            instance.jigs[jig.name] = jig
            self.jigs_initially_on_racks.append(jig)
            self.jigs_currently_on_site.append(jig)

            if jig.empty:
                # empty jigs can be part of outgoing flights
                self.can_be_outgoing[jig.type.name].append(jig)
            else:
                # loaded jigs can be scheduled for the factory
                self.jig_waiting_for_factory[
                    self.config.distribution_delivery_buffer()
                ].append(jig)

            if (jig.empty):
                rack.add_jig_beluga_side(jig)
            else:
                rack.add_jig_factory_side(jig)


    def gen_next_incoming_jigs(
        self, instance: BelugaProblem, flight_id: int
    ) -> list[Jig]:

        next_incoming_jigs = []

        ### ONLY UNSOLVABLE
        #### schedule additional jigs from failed outgoing flight
        if (
            UnsolvabilityScenario.OUTGOING_FLIGHT_NOT_SAT
            in self.config.unsolvable_scenario
            and self.flight_containing_missing_jigs == flight_id
        ):

            assert (
                self.missing_jigs is not None
            ), "ERROR while trying to make instance unsolvable due to " + str(
                UnsolvabilityScenario.OUTGOING_FLIGHT_NOT_SAT
            )

            if self.config.log:
                print(
                    "UNSOLVABLE: schedule additional jigs from failed outgoing flight"
                )
                print(self.missing_jigs)

            for jig in self.missing_jigs:
                next_incoming_jigs.append(jig)
                self.jigs_currently_on_site.append(jig)

                jig_delivery_buffer = self.config.distribution_delivery_buffer()
                self.jig_waiting_for_factory[jig_delivery_buffer].append(jig)

            return next_incoming_jigs

        ### normal schedule
        jig_type = self.config.distribution_jig_types(self.jig_types)
        num_jigs_fit_beluga = int(self.config.beluga_size / jig_type.size_loaded)
        # approximate how many jigs fit on the racks
        num_jigs_fit_racks = self.greedy_num_fit_racks(instance, jig_type)
        num_jigs_allowed = min(num_jigs_fit_beluga, num_jigs_fit_racks)

        if UnsolvabilityScenario.RACK_SPACE_GENERAL in self.config.unsolvable_scenario:
            # deliver maximal number of jigs fitting into the Beluga independent of space
            if self.config.log:
                print(
                    "UNSOLVABLE: more incoming jigs "
                    + str(num_jigs_allowed)
                    + " --> "
                    + str(num_jigs_fit_beluga)
                )
            num_jigs_allowed = num_jigs_fit_beluga

        if self.config.log:
            print("jig type: " + jig_type.name)
            print("num jigs fit racks: " + str(num_jigs_fit_racks))
            print("num jigs fit Beluga: " + str(num_jigs_fit_beluga))
            print("num jigs allowed: " + str(num_jigs_allowed))

        for _ in range(num_jigs_allowed):

            name = f"jig{utils.format_number(len(instance.jigs) + 1, 1000)}"
            jig = Jig(name, jig_type, False)

            instance.jigs[name] = jig
            next_incoming_jigs.append(jig)
            self.jigs_currently_on_site.append(jig)

            jig_delivery_buffer = self.config.distribution_delivery_buffer()
            self.jig_waiting_for_factory[jig_delivery_buffer].append(jig)

        return next_incoming_jigs

    def update_production_schedule(self) -> list[Jig]:

        if self.config.log:
            print("Jigs waiting for factory: ")
            for d, j in enumerate(self.jig_waiting_for_factory):
                print(str(d) + " flights(s): ")
                print(j)
            print(
                "Number of jigs added to production schedule: "
                + str(len(self.jig_waiting_for_factory[0]))
            )

        can_be_outgoing_jigs_after_next_flight = [
            j
            for j in self.jig_waiting_for_factory[0]
            if j.name not in self.have_been_outgoing
        ]

        self.linear_production_schedule += self.jig_waiting_for_factory[0]
        # shift waiting jigs by one flight
        self.jig_waiting_for_factory = self.jig_waiting_for_factory[1:] + [[]]

        if self.config.log:
            print(
                "production Schedule ("
                + str(len(self.linear_production_schedule))
                + ")"
            )
            print(self.linear_production_schedule)
            print("Can be outgoing after next flight:")
            print(can_be_outgoing_jigs_after_next_flight)

        return can_be_outgoing_jigs_after_next_flight

    def schedule_next_outgoing_jigs(
        self, instance: BelugaProblem, flight_id: int
    ) -> list[Jig]:

        next_outgoing = []

        #### ONLY UNSOLVABLE: failed outgoing flight
        if (
            UnsolvabilityScenario.OUTGOING_FLIGHT_NOT_SAT
            in self.config.unsolvable_scenario
            and self.blocking_outgoing_flight == flight_id
        ):

            if self.config.log:
                print("UNSOLVABLE: schedule to many outgoing jigs of one type")

            # how many jigs are on site of each type
            jig_types_on_site = {t: 0 for t in self.jig_types}
            for jig in self.jigs_currently_on_site:
                jig_types_on_site[jig.type] += 1

            if self.config.log:
                print("Jig types on site:")
                print(jig_types_on_site)

            # is there a type where more jigs fit into the Beluga than are on site
            possible_unsat_jig_types = []
            for t in self.jig_types:
                if int(self.config.beluga_size / t.size_empty) > jig_types_on_site[t]:
                    possible_unsat_jig_types.append(t)

            if self.config.log:
                print("Jig types with less jigs on site than fit into the Beluga:")
                print(possible_unsat_jig_types)

            if len(possible_unsat_jig_types) == 0:
                raise UnsolvableGenerationError(
                    str(UnsolvabilityScenario.OUTGOING_FLIGHT_NOT_SAT.value)
                    + ": In the randomly chosen flight there is no jig type with less jigs on site than fit into the Beluga!"
                )

            random_jig_type = self.config.random_state.get_random_element_uniform(
                possible_unsat_jig_types
            )
            num_jigs_on_site = jig_types_on_site[random_jig_type]
            num_jigs_fit_beluga = int(
                self.config.beluga_size / random_jig_type.size_empty
            )

            num_missing_jigs = (
                self.config.random_state.get_discrete_truncated_uniform_sample(
                    num_jigs_on_site + 1, num_jigs_fit_beluga
                )
                - num_jigs_on_site
            )

            if self.config.log:
                print("selected type: " + str(random_jig_type))
                print("Number of jigs on sight: " + str(num_jigs_on_site))
                print("Number of jigs fitting Beluga: " + str(num_jigs_fit_beluga))
                print("Number of missing jigs: " + str(num_missing_jigs))

            # create missing jigs
            self.missing_jigs = []
            for _ in range(num_missing_jigs):

                name = f"jig{utils.format_number(len(instance.jigs) + 1, 1000)}"
                jig = Jig(name, random_jig_type, True)

                instance.jigs[name] = jig
                self.missing_jigs.append(jig)

            # treat the actually existing jigs
            self.can_be_outgoing[random_jig_type.name] = (
                []
            )  # all jigs that could actually be schedules are scheduled
            next_outgoing = [
                j for j in self.jigs_currently_on_site if j.type == random_jig_type
            ]

            if self.config.log:
                print("Outgoing and on site: ")
                print(next_outgoing)

            for jig in next_outgoing:
                assert jig in self.jigs_currently_on_site, (
                    str(jig) + " not in " + str(self.jigs_currently_on_site)
                )
                self.jigs_currently_on_site.remove(jig)

            next_outgoing += self.missing_jigs

            self.have_been_outgoing.update(next_outgoing)

            if self.config.log:
                print("Missing jigs: ")
                print(self.missing_jigs)
                print("have been outgoing: ")
                print(self.have_been_outgoing)

            return next_outgoing

        #### normal outgoing flight
        if sum([len(jigs) for jigs in self.can_be_outgoing.values()]) > 0:

            # check which type has enough jigs to fill the beluga with the maximal number
            enough_jigs = []
            for t_name, jigs in self.can_be_outgoing.items():

                if len(jigs) > 0 and int(
                    self.config.beluga_size / jigs[0].type.size_empty
                ) >= len(jigs):
                    enough_jigs.append(t_name)

            # if there is no full flight, then choose the jig type that leaves the least amount of free space in the Beluga
            if len(enough_jigs) == 0:
                if self.config.log:
                    print(
                        "not enough empty jigs, use type with least free space in Beluga"
                    )
                min_free_space = self.config.beluga_size
                best_type = None
                for t_name, jigs in self.can_be_outgoing.items():
                    free_space = self.config.beluga_size - sum(
                        [j.type.size_empty for j in jigs]
                    )
                    if len(jigs) > 0 and free_space < min_free_space:
                        min_free_space = free_space
                        best_type = jigs[0].type.name
                enough_jigs.append(best_type)

            if self.config.log:
                print("can be empty and thus scheduled:")
                print(self.can_be_outgoing)
                print("enough jigs to fill Beluga completely:")
                print(enough_jigs)

            name_next_type_out = self.config.random_state.get_random_element_uniform(
                enough_jigs
            )
            num_jigs_fit_beluga = int(
                self.config.beluga_size
                / self.can_be_outgoing[name_next_type_out][0].type.size_empty
            )

            if self.config.log:
                print("Next outgoing type: " + str(name_next_type_out))
                print("Jigs fit Beluga: " + str(num_jigs_fit_beluga))

            # ONLY UNSOLVABLE:
            # only one outgoing jig independent on how many fit into the Beluga or
            # are available
            if (
                UnsolvabilityScenario.RACK_SPACE_GENERAL
                in self.config.unsolvable_scenario
            ):
                if self.config.log:
                    print(
                        "UNSOLVABLE: less outgoing jigs "
                        + str(num_jigs_fit_beluga)
                        + " --> "
                        + str(1)
                    )
                num_jigs_fit_beluga = 1

            next_outgoing = self.can_be_outgoing[name_next_type_out][
                :num_jigs_fit_beluga
            ]
            self.can_be_outgoing[name_next_type_out] = self.can_be_outgoing[
                name_next_type_out
            ][num_jigs_fit_beluga:]

            for jig in next_outgoing:
                assert jig in self.jigs_currently_on_site, (
                    str(jig) + " not in " + str(self.jigs_currently_on_site)
                )
                self.jigs_currently_on_site.remove(jig)

        else:
            if self.config.log:
                print("No jigs ready to be scheduled for outgoing flight")

        self.have_been_outgoing.update([j.name for j in next_outgoing])

        return next_outgoing

    def schedule_individual_production_lines(self, instance: BelugaProblem) -> None:
        if UnsolvabilityScenario.SCHEDULE_CLASHES in self.config.unsolvable_scenario:
            self.schedule_individual_production_lines_clashes(instance)
            return

        for i in range(self.config.num_production_lines):
            instance.production_lines.append(ProductionLine("pl" + str(i), []))

        if self.config.log:
            print("final production schedule:")
            print("linear schedule: ")
            print(self.linear_production_schedule)

        # effects the probability of a production line been chosen
        advantage = [0 for _ in range(self.config.num_production_lines)]

        for jig in self.linear_production_schedule:
            index = self.config.distribution_next_production_line(advantage)

            for i in range(self.config.num_production_lines):
                if i == index:
                    advantage[i] = 0
                else:
                    advantage[i] += 1
            # instance.production_lines[index].schedule.append(jig.name)
            instance.production_lines[index].schedule.append(jig)

        if self.config.log:
            for pl in instance.production_lines:
                print(pl.name)
                print(pl.schedule)

    def schedule_individual_production_lines_clashes(
        self, instance: BelugaProblem
    ) -> None:
        for i in range(self.config.num_production_lines):
            instance.production_lines.append(ProductionLine("pl" + str(i), []))
        jigs_arriving = [f.incoming for f in instance.flights if len(f.incoming) > 0]
        jigs_arriving_with_index = [
            [(jig, i) for jig in instance.flights[i].incoming]
            for i in range(len(instance.flights))
            if len(instance.flights[i].incoming) > 0
        ]
        all_jigs = set()
        all_jigs_index = set()
        all_jigs_queue = []
        for x, x_index in zip(jigs_arriving, jigs_arriving_with_index):
            for j in x:
                all_jigs.add(j)
            for j in x_index:
                all_jigs_index.add(j)
            all_jigs_queue += x
        put_in_factories = set()
        while len(put_in_factories) < len(all_jigs):
            max_ = max(all_jigs_index, key=lambda x: x[1])
            all_jigs_index.remove(max_)
            r_factory: ProductionLine = self.config.random_state.get_random_element_uniform(
                instance.production_lines
            )
            cur_index = max_[1]
            cur_jig = max_[0]
            while cur_index >= 0:
                r_factory.schedule.append(cur_jig)
                put_in_factories.add(cur_jig)
                next_candidates = [x for x in all_jigs_index if x[1] < cur_index]
                if len(next_candidates) > 0:
                    max_ = max(next_candidates, key=lambda x: x[1])
                    cur_index = max_[1]
                    cur_jig = max_[0]
                    all_jigs_index.remove(max_)
                else:
                    break

    def schedules(self, instance: BelugaProblem):

        flight_id = 1
        tries = 200
        while flight_id <= self.config.num_flights:
            tries -= 1
            assert tries > 0, "Error: Generating valid schedule."

            if self.config.log:
                print("++++++++++++ Flight " + str(flight_id) + " ++++++++++++++++")
                print("---------> INCOMING")

            next_incoming_jigs = self.gen_next_incoming_jigs(instance, flight_id)

            if self.config.log:
                print("---------> PRODUCTION SCHEDULE")

            can_be_outgoing_jigs_after_next_flight = self.update_production_schedule()

            if self.config.log:
                print("---------> OUTGOING")

            next_outgoing = self.schedule_next_outgoing_jigs(instance, flight_id)

            for jig in can_be_outgoing_jigs_after_next_flight:
                if jig.name not in self.have_been_outgoing:
                    self.can_be_outgoing[jig.type.name].append(jig)

            # if there are not incoming jigs (not enough space) and no outgoing
            # jigs (no jig ready according to delay buffer) then no flight
            # is scheduled, but the delay buffer is still push forward by one flight
            if len(next_incoming_jigs) == 0 and len(next_outgoing) == 0:
                if self.config.log:
                    print("flight canceled, no incoming and outgoing jigs")
                continue

            # flight = Flight(
            #     "beluga" + str(flight_id),
            #     [j.name for j in next_incoming_jigs],
            #     [j.type for j in next_outgoing],
            # )

            flight = Flight(
                "beluga" + str(flight_id),
                [j for j in next_incoming_jigs],
                [j.type for j in next_outgoing],
            )

            if self.config.log:
                print("next flight: ")
                print("incoming: ")
                print(flight.incoming)
                print("outgoing: ")
                print(flight.outgoing)
                print("currently on side: ")
                print(self.jigs_currently_on_site)
                print("++++++++++++ Flight " + str(flight_id) + " ++++++++++++++++")

            instance.flights.append(flight)
            flight_id += 1

        self.schedule_individual_production_lines(instance)

    def generate(self) -> BelugaProblem:

        instance = BelugaProblem()

        self.racks(instance)

        self.gen_jig_types(instance)

        self.trailers(instance)

        self.hangars(instance)

        self.jigs_on_racks(instance)

        self.schedules(instance)

        return instance


# ==============================================================================
# Code for generating a probabilistic model
# ==============================================================================


class ProbabilisticModelGenerator:

    def _single_transition(seq, pos, win, num, res, verbose=0):
        assert len(seq) == win + 1
        # Determine whether there's a mandatory next node
        mandatory = pos - win
        if mandatory >= 0 and mandatory not in seq:
            choices = [mandatory]
        else:
            choices = range(max(0, pos - win), min(num, pos + win + 1))
        if verbose > 0:
            print(f"seq={seq}, pos={pos}, win={win}, num={num}, choices={choices}")
        # Consider all possible next nodes
        visited = set(seq)
        for k in choices:
            if k in visited:
                continue
            nxt = seq + [k]
            res.append(tuple(nxt))

    def _assign_probabilities(tbl, pos, potential, prec=5):
        # Assign a potential to the transitions
        pvals = []
        zvals = {}
        last_of_group = []
        prev_last = None
        for lst, nxt in zip(tbl["last"], tbl["next"]):
            # Obtain the potential
            pval = potential(pos, lst, nxt)
            pvals.append(pval)
            # Update the normalization factor
            if lst not in zvals:
                zvals[lst] = pval
            else:
                zvals[lst] += pval
            # Flag the previous transition if it was the last in a group
            last_of_group.append(prev_last is not None and lst != prev_last)
        # The last transition always closes a group
        last_of_group.append(True)
        # Normalize the potentials to obtain probabilities
        tbl["prob"] = []
        current_group_prob = 0
        for lst, nxt, pval, log in zip(tbl["last"], tbl["next"], pvals, last_of_group):
            # Determine the probability and update the current group prob.
            if not log:
                prob = np.round(pval / zvals[lst], decimals=prec)
                current_group_prob += prob
            else:
                prob = 1 - current_group_prob
                current_group_prob = 0
            tbl["prob"].append(prob)

    def build_transition_table(num, win, potential, verbose=0):
        ptbl = [[-1] * (win + 1)]
        itbl = []
        res = {}
        for pos in range(0, num):
            if verbose > 0:
                print(f"=== POS {pos}")
            # Build multiple possible extensions
            tbl = []
            for seq in ptbl:
                ProbabilisticModelGenerator._single_transition(
                    seq=seq, pos=pos, win=win, num=num, res=tbl, verbose=verbose - 2
                )
            # Display the local transition table
            if verbose > 1:
                print(f"--- internal table")
                for row in tbl:
                    print(row)
            # Store local transition table
            tbl = sorted(tbl)
            itbl.append(tbl)
            # Build the predecessor table for the next iteration
            ptbl = set(t[1:] for t in tbl)
            ptbl = [list(t) for t in ptbl]
            if verbose > 1:
                print(f"--- next predecessor table")
                for row in ptbl:
                    print(row)
            # Build the transition table
            res[pos] = {"last": [t[:-1] for t in tbl], "next": [t[-1] for t in tbl]}
            # Assign a probability value to the transitions
            ProbabilisticModelGenerator._assign_probabilities(res[pos], pos, potential)
            # Print the transition table
            if verbose > 0:
                print(f"--- transition table")
                print(f"last, next, prob")
                for lst, nxt, prob in zip(
                    res[pos]["last"], res[pos]["next"], res[pos]["prob"]
                ):
                    print(f"{lst}, {nxt}, {prob}")
        return res

    def _read_potential(json_dict):
        if "type" not in json_dict:
            raise ValueError(
                'A Potential configuration file should have a "type" field'
            )
        ptype = json_dict["type"]
        for pclass in potentials.pclasses:
            if ptype == pclass.ptype:
                return pclass.from_json(json_dict)
        raise ValueError(f'Unsupporteed type of Potential "{ptype}"')

    def _augment_instance(prob, potential, win, use_flight_ids=False):
        # Obtain the flight names
        fl_names = {p: f["name"] for p, f in enumerate(prob["flights"])}
        fl_names[-1] = None
        # Prepare a data structure for the information to be added
        res = []
        # Build all the transition tables
        tables = ProbabilisticModelGenerator.build_transition_table(
            num=len(fl_names) - 1, win=win, potential=potential
        )
        for pos in sorted(tables.keys()):
            # Obtain the table for the current position
            tbl = tables[pos]
            to_add = {"last": None, "next": None, "prob": None}
            if use_flight_ids:
                to_add["last"] = tbl["last"]
                to_add["next"] = tbl["next"]
                to_add["prob"] = tbl["prob"]
            else:
                to_add["last"] = [tuple(fl_names[p] for p in t) for t in tbl["last"]]
                to_add["next"] = [fl_names[p] for p in tbl["next"]]
                to_add["prob"] = tbl["prob"]
            # Store the table
            res.append(to_add)
        # Add the new information
        prob["transition_tables"] = res
