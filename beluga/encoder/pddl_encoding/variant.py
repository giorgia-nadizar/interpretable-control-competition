class Variant:
    """
    Planning variant, i.e., classic, numeric, or probabilistic, to generate instances for.
    """

    def __init__(self):
        self.classic: bool = True
        self.probabilistic: bool = False
