from collections import deque
from random import randrange, random
from typing import Type
import logging
import math
from threading import Thread, Event, Lock
import time
from simsimsgui import GUIPlaceComponent as GuiComp, SimSimsGUI
from pydb import Analytics

COLOR_FOOD = "#11aa22"
COLOR_WORKER = "#1122aa"
COLOR_PRODUCT = "#ee3322"
SQL_FILE = "sqldb.db"
XLSX_PATH = "resources.xlsx"
TABLE_NAME = "Resources"
TARGET_FOOD = 40
TARGET_WORKERS = 40
TARGET_PRODUCTS = 50


class GUIObject:
    """Graphics object class"""
    def __init__(self, gui: GuiComp):
        self._gui = gui

    def get_gui(self) -> GuiComp:
        """Returns the GuiComp object"""
        return self._gui


class Resource(GUIObject):
    """Resource/token class"""
    def __init__(self, gui: GuiComp):
        """Resource Constructor"""
        super().__init__(gui)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} [{hex(id(self))}]"


class Worker(Resource):
    """Class representing a worker resource"""
    def __init__(self, gui: GuiComp):
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
    """Class representing a Food resource"""
    def __init__(self, quality: float, gui: GuiComp):
        super().__init__(gui)
        self._quality = quality

    def get_quality(self) -> float:
        """Returns the quality of the food"""
        return self._quality


class Product(Resource):
    """Class representing a Product resource"""
    def __init__(self, gui: GuiComp):
        super().__init__(gui)


class Place(GUIObject):
    """Class representing a graphical object with storage capabilities"""
    def __init__(self, gui: GuiComp):
        super().__init__(gui)
        self._resources = deque()
        self._reserved = 0
        self._lock = Lock()

    def reserve(self) -> bool:
        """Returns False if empty, otherwise returns True
        and saves a resource to retrieve later"""
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
        logging.debug("%s unreserve", self)
        if self._reserved > 0:
            self._reserved -= 1

    def add(self, resource: Resource):
        """Add a resource to the last place"""
        self._resources.append(resource)
        self._gui.add_token(resource.get_gui())
        logging.debug("%s, one %s added", self, resource)

    def get(self) -> Resource:
        """Returns the oldest Resource, returns None if empty"""
        if len(self._resources) > 0:
            logging.debug("%s sends one resource", self)
            resource = self._resources.popleft()
            self._gui.remove_token(resource.get_gui())
            logging.debug("%s has removed token")
            self.unreserve()
            logging.debug("%s has unreserved")

            return resource
        logging.debug("%s is empty, returns None", self)

    def __len__(self) -> int:
        return len(self._resources)

    def __str__(self) -> str:
        result = f"{self.__class__.__name__}[{len(self._resources)}, {self._reserved}, {hex(id(self))}]"
        return result


class Barn(Place):
    """Class representing a Barn place"""
    def __init__(self, gui: GuiComp):
        super().__init__(gui)


class Storage(Place):
    """Class representing a Storage place with a stack"""
    def __init__(self, gui: GuiComp):
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
    """Class for storing Workers in a queue"""
    def __init__(self, gui: GuiComp):
        super().__init__(gui)

    def add(self, worker: Worker):
        """Add a worker to the barrack"""
        if worker.vitality > 0:
            self._resources.append(worker)
            self._gui.add_token(worker.get_gui())
            logging.debug("%s, %s returned", self, worker)
        else:
            logging.debug("%s, %s dead", self, worker)

    def __str__(self) -> str:
        result = f"{self.__class__.__name__}[{len(self._resources)}, {self._reserved}, {hex(id(self))}]"
        return result


