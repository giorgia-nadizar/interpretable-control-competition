class Type:
    def __init__(self, name, base_type = 'object'):
        self.name = name
        self.base_type = base_type

    def get_name(self) -> str:
        return self.name

    def is_subtype(self, t) -> bool:
        return self.name == t.name or (isinstance(self.base_type,Type) and self.base_type.is_subtype(t))

    def to_pddl(self):
        return f"{self.name} - \
        {self.base_type if isinstance(self.base_type, str) else self.base_type.name}"
    
    def __eq__(self, __value: object) -> bool:
        return self.name == __value.name and self.base_type == __value.base_type
    
    def __lt__(self, __value: object) -> bool:
        return self.to_pddl().__lt__(__value.to_pddl())
    
    def __repr__(self) -> str:
        return self.name + "(" + str(self.base_type) + ")"