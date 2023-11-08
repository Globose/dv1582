from threading import Thread
from random import random
from time import sleep

class Varelse(Thread):
    def __init__(self):
        super().__init__()
        self.styrka = int(random()*10)
        self.result = False

    def equals(self, other: 'Varelse') -> bool:
        return False
    
    def assign_problem(self,problem:'Problem'):
        self._problem = problem

    def run(self):
        """Run"""
        self._result = self._problem.test(self)

class Problem():
    def __init__(self) -> None:
        pass
    
    def test(self, varelse: Varelse)->bool:
        #sleep(1*random())
        return varelse.styrka > 5


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
    

if __name__ == '__main__':
    problem = Problem()

    def run_population():
        p = Population()
        for _ in range(100):
            print("adding")
            p.add_varelse(Varelse())
        change = True
        while change:
            change = False
            p_len = len(p)
            for _ in range(p_len):
                var = p.get_varelse()
                if problem.test(var):
                    p.add_varelse(var)
                    # p.add_varelse(var.clone()
                else:
                    change = True
    
    threads = []
    for _ in range(5):
        threads.append(Thread(target=run_population))
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
