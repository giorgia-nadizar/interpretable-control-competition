from typing import Callable, List
from enum import Enum

from beluga_lib.jigs import JigType
from beluga_lib.beluga_problem import BelugaProblem
from .configs import ProblemConfig, UnsolvabilityScenario
from .random_state import RandomState

class JigTypeDistributionType:
    UNIFORM = 0
    SMALL_PREF = 1
    LARGE_PREF = 2


jig_types = [
    JigType("typeA", 4, 4),
    JigType("typeB", 8, 11),
    JigType("typeC", 9, 18),
    JigType("typeD", 18, 25),
    JigType("typeE", 32, 32),
] 


def get_jig_type_distribution(dist, random_state: RandomState):

    if dist == JigTypeDistributionType.UNIFORM:
        return lambda types: random_state.get_random_element_uniform(types)
    
    top = 0.35
    bottom = 0.05
    
    if dist == JigTypeDistributionType.SMALL_PREF:
        def dist(types): 
            if len(types) == 1:
                return types[0]
            types.sort(key = lambda jt: jt.size_loaded)
            props = [top - i * ((top - bottom) / (len(types) - 1)) for i in range(len(types))]
            s = sum(props)
            props = [v * (1 / s) for v in props]
            return random_state.get_random_element_prop(
                types, 
                props
        )
        return dist    
    
    if dist == JigTypeDistributionType.LARGE_PREF:
        def dist(types): 
            if len(types) == 1:
                return types[0]
            types.sort(key = lambda jt: jt.size_loaded, reverse=True)
            props = [top - i * ((top - bottom) / (len(types) - 1)) for i in range(len(types))]
            s = sum(props)
            props = [v * (1 / s) for v in props]
            return random_state.get_random_element_prop(
                types, 
                props
        )
        return dist    


class DefaultProblemConfig(ProblemConfig):

    def __init__(
        self,
        verbose: bool,
        seed: int,
        occ_rate: float,
        jig_t_dist: int,
        num_flights: int,
        unsolvable_scenarios: List[UnsolvabilityScenario] = [],
        probabilistic_model: str | None = None,
        probabilistic_window: int | None = None,
    ) -> None:
        super().__init__()

        self.verbose = verbose

        self.seed = seed

        self.random_state = RandomState(self.seed)

        self.occupancy_rate_racks = occ_rate
        self.num_flights = num_flights

        # jigs
        self.jig_types = jig_types

        # racks
        self.num_racks = int(min(20, 2 * max(1, 0.1 * num_flights)))
        self.min_rack_size = 20
        self.max_rack_size = 40

        self.beluga_size = 40

        self.num_beluga_trailers = self.random_state.get_discrete_truncated_uniform_sample(1,3)
        self.num_factory_trailers = self.random_state.get_discrete_truncated_uniform_sample(1,3)
        self.num_craning_hangars = self.random_state.get_discrete_truncated_uniform_sample(1,3)
        self.num_production_lines = self.random_state.get_discrete_truncated_uniform_sample(1,3)

        self.probabilistic_model = probabilistic_model
        self.probabilistic_window = probabilistic_window

        # racks
        self.distribution_rack_size = (
            lambda: self.random_state.get_discrete_truncated_uniform_sample(
                20,
                40
            )
        )

        # jigs
        self.distribution_initial_jig_state = (
            lambda: self.random_state.get_random_element_uniform([True, False])
        )

        self.distribution_jig_types = get_jig_type_distribution(
            jig_t_dist,
            self.random_state
        )

        # flights
        self.max_delivery_buffer = min(int(0.5 * self.num_flights), 25)
        self.distribution_delivery_buffer: Callable[[], int] = (
            lambda: self.random_state.get_discrete_truncated_normal_sample(
                0.25 * self.max_delivery_buffer,
                0.5 * self.max_delivery_buffer,
                1,
                self.max_delivery_buffer,
            )
        )

        # production line
        self.distribution_next_production_line: Callable[[list[int]], int] = (
            lambda del_since: self.random_state.get_uniform_advantage_sample(del_since)
        )

        self.unsolvable_scenario = unsolvable_scenarios

        self.check_config()


    def check_problem(self, instance: BelugaProblem) -> bool:

        # is at least one jig scheduled for production
        if sum([len(pl.schedule) for pl in instance.production_lines]) == 0:
            print("ERROR empty production lines")
            return False

        # is at least one jig incoming and outgoing
        num_in = sum([len(f.incoming) for f in instance.flights])
        num_out = sum([len(f.outgoing) for f in instance.flights])

        if num_in == 0 or num_out == 0:
            print("ERROR all incoming or outgoing flights empty")
            return False

        return True
