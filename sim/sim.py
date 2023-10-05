from collections import deque
from random import randrange

class World:    
    def __init__(self):
        self._barracks = []
        self._storages = []
        self._barns = []
        self._dining_halls = []
        self._homes = []
        self._fields = []
        self._factories = []
        
        b1 = Barrack()
        s1 = Storage()
        ba1 = Barn()
        dh1 = DiningHall(b1,b1,ba1)
        h1 = Home(b1, b1, s1)
        f1 = Field(b1, b1, ba1)
        fa1 = Factory(b1,b1,s1)
        
        b1.add_worker(Worker())
        self._barracks.append(b1)
        self._storages.append(s1)
        self._barns.append(ba1)
        self._dining_halls.append(dh1)
        self._homes.append(h1)
        self._fields.append(f1)
        self._factories.append(fa1)


    def _sim_finished(self):
        b: Barrack
        for b in self._barracks:
            if not b.is_empty():
                return False

        return True

    def Simulate(self):
        while not self._sim_finished():
            f: Factory
            for f in self._factories:
                f.work()
            
            f:Field
            for f in self._fields:
                f.farm()
            
            d:DiningHall
            for d in self._dining_halls:
                d.eat()
            
            h:Home
            for h in self._homes:
                h.rest()
        
            b:Barrack
            for b in self._barracks:
                print(b)


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
    def __init__ (self, quality:float):
        self._quality = quality

    def get_quality(self) -> float:
        """Returns quality of the food"""
        return self._quality


class Product:
    """Product"""


class Barn:
    def __init__(self):
        self._food = deque()
    
    def get_food(self) -> Food:
        """Returns one food, returns None if empty"""
        if len(self._food) > 0:
            return self._food.popleft()
        
    def add_food(self, food:Food):
        """Send food to barn"""
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

    def add_product(self, product:Product):
        """Send a product to storage"""
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
    
    def add_worker(self, worker:Worker):
        """Send a worker to the barrack"""
        self._workers.append(worker)
    
    def is_empty(self) -> bool:
        """Returns true if barrack is empty"""
        return len(self._workers) == 0
    
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
        """Farming"""
        print("Farming")
        if self._barrack_in.is_empty():
            return

        print("Creating food")
        worker = self._barrack_in.get_worker()
        print(self._barrack_in.is_empty(), "?")
        worker.change_vitality(-10)
        if worker.get_vitality() > 0:
            self._barrack_out.add_worker(worker)
        self._barn_out.add_food(Food(1))


class DiningHall:
    def __init__(self, barrack_in:Barrack, barrack_out:Barrack, barn_in:Barn):
        self._barrack_in = barrack_in
        self._barrack_out = barrack_out
        self._barn_in = barn_in
        
    def eat(self):
        """Eating"""
        print("Eating")
        if self._barrack_in.is_empty() or self._barn_in.is_empty():
            return
        print("Worker eats")
        worker = self._barrack_in.get_worker()
        food = self._barn_in.get_food()
        worker.change_vitality(10*food.get_quality())
        
        if worker.get_vitality() > 0:
            self._barrack_out.add_worker(worker)


class Home:
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, storage_in: Storage):
        self._barrack_in = barrack_in
        self._barrack_out = barrack_out
        self._storage_in = storage_in
    
    def rest(self):
        """Rest"""
        print("Resting")


class Factory:
    def __init__(self, barrack_in: Barrack, barrack_out: Barrack, storage_out: Storage):
        self._barrack_in = barrack_in
        self._barrack_out = barrack_out
        self._storage_out = storage_out
    
    def work(self):
        """Work"""
        print("Working")
        if self._barrack_in.is_empty():
            return
        print("Worker working")
        worker = self._barrack_in.get_worker()
        worker.change_vitality(-10)
        self._storage_out.add_product(Product())
        if worker.get_vitality() > 0:
            self._barrack_out.add_worker(worker)


    
if __name__=='__main__':
    w1 = World()
    w1.Simulate()
