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
            "black": 44,
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

    def pay(self, current_call_value):
        """
        Pay the current_call_value amount in chips, using a greedy algorithm.
        Meaning, we look for the greatest amount to fit, and downsize until no chips are left.
        :param current_call_value:
        :return:
        """
        paid = self.current_call_value

        chips = defaultdict(int)
        chip_idx = 0
        while paid < current_call_value:
            key = list(self.chips.keys())[chip_idx]
            value = get_value(key)

            while value < paid and self.chips[key] > 0:
                paid -= value
                chips[key] += 1
                self.chips[key] -= 1

            chip_idx += 1
            if chip_idx > len(self.chips.keys()):
                return None

        self.current_call_value = current_call_value
        return chips
