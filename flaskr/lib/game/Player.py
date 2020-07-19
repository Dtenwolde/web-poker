from collections import defaultdict

from flaskr import sio
from flaskr.lib.game.Bank import get_value
from flaskr.lib.models.models import UserModel


class Player:
    """
        Stores information about a player participating in a poker game.
    """

    def __init__(self, user: UserModel, socket):
        self.user = user
        self.socket = socket

        self.hand = []
        self.chips = {
            "black": 0,
            "green": 44,
            "blue": 44,
            "red": 44,
            "pink": 44,
            "white": 44
        }

        self.current_call_value = 0

    def deal(self, cards):
        self.hand.append(cards)

    def finish(self):
        self.hand = []
        self.current_call_value = 0

    def pay(self, current_call_value):
        """
        Pay the current_call_value amount in chips, using a greedy algorithm.
        Meaning, we look for the greatest amount to fit, and downsize until no chips are left.
        :param current_call_value:
        :return:
        """
        to_pay = current_call_value - self.current_call_value

        keys = list(self.chips.keys())
        chips = defaultdict(int)
        chip_idx = 0
        while to_pay > 0:
            key = keys[chip_idx]
            value = get_value(key)
            while value <= to_pay and self.chips[key] > 0:
                to_pay -= value
                chips[key] += 1
                self.chips[key] -= 1

            chip_idx += 1
            if chip_idx == len(self.chips.keys()) and to_pay != 0:
                # If no chip could be broken up to still pay the call value.
                if not self.check_break_chips():
                    return None
                chip_idx -= 1

        self.current_call_value = current_call_value
        return chips

    def check_break_chips(self):
        """
        Checks if any chips can be broken up into whites using
        :return: true if it broke up a chip, false otherwise
        """
        for key in self.chips.keys():
            if self.chips[key] > 0:
                value = get_value(key)
                n_whites = value // get_value("white")

                self.chips["white"] += n_whites
                self.chips[key] -= 1
                return True
        return False

    def sum_chips(self):
        return sum(get_value(key) * amount for key, amount in self.chips.items())

    def payout(self, pot):
        self.chips = {k: pot.get(k, 0) + self.chips.get(k, 0) for k in set(self.chips) | set(pot)}


