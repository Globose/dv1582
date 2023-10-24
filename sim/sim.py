from collections import deque
from random import randrange, random
from typing import Type
import logging
import math
from threading import Thread, Event, Lock
import time
from simsimsgui import GUIPlaceComponent as GuiComp, SimSimsGUI

TIME_OUT = 1
WAIT_TIME = 1

class GUIObject:
    def __init__(self, gui:GuiComp):
        self._gui = gui

    def get_gui(self) -> GuiComp:
        return self._gui

class Resource(GUIObject):
    def __init__(self, gui:GuiComp):
        """Resource Constructor"""
        super().__init__(gui)
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__} [{hex(id(self))}]"


class Worker(Resource):
    def __init__(self, gui:GuiComp):
        """Initializes the Worker with _vitality = 100"""
        super().__init__(gui)
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
    def __init__ (self, quality:float, gui:GuiComp):
        super().__init__(gui)
        self._quality = quality

    def get_quality(self) -> float:
        """Returns quality of the food"""
        return self._quality


class Product(Resource):
    """Product"""
    def __init__(self, gui:GuiComp):
        super().__init__(gui)


class Place(GUIObject):
    def __init__(self, gui:GuiComp):
        super().__init__(gui)
        self._resources = deque()
        self._reserved = 0
        self._lock = Lock()

    def reserve(self) -> bool:
        """Returns False if empty, otherwise returns True and saves a resource to retrieve later"""
        reservation_success = False
        self._lock.acquire()
        try:
            if len(self._resources) - self._reserved > 0:
                self._reserved += 1
                reservation_success = True
                logging.debug("%s Reservation successful", self)
            else:
                logging.debug("%s Reservation unsuccessful", self)
        finally:
            self._lock.release()

        return reservation_success


    def unreserve(self):
        """Removes a reservation"""
        if self._reserved > 0:
            self._reserved -= 1

    def add(self, resource: Resource):
        self._resources.append(resource)
        self._gui.add_token(resource.get_gui())
        logging.debug("%s, one %s added", self, resource)
    
    def get(self) -> Resource:
        """Returns one Resource, returns None if empty"""
        if len(self._resources) > 0:
            logging.debug("%s sends one resource", self)

            resource:Resource
            resource = self._resources.popleft()
            self._gui.remove_token(resource.get_gui())
            self.unreserve()

            return resource
        logging.debug("%s is empty, returns None", self)

    def __len__(self) -> int:
        return len(self._resources)

    def __str__(self) -> str:
        result = f"{self.__class__.__name__}[{len(self._resources)}, {self._reserved}, {hex(id(self))}]"
        return result


class Barn(Place):
    def __init__(self, gui:GuiComp):
        super().__init__(gui)

        
class Storage(Place):
    def __init__(self, gui:GuiComp):
        super().__init__(gui)

    def get(self) -> Product:
        """Returns a product"""
        if len(self._resources) > 0:
            logging.debug("%s sends one product", self)
            resource = self._resources.pop()
            self._gui.remove_token(resource.get_gui())
            self.unreserve()
            return resource
        logging.debug("%s is empty, returns None", self)

class Barrack(Place):
    def __init__(self, gui:GuiComp):
        super().__init__(gui)

    def add(self, worker:Worker):
        """Add a worker to the barrack"""
        if worker.vitality > 0:
            self._resources.append(worker)
            self._gui.add_token(worker.get_gui())
            logging.debug("%s, %s returned", self, worker)
        else:
            logging.debug("%s, %s dead", self, worker)


class Transition(Thread, GUIObject):
    def __init__(self, barrack_in:Barrack, barrack_out:Barrack, gui:GuiComp, sim_gui:SimSimsGUI):
        Thread.__init__(self)
        GUIObject.__init__(self, gui)
        self._barrack_in = barrack_in
        self._barrack_out = barrack_out
        self._gui = gui
        self._sim_gui = sim_gui

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{hex(id(self))}]"


class Field(Transition):
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, barn_out: Barn, stop_event:Event, gui:GuiComp, sim_gui:SimSimsGUI):
        super().__init__(barrack_in, barrack_out, gui, sim_gui)
        self._barn_out = barn_out
        self._stop_event = stop_event

    def run(self):
        """Do farming"""
        while not self._stop_event.is_set():
            time.sleep(TIME_OUT)
            logging.debug("%s attempts to reserve 1 from %s", self, self._barrack_in)
            if not self._barrack_in.reserve():
                logging.debug("%s empty: %s", self, self._barrack_in)
                continue

            logging.debug("%s retrieving 1 from %s", self, self._barrack_in)
            worker = self._barrack_in.get()
            self._gui.add_token(worker.get_gui())
            time.sleep(WAIT_TIME)

            food = Food(random(),self._sim_gui.create_token_gui({"color": "#11aa22"}))
            self._gui.add_token(food.get_gui())
            time.sleep(WAIT_TIME)

            vitality_change = 0
            if (random() > 0.8):
                vitality_change = -randrange(30,80)
            worker.change_vitality(vitality_change)

            logging.debug("%s sent food to %s, %s harmed %s", self, self._barn_out , worker, vitality_change)

            self._gui.remove_token(worker.get_gui())
            self._gui.remove_token(food.get_gui())
            self._barrack_out.add(worker)
            self._barn_out.add(food)



