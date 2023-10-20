from collections import deque
from random import randrange, random
from typing import Type
import logging
import math
from threading import Thread, Event, Lock
import time


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
        return f"{self.__class__.__name__}[{hex(id(self))}, {self._vitality}]"


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
        self._resources = deque()
        self._reserved = 0
        self._lock = Lock()

    def reserve(self) -> bool:
        """Returns False if empty, otherwise returns True and saves a resource to retrieve later"""
        reservation_success = False
        self._lock.acquire()
        logging.debug("%s Locked", self)
        try:
            if len(self._resources) - self._reserved > 0:
                self._reserved += 1
                reservation_success = True
                logging.debug("%s, Reservation succesful", self)
            else:
                logging.debug("%s, Reservation unsuccesful", self)
        finally:
            logging.debug("%s Open", self)
            self._lock.release()

        return reservation_success


    def unreserve(self):
        """Removes a reservation"""
        if self._reserved > 0:
            self._reserved -= 1

    def add(self, resource: Resource):
        self._resources.append(resource)
        logging.debug("%s, one %s added", self, resource)
    
    def get(self) -> Resource:
        """Returns one Resource, returns None if empty"""
        if len(self._resources) > 0:
            self.unreserve()
            resource = self._resources.popleft()
            return resource

    def __len__(self) -> int:
        return len(self._resources)

    def __str__(self) -> str:
        result = f"{self.__class__.__name__}[{len(self._resources)}, {self._reserved}, {hex(id(self))}]"
        return result


class Barn(Place):
    def __init__(self):
        super().__init__()

        
class Storage(Place):
    def __init__(self):
        super().__init__()

    def get(self) -> Product:
        """Returns a product"""
        if len(self._resources) > 0:
            logging.debug("%s sends one product", self)
            self.unreserve()
            return self._resources.pop()


class Barrack(Place):
    def __init__(self):
        super().__init__()

    def add(self, worker:Worker):
        """Add a worker to the barrack"""
        if worker.vitality > 0:
            self._resources.append(worker)
            logging.debug("%s, %s returned", self, worker)
        else:
            logging.debug("%s, %s dead", self, worker)


class Transition(Thread):
    def __init__(self, barrack_in:Barrack, barrack_out:Barrack):
        super().__init__()
        self._barrack_in = barrack_in
        self._barrack_out = barrack_out

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{hex(id(self))}]"


class Field(Transition):
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, barn_out: Barn, stop_event:Event):
        super().__init__(barrack_in, barrack_out)
        self._barn_out = barn_out
        self._stop_event = stop_event

    def run(self):
        """Do farming"""
        while not self._stop_event.is_set():
            logging.debug("%s attempts to reserve 1 from %s", self, self._barrack_in)
            if not self._barrack_in.reserve():
                logging.debug("%s empty: %s", self, self._barrack_in)
                continue

            logging.debug("%s retrieving 1 from %s", self, self._barrack_in)
            worker = self._barrack_in.get()
            vitality_change = 0
            if (random() > 0.8):
                vitality_change = -randrange(30,80)
            worker.change_vitality(vitality_change)

            logging.debug("%s sent food to %s, %s harmed %s", self, self._barn_out , worker, vitality_change)
            self._barrack_out.add(worker)
            self._barn_out.add(Food(random()))


class DiningHall(Transition):
    def __init__(self, barrack_in:Barrack, barrack_out:Barrack, barn_in:Barn, stop_event:Event):
        super().__init__(barrack_in, barrack_out)
        self._barn_in = barn_in
        self._stop_event = stop_event

    def run(self):
        """Do eating"""
        while not self._stop_event.is_set():
            logging.debug("%s attempting to reserve a worker from %s", self, self._barrack_in)
            if not self._barrack_in.reserve():
                logging.debug("%s empty: %s", self, self._barrack_in)
                continue

            logging.debug("%s attempting to reserve a food from %s", self, self._barn_in)
            if not self._barn_in.reserve():
                self._barrack_in.unreserve()
                logging.debug("%s empty: %s", self, self._barn_in)
                continue

            logging.debug("%s retrieving 1 from %s, 1 from %s",self, self._barn_in, self._barrack_in)
            food = self._barn_in.get()
            worker = self._barrack_in.get()
            vitality_change = (int)(math.atan(6*food.get_quality()-2)*25)
            worker.change_vitality(vitality_change)

            logging.debug("%s feeding worker %s, energy %s", self, worker, vitality_change)
            self._barrack_out.add(worker)


