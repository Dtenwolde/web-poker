from flaskr.lib.game.Player import Player
from flaskr.lib.game.Card import CardSuits, Card, CardRanks
import random
from typing import Optional, List

from flaskr.lib.models.models import UserModel


class PokerTable:
    """
    Stores information about the poker game being played
    """

    def __init__(self):
        self.player_list: List[Player] = []
        self.deck = self.deck_generator()

    def deck_generator(self):
        deck = []

        for suit in [suit for suit in dir(CardSuits) if not suit.startswith("__")]:
            for rank in [rank for rank in dir(CardRanks) if not rank.startswith("__")]:
                deck.append(Card(CardRanks[rank], CardSuits[suit]))

        # TODO: Use a non-crackable shuffle function instead
        random.shuffle(deck)
        return deck

    def deal_cards(self):
        # First round
        for player in self.player_list:
            player.deal(self.take_card())

        for player in self.player_list:
            player.deal(self.take_card())

    def take_card(self) -> Optional[Card]:
        if not len(self.deck):
            return self.deck.pop()
        else:
            return None

    def add_player(self, user: UserModel):
        if user not in self.player_list:
            self.player_list.append(Player(user))

    def export_players(self):
        return [{
            "name": player.user.username,
            "balance": player.user.balance
        } for player in self.player_list]
