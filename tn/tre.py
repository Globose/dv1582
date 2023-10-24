class Varelse:
    def __init__(self):
        pass

    def equals(self, other: 'Varelse') -> bool:
        return False

class Population:
    def __init__(self) -> None:
        self._varelser = []
    
    def add_varelse(self, varelse: Varelse):
        """Adds a Varelse at the end of the population, 
        given its genotyp is unique"""
        assert type(varelse) == Varelse
        v:Varelse
        for v in self._varelser:
            if v.equals(varelse):
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
    v1 = Varelse()
    p.add_varelse(v1)
    p.get_varelse()    