class DiningHall(Transition):
    def __init__(self, barrack_in:Barrack, barrack_out:Barrack, barn_in:Barn, stop_event:Event, gui:GuiComp, sim_gui:SimSimsGUI):
        super().__init__(barrack_in, barrack_out, gui, sim_gui)
        self._barn_in = barn_in
        self._stop_event = stop_event

    def run(self):
        """Do eating"""
        while not self._stop_event.is_set():
            time.sleep(TIME_OUT)
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

            self._gui.add_token(food.get_gui())
            self._gui.add_token(worker.get_gui())
            time.sleep(WAIT_TIME)

            vitality_change = (int)(math.atan(6*food.get_quality()-2)*25)
            worker.change_vitality(vitality_change)

            logging.debug("%s feeding worker %s, energy %s", self, worker, vitality_change)
            self._gui.remove_token(food.get_gui())
            self._gui.remove_token(worker.get_gui())
            self._barrack_out.add(worker)


class Home(Transition):
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, storage_in: Storage, stop_event:Event, gui:GuiComp, sim_gui:SimSimsGUI):
        super().__init__(barrack_in, barrack_out, gui, sim_gui)
        self._storage_in = storage_in
        self._stop_event = stop_event
    
    def run(self):
        """Do resting"""
        while not self._stop_event.is_set():
            time.sleep(TIME_OUT)
            logging.debug("%s attempting to reserve a product", self)
            if not self._storage_in.reserve():
                logging.debug("%s empty: %s", self, self._storage_in)
                continue

            logging.debug("%s attempting to reserve a worker", self)
            if not self._barrack_in.reserve():
                self._storage_in.unreserve()
                logging.debug("%s empty: %s", self, self._barrack_in)
                continue

            logging.debug("%s retrieving 1 product from %s", self, self._storage_in)
            product = self._storage_in.get()
            self._gui.add_token(product.get_gui())

            barrack_has_worker_2 = False
            if random() > 0.5:
                logging.debug("%s attempting to reserve 1 worker", self)
                barrack_has_worker_2 = self._barrack_in.reserve()

            if barrack_has_worker_2:
                logging.debug("%s retrieving 2 workers from %s", self, self._barrack_in)
                worker_1 = self._barrack_in.get()
                worker_2 = self._barrack_in.get()

                self._gui.add_token(worker_1.get_gui())
                self._gui.add_token(worker_2.get_gui())
                time.sleep(WAIT_TIME)

                worker_3 = Worker(self._sim_gui.create_token_gui({"lable": "Worker"}))

                self._gui.add_token(worker_3.get_gui())
                time.sleep(WAIT_TIME)

                logging.debug("%s: new %s + %s -> %s", self, worker_1, worker_2, worker_3)
                self._barrack_out.add(worker_1)
                self._barrack_out.add(worker_2)
                self._barrack_out.add(worker_3)
                self._gui.remove_token(worker_1.get_gui())
                self._gui.remove_token(worker_2.get_gui())
                self._gui.remove_token(worker_3.get_gui())

            else:
                logging.debug("%s retrieving 1 worker from %s", self, self._barrack_in)
                worker_1 = self._barrack_in.get()
                self._gui.add_token(worker_1.get_gui())
                time.sleep(WAIT_TIME)

                vitality_change = randrange(10,35)
                worker_1.change_vitality(vitality_change)
                logging.debug("%s: Resting %s, plus %s", self, worker_1, vitality_change)
                self._barrack_out.add(worker_1)
                self._gui.remove_token(worker_1.get_gui())
            self._gui.remove_token(product.get_gui())


