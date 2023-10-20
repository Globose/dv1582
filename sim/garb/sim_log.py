from collections import deque
from random import randrange, random
from typing import Type
import logging
import math

class Resource:
    def __init__(self):
        """Resource Constructor"""
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__} [{hex(id(self))}]"


class Worker(Resource):
    def __init__(self):
        """Initializes the Worker with _vitality = 100"""
        super().__init__()
        self._vitality = 100
    
    @property
    def vitality(self) -> int:
        """Returns the worker's vitality"""
        return self._vitality
        
    def change_vitality(self, change: int):
        """Changes vitality by an amount"""
        self._vitality += change

        if self._vitality > 100:
            self._vitality = 100
        elif self._vitality < 0:
            self._vitality = 0

    def __str__(self) -> str:
        return f"{self.__class__.__name__} [{hex(id(self))}, {self._vitality}]"


class Food(Resource):
    def __init__ (self, quality:float):
        super().__init__()
        self._quality = quality

    def get_quality(self) -> float:
        """Returns quality of the food"""
        return self._quality


class Product(Resource):
    """Product"""
    def __init__(self):
        super().__init__()


class Place:
    def __init__(self):
        self._Resources = deque()
    
    def add(self, resource: Resource):
        self._Resources.append(resource)
        logging.debug("%s, one %s added", self, resource)
    
    def get(self) -> Resource:
        """Returns one Resource, returns None if empty"""
        if len(self._Resources) > 0:
            resource = self._Resources.popleft()
            logging.debug("%s sends one %s", self, resource)
            return resource

    def is_empty(self) -> bool:
        """Returns true if place is empty"""
        return len(self._Resources) == 0

    def __len__(self) -> int:
        return len(self._Resources)

    def __str__(self) -> str:
        result = f"{self.__class__.__name__}[{len(self._Resources)}, {hex(id(self))}]"
        return result


class Barn(Place):
    def __init__(self):
        super().__init__()

        
class Storage(Place):
    def __init__(self):
        super().__init__()

    def get(self) -> Product:
        """Returns a product"""
        if len(self._Resources) > 0:
            logging.debug("%s sends one product", self)
            return self._Resources.pop()


class Barrack(Place):
    def __init__(self):
        super().__init__()

    def add(self, worker:Worker):
        """Add a worker to the barrack"""
        if worker.vitality > 0:
            self._Resources.append(worker)
            logging.debug("%s, %s returned", self, worker)
        else:
            logging.debug("%s, %s dead", self, worker)


class Transition:
    def __init__(self, barrack_in:Barrack, barrack_out:Barrack):
        self._barrack_in = barrack_in
        self._barrack_out = barrack_out
        
    def act(self):
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{hex(id(self))}]"


class Field(Transition):
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, barn_out: Barn):
        super().__init__(barrack_in, barrack_out)
        self._barn_out = barn_out

    def act(self):
        """Do farming"""
        if self._barrack_in.is_empty():
            return

        logging.debug("%s requesting 1 from %s", self, self._barrack_in)

        worker = self._barrack_in.get()
        vitality_change = 0
        if (random() > 0.8):
            vitality_change = -randrange(30,80)
        worker.change_vitality(vitality_change)

        logging.debug("%s sent food to %s, %s harmed %s", self, self._barn_out , worker, vitality_change)
        self._barrack_out.add(worker)
        self._barn_out.add(Food(1))


class DiningHall(Transition):
    def __init__(self, barrack_in:Barrack, barrack_out:Barrack, barn_in:Barn):
        super().__init__(barrack_in, barrack_out)
        self._barn_in = barn_in

    def act(self):
        """Do eating"""
        if self._barrack_in.is_empty() or self._barn_in.is_empty():
            logging.debug("%s: %s or %s is empty", self, self._barrack_in, self._barn_in)
            return

        logging.debug("%s requesting 1 from %s, 1 from %s",
                      self, self._barrack_in, self._barn_in)

        worker = self._barrack_in.get()
        food = self._barn_in.get()
        vitality_change = (int)(math.atan(6*food.get_quality()-2)*25)

        worker.change_vitality(vitality_change)
        logging.debug("%s: %s, %s, plus %s", self, food, worker, vitality_change)

        self._barrack_out.add(worker)


