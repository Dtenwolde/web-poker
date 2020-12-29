from collections import defaultdict

from flaskr import sio
from flaskr.lib.game.Exceptions import PokerException
from flaskr.lib.game.chip_utils import get_value
from flaskr.lib.models.models import UserModel


class Player:
    """
        Stores information about a player participating in a poker game.
    """

    def __init__(self, user: UserModel, socket):
        self.user = user
        self.socket = socket

        self.hand = []
        self.balance = user.balance
        self.all_in = False

        self.current_call_value = 0

    def deal(self, cards):
        self.hand.append(cards)

    def reset(self):
        self.hand = []
        self.current_call_value = 0

    def pay(self, current_call_value):
        """
        :param current_call_value:
        :return:
        """
        to_pay = current_call_value - self.current_call_value

        if self.balance < to_pay:  # all in
            paid = self.balance
            self.balance = 0
            self.all_in = True
        else:  # not all in
            paid = to_pay
            self.balance -= to_pay
        self.current_call_value = current_call_value
        return paid


    def payout(self, pot):
        self.balance += pot

    def export_hand(self):
        if len(self.hand) == 0:
            return None
        return [card.to_json() for card in self.hand]

    def leave(self):
        # TODO
        """
        Call this function if the player leaves the table.
        This will return the chips back to the user.

        :return:
        """

        pass
        # self.user.set_chips(self.chips)
        # self.chips = None