class Transition(Thread, GUIObject):
    """Class that represents transitions"""
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack,
                 gui: GuiComp, sim_gui: SimSimsGUI):
        Thread.__init__(self)
        GUIObject.__init__(self, gui)
        self.barrack_in = barrack_in
        self.barrack_out = barrack_out
        self._gui = gui
        self._sim_gui = sim_gui
        self._closed = False

    def is_closed(self) -> bool:
        """Returns True if transition is closed, otherwise False"""
        return self._closed

    def toggle_closed(self):
        """Sets closed to the opposite value it currently has"""
        self._closed = not self._closed

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{hex(id(self))}]"

    def _retrieve(self, place: Place) -> Resource:
        logging.debug("%s retrieving 1 from %s", self, place)
        resource = place.get()
        if resource is not None:
            self._gui.add_token(resource.get_gui())
        return resource

    def _reserve(self, place: Place) -> bool:
        logging.debug("%s attempts to reserve 1 from %s", self, place)
        reservation = place.reserve()
        if not reservation:
            logging.debug("%s empty: %s", self, self.barrack_in)
        return reservation

    def _send_resource(self, resource: Resource, place: Place):
        logging.debug("%s sent %s to %s", self, resource, place)
        self._gui.remove_token(resource.get_gui())
        place.add(resource)


class Field(Transition):
    """Field class representing a field that produces food"""
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack,
                 barn_out: Barn, stop_event: Event, gui: GuiComp,
                 sim_gui: SimSimsGUI):
        super().__init__(barrack_in, barrack_out, gui, sim_gui)
        self.barn_out = barn_out
        self._stop_event = stop_event

    def run(self):
        """Run method that creates food"""
        while not self._stop_event.is_set():
            if self._closed:
                time.sleep(0.5)
                continue

            if not self._reserve(self.barrack_in):
                continue
            worker = self._retrieve(self.barrack_in)

            if worker is None:
                continue

            food = Food(random(), self._sim_gui.create_token_gui
                        ({"color": COLOR_FOOD}))
            self._gui.add_token(food.get_gui())

            vitality_change = 0
            if random() > 0.8:
                vitality_change = -randrange(30, 80)
            worker.change_vitality(vitality_change)

            self._send_resource(worker, self.barrack_out)
            self._send_resource(food, self.barn_out)


class DiningHall(Transition):
    """Dininghall transition where workers eat food"""
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack,
                 barn_in: Barn, stop_event: Event, gui: GuiComp,
                 sim_gui: SimSimsGUI):
        super().__init__(barrack_in, barrack_out, gui, sim_gui)
        self.barn_in = barn_in
        self._stop_event = stop_event

    def run(self):
        """Run method that repeats the dining process"""
        while not self._stop_event.is_set():
            if self._closed:
                time.sleep(0.5)
                continue

            if not self._reserve(self.barrack_in):
                continue

            if not self._reserve(self.barn_in):
                self.barrack_in.unreserve()
                continue

            food = self._retrieve(self.barn_in)
            worker = self._retrieve(self.barrack_in)
            if worker is None:
                continue

            logging.debug("%s food %s, worker %s", self, food, worker)

            vitality_change = (int)(math.atan(6*food.get_quality()-2)*25)
            worker.change_vitality(vitality_change)
            self._gui.remove_token(food.get_gui())
            self._send_resource(worker, self.barrack_out)


