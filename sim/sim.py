from collections import deque
from random import randrange

class Token:
    def __init__(self):
        pass
    
    
class Worker(Token):
    def __init__(self):
        self._vitality = 100
    
    def get_vitality(self) -> int:
        """Returns the worker's vitality"""
        return self._vitality
        
    def change_vitality(self, change: int):
        """Changes vitality by an amount"""
        self._vitality += change

        if self._vitality > 100:
            self._vitality = 100
        elif self._vitality < 0:
            self._vitality = 0


class Food(Token):
    def __init__ (self, quality:float):
        self._quality = quality

    def get_quality(self) -> float:
        """Returns quality of the food"""
        return self._quality


class Product(Token):
    """Product"""


class Place:
    def __init__(self):
        self._tokens = deque()
    
    def add(self, token: Token):
        self._tokens.append(token)
    
    def get(self) -> Token:
        """Returns one token, returns None if empty"""
        if len(self._tokens) > 0:
            return self._tokens.popleft()
    
    def is_empty(self) -> bool:
        """Returns true if place is empty"""
        return len(self._tokens) == 0


class Barn(Place):
    def __init__(self):
        super().__init__()

    def __str__(self) -> str:
        return f"Barn ({len(self._tokens)})"

        
class Storage(Place):
    def __init__(self):
        super().__init__()
    
    def get(self) -> Product:
        """Returns a product"""
        if len(self._tokens) > 0:
            return self._tokens.pop()

    def __str__(self) -> str:
        return f"storage ({len(self._tokens)})"


class Barrack(Place):
    def __init__(self):
        super().__init__()
    
    def add(self, worker:Worker):
        """Add a worker to the barrack"""
        if worker.get_vitality() > 0:
            self._tokens.append(worker)
    
    def __str__(self) -> str:
        result = f"Barrack ({len(self._tokens)})"
        
        w: Worker
        for w in self._tokens:
            result += f"\n Worker: {w.get_vitality()}"
        return result

class Transition:
    def __init__(self, barrack_in, barrack_out):
        self._barrack_in = barrack_in
        self._barrack_out = barrack_out
        
    def act(self):
        pass


class Field(Transition):
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, barn_out: Barn):
        super().__init__(barrack_in, barrack_out)
        self._barn_out = barn_out

    def act(self):
        """Do farming"""
        if self._barrack_in.is_empty():
            return

        worker = self._barrack_in.get()
        worker.change_vitality(-10)
        self._barrack_out.add(worker)
        self._barn_out.add(Food(1))


class DiningHall:
    def __init__(self, barrack_in:Barrack, barrack_out:Barrack, barn_in:Barn):
        self._barrack_in = barrack_in
        self._barrack_out = barrack_out
        self._barn_in = barn_in
        
    def act(self):
        """Do eating"""
        if self._barrack_in.is_empty() or self._barn_in.is_empty():
            return

        worker = self._barrack_in.get()
        food = self._barn_in.get()
        worker.change_vitality(10*food.get_quality())
        self._barrack_out.add(worker)


class Home(Transition):
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, storage_in: Storage):
        super().__init__(barrack_in, barrack_out)
        self._storage_in = storage_in
    
    def act(self):
        """Do resting"""


class Factory(Transition):
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, storage_out: Storage):
        super().__init__(barrack_in,barrack_out)
        self._storage_out = storage_out
    
    def act(self):
        """Do work"""
        if self._barrack_in.is_empty():
            return
        worker = self._barrack_in.get()
        worker.change_vitality(-10)
        self._storage_out.add(Product())
        self._barrack_out.add(worker)


class World:    
    def __init__(self, barrack_size:int, storage_size, barn_size, dining_halls_size, homes_size, fields_size, factories_size, workers_size):
        self._day = 0
        self._barracks = [Barrack() for _ in range(barrack_size)]
        self._storage = [Storage() for _ in range(storage_size)]
        self._barns = [Barn() for _ in range(barn_size)]

        self._dining_halls = [DiningHall(self._barracks[randrange(len(self._barracks))], 
                                         self._barracks[randrange(len(self._barracks))],
                                         self._barns[randrange(len(self._barns))])
                              for _ in range(dining_halls_size)]
        
        self._homes = [Home(self._barracks[randrange(len(self._barracks))], 
                            self._barracks[randrange(len(self._barracks))], 
                            self._storage[randrange(len(self._storage))])
                       for _ in range(homes_size)]
        
        self._fields = [Field(self._barracks[randrange(len(self._barracks))],
                              self._barracks[randrange(len(self._barracks))],
                              self._barns[randrange(len(self._barns))])
                        for _ in range(fields_size)]
        
        self._factories = [Factory(self._barracks[randrange(len(self._barracks))],
                                   self._barracks[randrange(len(self._barracks))],
                                   self._storage[randrange(len(self._storage))])
                           for _ in range(factories_size)]
        
        for _ in range(workers_size):
            self._barracks[randrange(len(self._barracks))].add(Worker())


    def _sim_finished(self):
        b: Barrack
        for b in self._barracks:
            if not b.is_empty():
                return False

        return True

    def Simulate(self):
        while not self._sim_finished():
            self._day += 1
            
            print()
            print("Day", self._day)
            f: Factory
            for f in self._factories:
                f.act()
            
            f:Field
            for f in self._fields:
                f.act()
            
            d:DiningHall
            for d in self._dining_halls:
                d.act()
            
            h:Home
            for h in self._homes:
                h.act()
        
            b:Barrack
            for b in self._barracks:
                print(b)    
    
            break

if __name__=='__main__':
    w1 = World(10, 10, 10, 10, 3, 3, 3,200)
    w1.Simulate()
