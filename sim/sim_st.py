from collections import deque
from random import randrange


class Worker:
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


class Food:
    def __init__(self, quality: float):
        self._quality = quality

    def get_quality(self) -> float:
        """Returns quality of the food"""
        return self._quality


class Product:
    """Product"""
    def __init__(self):
        """Product constructor"""


class Barn:
    def __init__(self):
        self._food = deque()

    def get_food(self) -> Food:
        """Returns one food, returns None if empty"""
        if len(self._food) > 0:
            return self._food.popleft()

    def add_food(self, food: Food):
        """Add food to barn"""
        self._food.append(food)

    def is_empty(self) -> bool:
        """Returns true if barn is empty"""
        return len(self._food) == 0

    def __str__(self) -> str:
        return f"Barn ({len(self._food)})"


class Storage():
    def __init__(self):
        self._products = deque()

    def get_product(self) -> Product:
        """Returns a product, returns none if empty"""
        if len(self._products) > 0:
            return self._products.pop()

    def add_product(self, product: Product):
        """Add a product to storage"""
        self._products.append(product)

    def __str__(self) -> str:
        return f"Storage ({len(self._products)})"


class Barrack:
    def __init__(self):
        self._workers = deque()

    def get_worker(self) -> Worker:
        """Returns a worker"""
        if len(self._workers) > 0:
            return self._workers.popleft()

    def add_worker(self, worker: Worker):
        """Add a worker to the barrack"""
        if worker.get_vitality() > 0:
            self._workers.append(worker)

    def is_empty(self) -> bool:
        """Returns true if barrack is empty"""
        return len(self._workers) == 0

    def __len__(self) -> int:
        """Returns number of workers in the barrack"""
        return len(self._workers)

    def __str__(self) -> str:
        result = f"Barrack ({len(self._workers)})"

        w: Worker
        for w in self._workers:
            result += f"\n Worker: {w.get_vitality()}"
        return result


class Field:
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, barn_out: Barn):
        self._barrack_in = barrack_in
        self._barrack_out = barrack_out
        self._barn_out = barn_out

    def farm(self):
        if self._barrack_in.is_empty():
            return

        worker = self._barrack_in.get_worker()
        worker.change_vitality(-10)

        self._barrack_out.add_worker(worker)
        self._barn_out.add_food(Food(1))


class DiningHall:
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, barn_in: Barn):
        self._barrack_in = barrack_in
        self._barrack_out = barrack_out
        self._barn_in = barn_in

    def eat(self):
        if self._barrack_in.is_empty() or self._barn_in.is_empty():
            return
        worker = self._barrack_in.get_worker()
        food = self._barn_in.get_food()
        worker.change_vitality(10*food.get_quality())
        self._barrack_out.add_worker(worker)


class Home:
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, storage_in: Storage):
        self._barrack_in = barrack_in
        self._barrack_out = barrack_out
        self._storage_in = storage_in

    def rest(self):
        """Rest"""


class Factory:
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, storage_out: Storage):
        self._barrack_in = barrack_in
        self._barrack_out = barrack_out
        self._storage_out = storage_out

    def work(self):
        if self._barrack_in.is_empty():
            return
        worker = self._barrack_in.get_worker()
        worker.change_vitality(-40)
        self._storage_out.add_product(Product())
        self._barrack_out.add_worker(worker)


class World:
    def __init__(self, barracks_size, storages_size, barns_size,
                 dining_halls_size, homes_size, fields_size, factories_size, workers_size):
        self._day = 0
        self._barracks = [Barrack() for _ in range(barracks_size)]
        self._storages = [Storage() for _ in range(storages_size)]
        self._barns = [Barn() for _ in range(barns_size)]

        self._dining_halls = [DiningHall(self._barracks[randrange(len(self._barracks))],
                                         self._barracks[randrange(len(self._barracks))],
                                         self._barns[randrange(len(self._barns))])
                              for _ in range(dining_halls_size)]

        self._homes = [Home(self._barracks[randrange(len(self._barracks))],
                            self._barracks[randrange(len(self._barracks))],
                            self._storages[randrange(len(self._storages))])
                       for _ in range(homes_size)]

        self._fields = [Field(self._barracks[randrange(len(self._barracks))],
                              self._barracks[randrange(len(self._barracks))],
                              self._barns[randrange(len(self._barns))])
                        for _ in range(fields_size)]

        self._factories = [Factory(self._barracks[randrange(len(self._barracks))],
                                   self._barracks[randrange(len(self._barracks))],
                                   self._storages[randrange(len(self._storages))])
                           for _ in range(factories_size)]

        for _ in range(workers_size):
            self._barracks[randrange(len(self._barracks))].add_worker(Worker())

    def _is_finished(self):
        b: Barrack
        for b in self._barracks:
            if not b.is_empty():
                return False
        return True

    def Simulate(self):
        while not self._is_finished():
            self._day += 1
            print()
            print("Day", self._day)

            f: Factory
            for f in self._factories:
                f.work()

            f: Field
            for f in self._fields:
                f.farm()

            d: DiningHall
            for d in self._dining_halls:
                d.eat()

            h: Home
            for h in self._homes:
                h.rest()

            workers = 0
            b: Barrack
            for b in self._barracks:
                workers += len(b)
            print(f"{workers} alive")

            if self._day > 95:
                break


if __name__ == '__main__':
    w1 = World(1, 10, 10, 10, 10, 10, 10, 100)
    w1.Simulate()