class Home(Transition):
    """Home Transition representing a resting area for workers"""
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack,
                 storage_in: Storage, stop_event: Event, gui: GuiComp,
                 sim_gui: SimSimsGUI):
        super().__init__(barrack_in, barrack_out, gui, sim_gui)
        self.storage_in = storage_in
        self._stop_event = stop_event
        self._priority = 0.5

    def change_priority(self, amount: float):
        """Change if home priorities to reproduce or rest
        Higher priority = smaller chance to reproduce
        """
        self._priority += amount
        if self._priority > 1:
            self._priority = 1
        elif self._priority < 0:
            self._priority = 0

    def run(self):
        """Run method that repeats the resting process"""
        while not self._stop_event.is_set():
            if self._closed:
                time.sleep(0.5)
                continue

            if not self._reserve(self.storage_in):
                continue

            if not self._reserve(self.barrack_in):
                self.storage_in.unreserve()
                continue

            product = self._retrieve(self.storage_in)

            barrack_has_worker_2 = False
            if random() > self._priority:
                barrack_has_worker_2 = self.barrack_in.reserve()

            if barrack_has_worker_2:
                worker_1 = self._retrieve(self.barrack_in)
                worker_2 = self._retrieve(self.barrack_in)

                if worker_1 is None:
                    self._send_resource(worker_2, self.barrack_out)
                    continue
                if worker_2 is None:
                    self._send_resource(worker_1, self.barrack_out)
                    continue

                worker_3 = Worker(self._sim_gui.create_token_gui
                                  ({"color": COLOR_WORKER}))
                self._gui.add_token(worker_3.get_gui())
                logging.debug("%s: new %s + %s -> %s", self,
                              worker_1, worker_2, worker_3)

                self._send_resource(worker_1, self.barrack_out)
                self._send_resource(worker_2, self.barrack_out)

                self.barrack_out.add(worker_3)
                self._gui.remove_token(worker_3.get_gui())
            else:
                worker_1 = self._retrieve(self.barrack_in)
                if worker_1 is None:
                    continue

                vitality_change = randrange(10, 35)
                worker_1.change_vitality(vitality_change)
                logging.debug("%s: Resting %s, plus %s", self,
                              worker_1, vitality_change)
                self._send_resource(worker_1, self.barrack_out)
            self._gui.remove_token(product.get_gui())


class Factory(Transition):
    """A Factory that produces products"""
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack,
                 storage_out: Storage, stop_event: Event,
                 gui: GuiComp, sim_gui: SimSimsGUI):
        super().__init__(barrack_in, barrack_out, gui, sim_gui)
        self.storage_out = storage_out
        self._harm_level = randrange(0, 10)
        self._stop_event = stop_event

    def run(self):
        """Run method that repeats the manufacturing process"""
        while not self._stop_event.is_set():
            if self._closed:
                time.sleep(0.5)
                continue

            if not self._reserve(self.barrack_in):
                continue

            worker = self._retrieve(self.barrack_in)
            if worker is None:
                continue

            product = Product(self._sim_gui.create_token_gui
                              ({"color": COLOR_PRODUCT}))
            self._gui.add_token(product.get_gui())

            vitality_change = (int)(-40*(random()**2) - self._harm_level)
            worker.change_vitality(vitality_change)

            self._send_resource(worker, self.barrack_out)
            self._send_resource(product, self.storage_out)


