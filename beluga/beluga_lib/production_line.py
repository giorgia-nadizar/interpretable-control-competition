from .jigs import Jig
from typing import List

class ProductionLine:

    def __init__(self, name: str, schedule: list[Jig] = []) -> None:
        self.name = name
        self.schedule : list[Jig] = schedule

    def add_jig_to_schedule(self, jig: Jig):
        self.schedule.append(jig)

    def add_jigs_to_schedule(self, jigs: list[Jig]):
        self.schedule += jigs