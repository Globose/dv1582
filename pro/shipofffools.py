from random import randrange


class Die:
    def __init__(self):
        self._value = 1
        self.roll()

    def __str__(self):
        return str(self._value)

    def __add__(self, other):
        return self._value + other.get_value()

    def get_value(self):
        return self._value

    def roll(self):
        self._value = randrange(1, 7)


class DiceCup:
    def __init__(self, die_count=5):
        self._dice = []
        self._locked = []

        for i in range(die_count):
            self._dice.append(Die())
            self._locked.append(False)

    def roll(self):
        for i, d in enumerate(self._dice):
            if not self._locked[i]:
                d.roll()

    def die_value(self, index):
        return self._dice[index].get_value()

    def bank(self, index):
        self._locked[index] = True

    def is_banked(self, index):
        return self._locked[index]

    def release(self, index):
        self._locked[index] = False

    def release_all(self):
        self._locked = []
        for i in range(len(self._dice)):
            self._locked.append(False)

    def lock_value(self, value):
        for i, die in enumerate(self._dice):
            if die.get_value() == value:
                self._locked[i] = True
                return True

    def get_sum(self):
        sum = 0
        for die in self._dice:
            sum += die.get_value()
        return sum


class Player:
    def __init__(self, name):
        self._score = 0
        self.name = name

    def current_score(self):
        return self._score

    def get_name(self):
        return self.name

    def reset_score(self):
        self.score = 0

    def play_turn(self, game):
        self._score += game.turn()


class ShipOfFoolsGame:
    def __init__(self):
        self.winning_score = 50
        self._cup = DiceCup(5)

    def turn(self):
        self._cup.release_all()
        has_ship = False
        has_captain = False
        has_mate = False

        crew = 0
        for _ in range(3):
            self._cup.roll()

            if not has_ship and self._cup.lock_value(6):
                has_ship = True

            if has_ship and not has_captain and self._cup.lock_value(5):
                has_captain = True

            if has_captain and not has_mate and self._cup.lock_value(4):
                has_mate = True

            if has_ship and has_captain and has_mate:
                for i in range(5):
                    if self._cup.die_value(i) > 3:
                        self._cup.bank(i)

        if has_ship and has_captain and has_mate:
            crew = self._cup.get_sum() - 15

        return crew


class PlayRoom:
    def __init__(self):
        self._game = None
        self._players = []
        self._winners = None

    def set_game(self, game):
        self._game = game

    def add_player(self, player):
        self._players.append(player)

    def reset_scores(self):
        for player in self._players:
            player.reset_score()
            self._winners = None

    def play_round(self):
        for player in self._players:
            print(player.get_name(), " turn")
            player.play_turn(self._game)

    def print_scores(self):
        print("")
        for player in self._players:
            print("{}: {}".format(player.get_name(), player.current_score()))

    def game_finished(self):
        winners = []
        for player in self._players:
            if player.current_score() >= self._game.winning_score:
                winners.append(player)
        if len(winners) == 1:
            self._winners = winners
            return True
        elif len(winners) > 1:
            winner = winners[0]
            for player in winners:
                if player.current_score() >= winner.current_score():
                    winner = player
            self._winners = []
            for player in self._players:
                if player.current_score() == winner.current_score():
                    self._winners.append(player)
            return True
        return False

    def print_winner(self):
        if len(self._winners) > 1:
            print("Winners:")
            for player in self._winners:
                print(player.get_name())
        else:
            print("{}: {}".format("Winner", self._winners[0].get_name()))

if __name__ == "__main__":
    room = PlayRoom()
    room.set_game(ShipOfFoolsGame())
    room.add_player(Player("Nora"))
    room.add_player(Player("Selman"))
    room.reset_scores()
    room.print_scores()
    while not room.game_finished():
        room.play_round()
        room.print_scores()

    room.print_scores()
    room.print_winner()

