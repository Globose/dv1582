from threading import Thread, Event
from random import random

class Competitor(Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name     # Name of the competitor
        self._points = 0.0    # Competing as long as > 0.0
        self._penelty_time = 1.0
        self._timer = Event()
    @property
    def name(self):
        return self._name
    @property
    def points(self):
        return self._points
    @property
    def competing(self):
        ''' True if the competitor is still competing.'''
        return self._points > 0.0
    @competing.setter
    def competing(self, b):
        ''' Set as True to start competing and False to stop competing.'''
        if b and (self._points == 0.0):
            self._points = 100.0
        if not b:
            self._points = 0.0
            self._timer.set() # Quit waiting

    def turn(self):
        ''' Update points and time to rest'''
        score = 20.0*random() - 15.0
        # Update points
        self._points = max(0.0, self._points + score)
        self._penelty_time = 1.0 + 0.05 * score

    def rest(self):
        ''' Rests '''
        self._timer.wait(self._penelty_time)

    def run(self):
        self.competing = True
        print("{} has started".format(self.name))

        while (self.competing):
            self.turn()
            print("{} has {:.2f} points".format(self.name,self.points))
            if self.competing:
                self.rest()
            else:
                print("{} has quit".format(self.name))

def main1():
    competitors = [Competitor("Ingemar"),
        Competitor("Magdalena"),
        Competitor("Danijela")]

    for c in competitors:
            # All competitors' score are set to 100.
            c.competing = True
            print("{} has started".format(c.name))

    cont = True
    while cont:
        cont = False # Set to False
        for c in [c for c in competitors if c.competing]:
            # For each competitor c that still is competing
            c.turn()
            print("{} has {:.2f} points".format(c.name, c.points))
            if c.competing:
                c.rest()
                cont = True # Continue playing if at least one player remains.
            else:
                print("{} has quit".format(c.name))

    print("The competition has ended.")

def main2():
    """Main2"""
    competitors = [Competitor("Ingemar"), Competitor("Magdalena"),
        Competitor("Danijela")]
    for c in competitors:
        c.start()

    for c in competitors:
        c.join()


if __name__ == '__main__':
    main2()