class World:
    def __init__(self):
        self.barracks = []
        self.storages = []
        self.barns = []
        self.dining_halls = []
        self.homes = []
        self.fields = []
    
    
class Field:
    def __init__(self, barrack_in, barrack_out, barn_out):
        self._barrack_in = barrack_in
        self._barrack_out = barrack_out
        self._barn_out = barn_out

    def farm(self):
        """Farming"""


class DiningHall:
    def __init__(self, barrack_in, barrack_out, barn_in):
        self._barrack_in = barrack_in
        self._barrack_out = barrack_out
        self._barn_in = barn_in
        
    def eat(self):
        """Eating"""


class Home:
    def __init__(self, barrack_in, barrack_out, storage_in):
        self._barrack_in = barrack_in
        self._barrack_out = barrack_out
        self._storage_in = storage_in
    
    def rest(self):
        """Rest"""


class Factory:
    def __init__(self, barrack_in, barrack_out, storage_out):
        self._barrack_in = barrack_in
        self._barrack_out = barrack_out
        self._storage_out = storage_out
    
    def work(self):
        """Work"""


class Barn:
    def __init__(self):
        self.food = []
    
    def get_food(self):
        """Returns food"""
        
    def add_food(self, food):
        """Send food to barn"""
        
    def is_empty(self):
        """Returns true if barn is empty"""


class Barrack:
    def __init__(self):
        self.workers = []
    
    def get_worker(self):
        """Returns a worker"""
    
    def add_worker(self, worker):
        """Send a worker to the barrack"""
    
    def is_empty(self):
        """Returns true if barrack is empty"""
        
        
class Storage():
    def __init__(self):
        self.products = []
    
    def get_product():
        """Returns a product"""
    
    def add_product(product):
        """Send a product to storage"""
        
    
class Worker:
    def __init__(self):
        self.vitality = 100
    
    def get_vitality(self):
        """Returns the worker's vitality"""
        
    def change_vitality(self, change):
        """Changes vitality by an amount"""


class Food:
    def __init__ (self, quality):
        self.quality = quality

    def get_quality(self):
        """Returns quality of the food"""


class Product:
    """Product"""