class Factory(Transition):
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, storage_out: Storage, stop_event:Event, gui:GuiComp, sim_gui:SimSimsGUI):
        super().__init__(barrack_in,barrack_out, gui, sim_gui)
        self._storage_out = storage_out
        self._harm_level = randrange(0,10)
        self._stop_event = stop_event
    
    def run(self):
        """Do work"""
        while not self._stop_event.is_set():
            time.sleep(TIME_OUT)
            logging.debug("%s attempting to reserve from %s", self, self._barrack_in)
            if not self._barrack_in.reserve():
                logging.debug("%s failed to reserve worker", self)
                continue
            logging.debug("%s retrieving 1 worker from %s", self, self._barrack_in)
            worker = self._barrack_in.get()
            self._gui.add_token(worker.get_gui())
            time.sleep(WAIT_TIME)

            product = Product(self._sim_gui.create_token_gui({"color": "#ee3322"}))
            self._gui.add_token(product.get_gui())
            time.sleep(WAIT_TIME)

            x = random()
            vitality_change = (int)(-90*(x**2) - self._harm_level)
            worker.change_vitality(vitality_change)

            logging.debug("%s: product sent to %s), %s harmed %s", self, self._storage_out, worker, vitality_change)

            self._gui.remove_token(worker.get_gui())
            self._gui.remove_token(product.get_gui())
            self._storage_out.add(product)
            self._barrack_out.add(worker)


class World:    
    def __init__(self, barrack_size:int, storage_size:int, barn_size:int, dining_halls_size:int, homes_size:int, fields_size:int, factories_size:int, workers_size:int):
        self.stop = False
        if barrack_size < 1 or storage_size < 1 or barn_size < 1:
            self.stop = True
            return

        self._gui = SimSimsGUI(1000, 600)
        self._stop_event = Event()

        self._day = 0
        self._barracks = [Barrack(self._gui.create_place_gui({"lable": "Barrack"})) for _ in range(barrack_size)]
        self._storage = [Storage(self._gui.create_place_gui({"lable": "Storage"})) for _ in range(storage_size)]
        self._barns = [Barn(self._gui.create_place_gui({"lable": "Barn"})) for _ in range(barn_size)]
        logging.info("Added barracks (%s), storages (%s), barns (%s)", barrack_size, storage_size, barn_size)

        self._transitions = []
        self._connect_transition(DiningHall, self._barns, dining_halls_size, "Dining Hall")
        self._connect_transition(Home, self._storage, homes_size, "Home")
        self._connect_transition(Field, self._barns, fields_size, "Field")
        self._connect_transition(Factory, self._storage, factories_size, "Factory")

        for _ in range(workers_size):
            self._barracks[randrange(len(self._barracks))].add(Worker(self._gui.create_token_gui({"lable": "Worker"})))

        self._init_gui()

        logging.info("Added dining halls (%s), homes (%s), fields (%s), factories (%s), workers (%s)"
                     , dining_halls_size, homes_size, fields_size, factories_size, workers_size)

    def _init_gui(self):
        """Creates UI elements"""
        place_list = self._barns+self._barracks+self._storage
        transitions_len = len(self._transitions)
        places_len = len(place_list)

        t:Transition
        for i,t in enumerate(self._transitions):
            t.get_gui().autoplace(i, transitions_len+places_len)

        p:Place
        for i, p in enumerate(place_list):
            p.get_gui().autoplace(i+transitions_len, places_len+transitions_len)

        self._gui.start()

    def _connect_transition(self, transition_type:Type[Transition], place_others:list[Transition], size:int, label:str):
        for _ in range(size):
            barrack_1 = self._barracks[randrange(len(self._barracks))]
            barrack_2 = self._barracks[randrange(len(self._barracks))]
            place_other = place_others[randrange(len(place_others))]
            transit = transition_type(barrack_1,barrack_2,place_other,self._stop_event, self._gui.create_transition_gui({"lable":label}),self._gui)

            if transition_type == DiningHall or transition_type == Home:
                self._gui.connect(place_other.get_gui(), transit.get_gui(),{"arrows": True})
            else:
                self._gui.connect(transit.get_gui(), place_other.get_gui(),{"arrows": True})
            self._gui.connect(barrack_1.get_gui(), transit.get_gui(),{"arrows": True})
            self._gui.connect(transit.get_gui(),barrack_2.get_gui(),{"arrows": True})

            self._transitions.append(transit)
            logging.debug("Connecting %s to %s, %s, %s",
                    transit, barrack_1, barrack_2, place_other)

    def _sim_finished(self):
        b: Barrack
        for b in self._barracks:
            if not b.is_empty():
                return False
        return True

    def _gui_update(self):
        i = 0
        while self._gui.is_alive:

            time.sleep(0.06)

    def Simulate(self):
        if self.stop:
            return

        thread_1 = Thread(target=self._gui_update)
        thread_1.start()

        t:Transition
        for t in self._transitions:
            t.start()
            time.sleep(0.1)

        self._gui.mainloop()

        self._stop_event.set()
        for t in self._transitions:
            t.join()


if __name__=='__main__':
    logging.basicConfig(filename='sim.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
    logging.info("Program started")

    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.DEBUG)
    # root_logger = logging.getLogger()
    # root_logger.addHandler(console_handler)

    w1 = World(1, 1, 1, 4, 4, 7, 4,20)
    w1.Simulate()
    logging.info("Program ended")
