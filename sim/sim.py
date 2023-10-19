from collections import deque
from random import randrange, random
from typing import Type
import logging
import math

class Resource:
    def __init__(self):
        """Resource Constructor"""
    
    
class Worker(Resource):
    def __init__(self):
        """Initializes the Worker with _vitality = 100"""
        super().__init__()
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
    
    def add(self, Resource: Resource):
        self._Resources.append(Resource)
    
    def get(self) -> Resource:
        """Returns one Resource, returns None if empty"""
        if len(self._Resources) > 0:
            resource = self._Resources.popleft()
            logging.debug("Place (%s) sends resource (%s)", self, hex(id(resource)))
            return resource

    
    def is_empty(self) -> bool:
        """Returns true if place is empty"""
        return len(self._Resources) == 0

    def __len__(self) -> int:
        return len(self._Resources)


class Barn(Place):
    def __init__(self):
        super().__init__()

    def __str__(self) -> str:
        return f"Barn ({len(self._Resources)})"

        
class Storage(Place):
    def __init__(self):
        super().__init__()

    def get(self) -> Product:
        """Returns a product"""
        if len(self._Resources) > 0:
            logging.debug("Storage %s sends one product", hex(id(self)))
            return self._Resources.pop()

    def __str__(self) -> str:
        return f"storage ({len(self._Resources)})"


class Barrack(Place):
    def __init__(self):
        super().__init__()

    def add(self, worker:Worker):
        """Add a worker to the barrack"""
        if worker.get_vitality() > 0:
            self._Resources.append(worker)
            logging.debug("Barrack %s, worker (%s) returned", hex(id(self)), hex(id(worker)))
        else:
            logging.debug("Barrack %s, worker (%s) dead", hex(id(self)), hex(id(worker)))
    
    def __str__(self) -> str:
        result = f"Barrack ({len(self._Resources)}) ({hex(id(self))})"
        return result


class Transition:
    def __init__(self, barrack_in:Barrack, barrack_out:Barrack):
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

        logging.debug("Field %s requesting 1 worker (barrack %s)", hex(id(self)), hex(id(self._barrack_in)))

        worker = self._barrack_in.get()
        worker_vitality = worker.get_vitality() #for debugging
        if (random() > 0.8):
            worker.change_vitality(-randrange(30,80))

        logging.debug("Field %s, worker (%s) harmed (%s -> %s)", hex(id(self)), hex(id(worker)), worker_vitality, worker.get_vitality())
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
            logging.debug("Dininghall %s: barrack (%s) or barn (%s) empty", hex(id(self)), self._barrack_in.is_empty(), self._barn_in.is_empty())
            return

        logging.debug("Dininghall %s requesting 1 worker (barrack %s) and 1 food (barn %s)",
                      hex(id(self)), hex(id(self._barrack_in)), hex(id(self._barn_in)))

        worker = self._barrack_in.get()
        food = self._barn_in.get()
        worker_vitality = worker.get_vitality() #for debugging

        worker.change_vitality((int)(math.atan(6*food.get_quality()-2)*25))
        logging.debug("Dininghall %s: Food quality (%s), worker (%s), health (%s -> %s)", hex(id(self)), food.get_quality(), hex(id(worker)), worker_vitality, worker.get_vitality())

        self._barrack_out.add(worker)


class Home(Transition):
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, storage_in: Storage):
        super().__init__(barrack_in, barrack_out)
        self._storage_in = storage_in
    
    def act(self):
        """Do resting"""
        if self._storage_in.is_empty():
            logging.debug("Home %s, storage empty", hex(id(self)))
            return

        if len(self._barrack_in) > 1 and randrange(100) < 50:
            logging.debug("Home %s requesting 2 workers (barrack %s) and 1 product (storage %s)",
                          hex(id(self)), hex(id(self._barrack_in)), hex(id(self._storage_in)))

            w1 = self._barrack_in.get()
            w2 = self._barrack_in.get()
            self._storage_in.get()
            w3 = Worker()

            logging.debug("Home %s: new worker created (%s + %s -> %s)", hex(id(self)), hex(id(w1)),hex(id(w2)), hex(id(w3)))
            self._barrack_out.add(w1)
            self._barrack_out.add(w2)
            self._barrack_out.add(w3)

        elif not self._barrack_in.is_empty():
            logging.debug("Home %s requesting one worker (barrack %s) and 1 product (storage %s)",
                          hex(id(self)), hex(id(self._barrack_in)), hex(id(self._storage_in)))

            w1 = self._barrack_in.get()
            w1_vitality = w1.get_vitality() #for debugging

            self._storage_in.get()
            w1.change_vitality(5)

            logging.debug("Home %s: worker resting (%s), %s -> %s", hex(id(self)), hex(id(w1)), w1_vitality, w1.get_vitality())
            self._barrack_out.add(w1)



class Factory(Transition):
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, storage_out: Storage):
        super().__init__(barrack_in,barrack_out)
        self._storage_out = storage_out
        self._harm_level = randrange(0,10)
    
    def act(self):
        """Do work"""
        if self._barrack_in.is_empty():
            logging.debug("Factory %s: barrack empty", hex(id(self)))
            return

        logging.debug("Factory (%s) requesting 1 worker (barrack %s)", hex(id(self)), hex(id(self._barrack_in)))
        worker = self._barrack_in.get()

        worker_vitality = worker.get_vitality() #for debugging
        x = random()
        vitality_chage = (int)(-100*(x**2) - self._harm_level)
        worker.change_vitality(vitality_chage)

        logging.debug("Factory %s: product created, worker (%s), harmed (%s -> %s)", hex(id(self)), hex(id(worker)), worker_vitality, worker.get_vitality())
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
            self._transitions.append(transition_type(b1,b2,out))
            logging.debug("Connecting transition (%s) to barracks (%s)(%s) and place (%s)(%s)",
                    transition_type, hex(id(b1)), hex(id(b2)), out_place, hex(id(out_place)))

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

    w1 = World(1, 1, 1, 1, 1, 1, 2,2)
    w1.Simulate()
    logging.info("Program ended")
