class Genotyp:
    def __init__(self, styrka, uthallighet, intelligens) -> None:
        super().__init__()
        self.styrka = styrka
        self.uthallighet = uthallighet
        self.intelligens = intelligens

    def mutate(self) -> 'Genotyp':
        pass
    
    def __eq__(self, other:'Genotyp') -> bool:
        return (self.styrka == other.styrka and
                self.uthallighet == other.uthallighet and
                self.intelligens == other.intelligens)


class Varelse:
    def __init__(self, genotyp: Genotyp):
        self._genotyp = genotyp
        
    def __eq__(self, other: 'Varelse') -> bool:
        return self._genotyp == other._genotyp
    
    def __hash__(self):
        return 10*self._genotyp.styrka+\
            100*self._genotyp.uthallighet*\
                1000*self._genotyp.intelligens
    

class Population:
    def __init__(self) -> None:
        self._varelser = []
    
    def add_varelse(self, varelse: Varelse):
        """Adds a Varelse at the end of the population, 
        given its genotyp is unique"""
        assert type(varelse) == Varelse
        v:Varelse
        for v in self._varelser:
            if v == varelse:
                return
        self._varelser.append(varelse)

    def get_varelse(self) -> Varelse:
        """Returns the first Varelse in the Population"""
        assert len(self) > 0
        return self._varelser.pop(0)
    
    def __len__(self) -> int:
        """Returns the size of the population"""
        return len(self._varelser)

    def attempt_problem(self, problem):
        pass


if __name__ == '__main__':
    p = Population()
    g1 = Genotyp(10,4,8)
    g2 = Genotyp(10,8,4)
    v1 = Varelse(g1)
    v2 = Varelse(g2)
    p.add_varelse(v1)
    p.add_varelse(v2)
    