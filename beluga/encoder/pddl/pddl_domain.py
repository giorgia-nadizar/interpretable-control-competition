from typing import List

from .pddl_predicate_def import PDDLPredicateDef

from .type import Type
from .pddl_predicate import PDDLPredicate
from .pddl_action import PDDLAction
from .pddl_literal import PDDLLiteral

class PDDLDomain:
    def __init__(self):
        self.requirements: list[str] = [":typing", ":equality", ":action-costs"]
        self.types : dict[str, Type] = {}
        self.constants :  dict[str, PDDLLiteral] = {}
        self.predicates :  dict[str, PDDLPredicateDef] = {}
        self.functions :  dict[str, PDDLPredicateDef] = {}
        self.actions : list[PDDLAction] = []


    def get_type(self, name) -> Type:
        assert name in self.types, "Type " + name + " not defined in domain!"
        return self.types[name]
    
    def get_constant(self, name) -> PDDLLiteral:
        assert name in self.constants, "Constant " + name + " not defined in domain!"
        return self.constants[name]
    
    def get_predicate(self, name) -> PDDLPredicateDef:
        assert name in self.predicates, "Predicate " + name + " not defined in domain!"
        return self.predicates[name]
    
    def get_function(self, name) -> PDDLPredicateDef:
        assert name in self.functions, "Function " + name + " not defined in domain!"
        return self.functions[name]

    def to_pddl(self, name: str) -> str:

        sorted_types = list(self.types.values())
        sorted_types.sort()

        sorted_constants = list(self.constants.values())
        sorted_constants.sort()

        sorted_predicates = list(self.predicates.values())
        sorted_predicates.sort()

        sorted_function = list(self.functions.values())
        sorted_function.sort()

        s = f"(define (domain {name})\n"
        s += f"  (:requirements {' '.join(self.requirements)})\n"
        s += "  (:types\n\t\t" + "\n\t\t".join(t.to_pddl() for t in sorted_types) + "\n)\n"
        s += "  (:constants\n\t\t" + "\n\t\t".join(constant.to_pddl() for constant in sorted_constants) + "\n\t)\n\n\n"
        s += "  (:predicates\n\t\t" + "\n\t\t".join(predicate.to_pddl() for predicate in sorted_predicates) + "\n\t)\n\n\n"
        s += "  (:functions\n\t\t" + "\n\t\t".join(f"{function.to_pddl()}" for function in sorted_function) + "\n\t)\n\n\n"
        s += "\n\n\n".join(action.to_pddl() for action in self.actions)
        s += ")"
        return s