class Home(Transition):
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, storage_in: Storage):
        super().__init__(barrack_in, barrack_out)
        self._storage_in = storage_in
    
    def act(self):
        """Do resting"""
        if self._storage_in.is_empty():
            logging.debug("%s, empty %s", self, self._storage_in)
            return

        if len(self._barrack_in) > 1 and randrange(100) < 50:
            logging.debug("%s requesting 2 from %s and 1 from %s",
                          self, self._barrack_in, self._storage_in)

            w1 = self._barrack_in.get()
            w2 = self._barrack_in.get()
            self._storage_in.get()
            w3 = Worker()

            logging.debug("%s: new %s + %s -> %s", self, w1, w2, w3)
            self._barrack_out.add(w1)
            self._barrack_out.add(w2)
            self._barrack_out.add(w3)

        elif not self._barrack_in.is_empty():
            logging.debug("%s requesting 1 from %s, 1 from %s",
                          self, self._barrack_in, self._storage_in)

            w1 = self._barrack_in.get()
            self._storage_in.get()
            vitality_change = randrange(20)
            w1.change_vitality(vitality_change)

            logging.debug("%s: Resting %s, plus %s", self, w1, vitality_change)
            self._barrack_out.add(w1)
        else:
            logging.debug("Home %s, barrack (%s) empty", self, self._barrack_in)


class Factory(Transition):
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, storage_out: Storage):
        super().__init__(barrack_in,barrack_out)
        self._storage_out = storage_out
        self._harm_level = randrange(0,10)
    
    def act(self):
        """Do work"""
        if self._barrack_in.is_empty():
            logging.debug("Factory %s: barrack empty", self)
            return

        logging.debug("Factory (%s) requesting 1 worker (barrack %s)", self, self._barrack_in)
        worker = self._barrack_in.get()

        x = random()
        vitality_change = (int)(-100*(x**2) - self._harm_level)
        worker.change_vitality(vitality_change)

        logging.debug("%s: product created (sent to: %s), %s harmed %s", self, self._storage_out, worker, vitality_change)
        self._storage_out.add(Product())
        self._barrack_out.add(worker)


class World:    
    def __init__(self, barrack_size:int, storage_size:int, barn_size:int, dining_halls_size:int, homes_size:int, fields_size:int, factories_size:int, workers_size:int):
        self._day = 0
        self._barracks = [Barrack() for _ in range(barrack_size)]
        self._storage = [Storage() for _ in range(storage_size)]
        self._barns = [Barn() for _ in range(barn_size)]
        logging.info("Added barracks (%s), storages (%s), barns (%s)", barrack_size, storage_size, barn_size)

        self._transitions = []
        self._connect_transition(DiningHall, self._barns, dining_halls_size)
        self._connect_transition(Home, self._storage, homes_size)
        self._connect_transition(Field, self._barns, fields_size)
        self._connect_transition(Factory, self._storage, factories_size)

        for _ in range(workers_size):
            self._barracks[randrange(len(self._barracks))].add(Worker())

        logging.info("Added dining halls (%s), homes (%s), fields (%s), factories (%s), workers (%s)"
                     , dining_halls_size, homes_size, fields_size, factories_size, workers_size)

    def _connect_transition(self, transition_type:Type[Transition], out_place:Transition, size:int):
        for _ in range(size):
            b1 = self._barracks[randrange(len(self._barracks))]
            b2 = self._barracks[randrange(len(self._barracks))]
            out = out_place[randrange(len(out_place))]
            transit = transition_type(b1,b2,out)
            self._transitions.append(transit)
            logging.debug("Connecting %s to %s, %s, %s",
                    transit, b1, b2, out)

    def _sim_finished(self):
        b: Barrack
        for b in self._barracks:
            if not b.is_empty():
                return False

        return True

    def Simulate(self):
        while not self._sim_finished() and self._day < 200:
            self._day += 1
            
            logging.info("New day (%s)", self._day)

            print()
            print("Day", self._day)

            t:Transition
            for t in self._transitions:
                t.act()

            b:Barrack
            for b in self._barracks:
                print(b)
    

if __name__=='__main__':
    logging.basicConfig(filename='sim.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
    logging.info("Program started")

    w1 = World(1, 1, 1, 1, 1, 4, 5,20)
    w1.Simulate()
    logging.info("Program ended")