class Home(Transition):
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, storage_in: Storage, stop_event:Event):
        super().__init__(barrack_in, barrack_out)
        self._storage_in = storage_in
        self._stop_event = stop_event
    
    def run(self):
        """Do resting"""
        while not self._stop_event.is_set():
            logging.debug("%s attempting to reserve a product", self)
            if not self._storage_in.reserve():
                logging.debug("%s empty: %s", self, self._storage_in)
                continue

            logging.debug("%s attempting to reserve a worker", self)
            if not self._barrack_in.reserve():
                self._storage_in.unreserve()
                logging.debug("%s empty: %s", self, self._barrack_in)
                continue

            self._storage_in.get()

            barrack_has_worker_2 = False
            if random() > 0.5:
                barrack_has_worker_2 = self._barrack_in.reserve()

            if barrack_has_worker_2:
                logging.debug("%s retrieving 2 workers from %s", self, self._barrack_in)
                worker_1 = self._barrack_in.get()
                worker_2 = self._barrack_in.get()
                worker_3 = Worker()

                logging.debug("%s: new %s + %s -> %s", self, worker_1, worker_2, worker_3)
                self._barrack_out.add(worker_1)
                self._barrack_out.add(worker_2)
                self._barrack_out.add(worker_3)
            else:
                logging.debug("%s retrieving 1 worker from %s", self, self._barrack_in)
                worker_1 = self._barrack_in.get()
                vitality_change = randrange(10,35)
                worker_1.change_vitality(vitality_change)
                logging.debug("%s: Resting %s, plus %s", self, worker_1, vitality_change)


class Factory(Transition):
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, storage_out: Storage, stop_event:Event):
        super().__init__(barrack_in,barrack_out)
        self._storage_out = storage_out
        self._harm_level = randrange(0,10)
        self._stop_event = stop_event
    
    def run(self):
        """Do work"""
        while not self._stop_event.is_set():
            logging.debug("%s attempting to reserve from %s", self, self._barrack_in)
            if not self._barrack_in.reserve():
                logging.debug("%s failed to reserve worker", self)
                continue
            logging.debug("%s retrieving 1 worker from %s", self, self._barrack_in)
            worker = self._barrack_in.get()

            x = random()
            vitality_change = (int)(-90*(x**2) - self._harm_level)
            worker.change_vitality(vitality_change)

            logging.debug("%s: product sent to %s), %s harmed %s", self, self._storage_out, worker, vitality_change)
            self._storage_out.add(Product())
            self._barrack_out.add(worker)


class World:    
    def __init__(self, barrack_size:int, storage_size:int, barn_size:int, dining_halls_size:int, homes_size:int, fields_size:int, factories_size:int, workers_size:int):
        self.stop = False
        if barrack_size < 1 or storage_size < 1 or barn_size < 1:
            self.stop = True
            return

        self._stop_event = Event()

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
            transit = transition_type(b1,b2,out,self._stop_event)
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
        if self.stop:
            return

        t:Transition
        for t in self._transitions:
            t.start()

        time.sleep(0.15)
        self._stop_event.set()

        for t in self._transitions:
            t.join()


if __name__=='__main__':
    logging.basicConfig(filename='sim.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
    logging.info("Program started")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)

    w1 = World(1, 1, 1, 5, 5, 5, 5,10)
    w1.Simulate()
    logging.info("Program ended")