class World:
    """Main class responsible for the entire simulation process"""
    def __init__(self, barrack_size: int, storage_size: int, barn_size: int,
                 dining_halls_size: int, homes_size: int, fields_size: int,
                 factories_size: int, workers_size: int):
        self.stop = False
        if barrack_size < 1 or storage_size < 1 or barn_size < 1:
            self.stop = True
            return

        self._home_count = homes_size
        self._fields_count = fields_size
        self._dining_halls_count = dining_halls_size
        self._factories_count = factories_size

        self._gui = SimSimsGUI(1000, 600)
        self._stop_event = Event()

        self._day = 0
        self._barracks = [Barrack(self._gui.create_place_gui(
            {"lable": "Barrack"}))for _ in range(barrack_size)]
        self._storage = [Storage(self._gui.create_place_gui(
            {"lable": "Storage"})) for _ in range(storage_size)]
        self._barns = [Barn(self._gui.create_place_gui(
            {"lable": "Barn"})) for _ in range(barn_size)]
        logging.info("Added barracks (%s), storages (%s), barns (%s)",
                     barrack_size, storage_size, barn_size)

        self._transitions = []
        self._connect_transition(DiningHall, self._barns,
                                 dining_halls_size, "Dining Hall")
        self._connect_transition(Home, self._storage,
                                 homes_size, "Home")
        self._connect_transition(Field, self._barns,
                                 fields_size, "Field")
        self._connect_transition(Factory, self._storage,
                                 factories_size, "Factory")

        for _ in range(workers_size):
            self._barracks[randrange(len(self._barracks))].add(
                Worker(self._gui.create_token_gui({"color": COLOR_WORKER})))
        self._init_gui()

    def _init_gui(self):
        """Initializes the UI elements"""
        place_list = self._barns+self._barracks+self._storage
        transitions_len = len(self._transitions)
        places_len = len(place_list)

        t: Transition
        for i, t in enumerate(self._transitions):
            t.get_gui().autoplace(i, transitions_len+places_len)

        p: Place
        for i, p in enumerate(place_list):
            p.get_gui().autoplace(
                i+transitions_len, places_len + transitions_len)

        self._gui.start()

    def _connect_transition(self, transition_type: Type[Transition],
                            place_others: list[Transition],
                            size: int, label: str):
        """Creates transitions and connects them to places"""
        for _ in range(size):
            barrack_1 = self._barracks[randrange(len(self._barracks))]
            barrack_2 = self._barracks[randrange(len(self._barracks))]
            place_other = place_others[randrange(len(place_others))]
            transit = transition_type(
                barrack_1, barrack_2, place_other, self._stop_event,
                self._gui.create_transition_gui({"lable": label}), self._gui)

            if transition_type == DiningHall or transition_type == Home:
                self._gui.connect(place_other.get_gui(),
                                  transit.get_gui(), {"arrows": True})
            else:
                self._gui.connect(transit.get_gui(), place_other.get_gui(),
                                  {"arrows": True})
            self._gui.connect(barrack_1.get_gui(), transit.get_gui(),
                              {"arrows": True})
            self._gui.connect(transit.get_gui(), barrack_2.get_gui(),
                              {"arrows": True})

            self._transitions.append(transit)

    def _sim_finished(self):
        """Determines when the simulation is done"""
        start_time = time.time()
        while not self._stop_event.is_set():
            stop_sim = True
            b: Barrack
            for b in self._barracks:
                if len(b) > 0:
                    stop_sim = False
                    break

            if time.time() - start_time > 70:
                stop_sim = True

            if stop_sim:
                logging.info("Sim finished")
                self._stop_event.set()
            time.sleep(0.05)

    def _resource_count(self) -> tuple[int, int, int]:
        """Counts the number of workers, products and food in the world"""
        workers_count = 0
        b: Barrack
        for b in self._barracks:
            workers_count += len(b)

        product_count = 0
        s: Storage
        for s in self._storage:
            product_count += len(s)

        food_count = 0
        b: Barn
        for b in self._barns:
            food_count += len(b)

        return (workers_count, product_count, food_count)

    def _observer(self):
        """Logs resources and store them in a database and xlsx"""
        start_time = time.time()
        analytics = Analytics(SQL_FILE, TABLE_NAME)
        analytics.create_table()

        while True:
            workers_count, product_count, food_count = self._resource_count()

            cur_time = (int)((time.time()-start_time)*1000)
            analytics.add_step(cur_time, workers_count,
                               product_count, food_count)
            if self._stop_event.is_set():
                break
            time.sleep(0.1)
        analytics.save_to_xlsx(XLSX_PATH)
        logging.info("Saved to xlsx")

    def _stabilizer(self):
        """Adjusts the transitions to that the resources are balanced"""
        while not self._stop_event.is_set():
            workers_count, product_count, food_count = self._resource_count()
            alter_home = 0
            if workers_count > TARGET_WORKERS*1.2:
                alter_home = 0.2
            elif workers_count < TARGET_WORKERS*.8:
                alter_home = -0.2

            factory_closed = dining_hall_closed = 0
            field_closed = home_closed = 0

            t: Transition
            for t in self._transitions:
                if isinstance(t, Home):
                    t.change_priority(alter_home*random())
                    if t.is_closed():
                        home_closed += 1
                if isinstance(t, Factory) and t.is_closed():
                    factory_closed += 1
                if isinstance(t, DiningHall) and t.is_closed():
                    dining_hall_closed += 1
                if isinstance(t, Field) and t.is_closed():
                    field_closed += 1

            self._stabilize_transition(self._home_count, workers_count,
                                       TARGET_WORKERS, home_closed, Home)
            self._stabilize_transition(self._dining_halls_count,
                                       workers_count, TARGET_WORKERS,
                                       dining_hall_closed, DiningHall)
            self._stabilize_transition(self._fields_count, food_count,
                                       TARGET_FOOD, field_closed, Field)
            self._stabilize_transition(self._factories_count,
                                       product_count, TARGET_PRODUCTS,
                                       factory_closed, Factory)
            self._rearrange_connections()
            time.sleep(0.2)

    def _stabilize_transition(self, tran_count: int,
                              resources_count: int, target_resources: int,
                              closed_count: int, t_type: Type[Transition]):
        """Turns transitions off and on based on resource count"""
        closed_target = min(tran_count-1, max(0, (int)(
            tran_count*(resources_count-target_resources)/target_resources)))

        if not closed_target == closed_count:
            t: Transition
            for t in self._transitions:
                if (isinstance(t, t_type)
                        and t.is_closed() == (closed_count > closed_target)):
                    t.toggle_closed()
                    break

    def _rearrange_connections(self):
        """Rearrages transition connections for
        more evenly distributed resources"""
        t: Transition
        t = self._transitions[randrange(len(self._transitions))]
        self._gui.disconnect(t.get_gui(), t.barrack_out.get_gui())
        self._gui.disconnect(t.barrack_in.get_gui(), t.get_gui())
        t.barrack_in = max(self._barracks, key=len)
        t.barrack_out = min(self._barracks, key=len)
        self._gui.connect(t.barrack_in.get_gui(), t.get_gui())
        self._gui.connect(t.get_gui(), t.barrack_out.get_gui())

        if isinstance(t, Home):
            self._gui.disconnect(t.storage_in.get_gui(), t.get_gui())
            t.storage_in = max(self._storage, key=len)
            self._gui.connect(t.storage_in.get_gui(), t.get_gui())
        elif isinstance(t, DiningHall):
            self._gui.disconnect(t.barn_in.get_gui(), t.get_gui())
            t.barn_in = max(self._barns, key=len)
            self._gui.connect(t.barn_in.get_gui(), t.get_gui())
        elif isinstance(t, Factory):
            self._gui.disconnect(t.get_gui(), t.storage_out.get_gui())
            t.storage_out = min(self._storage, key=len)
            self._gui.connect(t.get_gui(), t.storage_out.get_gui())
        elif isinstance(t, Field):
            self._gui.disconnect(t.get_gui(), t.barn_out.get_gui())
            t.barn_out = min(self._barns, key=len)
            self._gui.connect(t.get_gui(), t.barn_out.get_gui())

    def simulate(self):
        """Starts the world simulation"""
        if self.stop:  # If less than one barrack, barn and storage
            return

        threads = [Thread(target=self._sim_finished),
                   Thread(target=self._observer),
                   Thread(target=self._stabilizer)]

        t: Thread
        for t in threads:
            t.start()

        t: Transition
        for t in self._transitions:
            t.start()

        self._gui.mainloop()
        self._stop_event.set()
        threads[1].join()


def main():
    """Main function"""
    logging.basicConfig(filename='sim.log', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filemode='w')
    logging.info("Program started")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)

    w1 = World(3, 2, 2, 7, 7, 7, 5, 50)
    w1.simulate()
    logging.info("Program ended")

    logging.info("Creating diagram")
    analytics = Analytics(SQL_FILE, TABLE_NAME)
    analytics.to_figure()


if __name__ == '__main__':
    main()
