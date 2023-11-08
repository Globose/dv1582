class Genotyp:
    def __init__(self) -> None:
        pass

    def mutate(self) -> 'Genotyp':
        """Returns a mutated copy of the genotype"""
        pass

class GnomeGenotyp(Genotyp):
    def __init__(self, styrka, uthallighet, intelligens) -> None:
        super().__init__()
        self.styrka = styrka
        self.uthallighet = uthallighet
        self.intelligens = intelligens

    def mutate(self) -> 'GnomeGenotyp':
        pass

class ListGenotyp(Genotyp):
    def __init__(self, properties: list[int]) -> None:
        super().__init__()
        self._properties = properties

    def mutate(self) -> 'ListGenotyp':
        pass

if __name__ == '__main__':
    pass

