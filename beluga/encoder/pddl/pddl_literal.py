from abc import ABC, abstractmethod

class PDDLLiteral(ABC):
    @abstractmethod
    def to_pddl(self) -> str:
        pass

    def __repr__(self) -> str:
        pass



class PDDLComment(PDDLLiteral):

    def __init__(self, text) -> None:
        self.text = text
    
    def to_pddl(self) -> str:
        return "; " + self.text

    def __repr__(self) -> str:
        return self.text