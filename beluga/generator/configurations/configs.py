from abc import ABC, abstractmethod
from typing import Callable, Tuple

from .random_state import RandomState
from beluga_lib import BelugaProblem, JigType

from enum import Enum


class UnsolvableGenerationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class UnsolvabilityScenario(Enum):

    RACK_SPACE_GENERAL = "RACK_SPACE_GENERAL"
    # incoming flights have the maximal number of jigs fitting into the Beluga and
    # outgoing flights have at most one jig

    OUTGOING_FLIGHT_NOT_SAT = "OUTGOING_FLIGHT_NOT_SAT"
    # outgoing flights schedules more jigs of a type than on site

    SCHEDULE_CLASHES = "SCHEDULE_CLASHES"
    # incoming jig schedule and production schedule are built to maximize potential
    # clashes in racks and therefore increase the number of needed swaps.

    def __str__(self):
        return self.value.lower()

    def __repr__(self):
        return str(self)

    @staticmethod
    def argparse(s):
        try:
            return UnsolvabilityScenario[s.upper()]
        except KeyError:
            return s


class ProblemConfig(ABC):

    def __init__(self) -> None:

        # LOG debug output
        self.log = False

        self.seed: int = 0
        self.random_state = RandomState(self.seed)

        # how much space of the racks is initially occupied
        self.occupancy_rate_racks: float = None
        self.distribution_initial_jig_state = None

        # jig types (the number of jigs is automatically determined)
        self.jig_types: list[JigType] = None
        # if jig types are not defined then they are generated based on:
        self.num_jig_types: int = None
        self.distribution_jig_types: Callable[[], JigType]
        self.distribution_size_loaded_jig: Callable[[], int] = None
        self.distribution_size_empty_jig: Callable[[int], int] = None

        # racks
        self.rack_sizes: list[int] = None
        # if rack size are not defined then they are generated based on:
        self.num_racks: int = None
        self.min_rack_size: int = None
        self.max_rack_size: int = None
        self.distribution_rack_size: Callable[[int, int], int] = None

        # flights
        self.num_flights: int = None
        # how many flights before a part is needed in the factory it is delivered
        self.distribution_delivery_buffer: Callable[[], int] = None
        self.max_delivery_buffer: int = None

        self.beluga_size: int = None

        # trailers
        self.num_beluga_trailers: int = None
        self.num_factory_trailers: int = None

        # hangar
        self.num_craning_hangars: int = None

        # production lines
        self.num_production_lines: int = None
        self.distribution_next_production_line: Callable[[list[int]], int] = None
        # the distribution can depend on the number of jigs that have been
        # delivered to a production line since the last delivery to any
        # production line

        # If an unsolvable reason is defined then the generator tries to make
        # make the instance unsolvable due to this reason.
        # If no reason is specified, then the generator tries to generate a
        # solvable instance.
        # In both cases the unsolvability/solvability is not guarantied.
        self.unsolvable_scenario = []

        # probabilistic window determining next flight probability generation
        self.probabilistic_model: str | None = None
        self.probabilistic_window: int | None = None

    def check_config(self):

        assert self.occupancy_rate_racks is not None
        assert self.occupancy_rate_racks > 0 or (
            self.distribution_initial_jig_state is not None
        )

        assert self.jig_types is not None or (
            self.num_jig_types is not None
            and self.distribution_jig_types is not None
            and self.distribution_size_loaded_jig is not None
            and self.distribution_size_empty_jig is not None
        )

        assert self.rack_sizes is not None or (
            self.num_racks is not None
            and self.min_rack_size is not None
            and self.max_rack_size is not None
            and self.distribution_rack_size is not None
        )

        assert (
            self.max_rack_size is None or self.max_rack_size >= 5
        ), "Racks must have at least size 5."

        assert self.num_flights is not None
        assert self.distribution_delivery_buffer is not None

        assert self.beluga_size is not None

        assert self.num_beluga_trailers is not None
        assert self.num_factory_trailers is not None

        assert self.num_production_lines is not None
        assert self.distribution_next_production_line is not None

        assert self.probabilistic_window is None or self.probabilistic_window <= self.num_flights, "The probabilistic window must be strictly positive and cannot be larger than the number of flights, minus one"

        assert (self.probabilistic_window is None) == (self.probabilistic_model is None), "Incomplete probabilistic problem configuration. Missing probabilistic_window or probabilistic_model parameter."

    def check_problem(self, instance: BelugaProblem) -> bool:
        return True


class ProblemGeneratorConfig(ABC):

    @abstractmethod
    def num_configurations(self) -> int:
        pass

    @abstractmethod
    def valid_configuration(self, ProblemConfig) -> Tuple[bool, str]:
        pass

    @abstractmethod
    def gen_configs(self):
        pass
