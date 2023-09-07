from random import randrange

class Die:
    def __init__(self):
        self._value = 1
        self.roll()
    
    def __str__(self):
        return str(self._value)
    
    def  __add__(self,other):
        return self._value + other.get_value()
    
    def get_value(self):
        return self._value
    
    def roll(self):
        self._value = randrange(1,7)


class DiceCup:
    def __init__(self, die_count=1):
        self._dice = [Die for i in range(die_count)]
        self.locked = [True for i in range(die_count)]


    def roll(self):
        for i, d in enumerate(self._dice):
            if not self.locked[i]:
                d.roll()
        
    def die_value(self, index):
        return self._dice[index-1].get_value()


    def bank(self, index):
        self.locked[index-1] = True

    
    def is_banked(self, index):
        return self.locked[index-1]


    def release(self, index):
        self.locked[index-1] = False
    
    
    def release_all(self):
        for l in self.locked:
            l = True


die1 = Die()
die2 = Die()
print(f"{die1.get_value()} {die2.get_value()} ")
print(f"Värdet är: {str(die1+die2)}")
    