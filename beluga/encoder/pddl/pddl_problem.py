import re

from .pddl_param import PDDLParam
from .pddl_predicate import PDDLPredicate
from .pddl_numeric_fluent import PDDLNumericFluent
from .pddl_literal import PDDLLiteral

class PDDLProblem:
    def __init__(self, name: str, domain_name: str):
        self.name = name
        self.domain_name = domain_name
        self.objects: list[PDDLParam] = []
        self.init: list[PDDLLiteral] = []
        self.goal: list[PDDLLiteral] = []

    def add_object(self, o : PDDLParam) -> None:
        self.objects.append(o)

    def add_init(self, l : PDDLLiteral) -> None:
        self.init.append(l)

    def add_goal(self, l : PDDLLiteral) -> None:
        self.goal.append(l)


    def to_pddl(self, name: str) -> str:
        sanitized_name = re.sub(r"\s+", '_', name)
        sanitized_domain_name = re.sub(r"\s+", '_', self.domain_name)

        s = f"(define\n\t(problem {sanitized_name})\n\t(:domain " + sanitized_domain_name + ")\n"
        s += "  (:objects\n\t\t" + "\n\t\t".join(obj.to_pddl() for obj in self.objects) + "\n\t)\n"
        s += "  (:init\n\t\t" + "\n\t\t".join(init.to_pddl() for init in self.init) + "\n\t)\n"
        s += "  (:goal (and\n\t\t" + "\n\t\t".join(goal.to_pddl() for goal in self.goal) + "\n\t))\n"
        s += "  (:metric minimize (total-cost))\n"
        s += ")"
        return s
    


