from flaskr.lib.game.Player import Player
from flaskr.lib.game.Card import CardSuits, Card, CardRanks
import random
from typing import Optional

class PokerTable:
    """
    Stores information about the poker game being played
    """
    def __init__(self):
        self.player_list: list[Player] = []
        self.deck = self.deck_generator()
        print(self.deck)
    
    def deck_generator(self):
        deck = []
        
        for suit in [suit for suit in dir(CardSuits) if not suit.startswith("__")]:
            for rank in [rank for rank in dir(CardRanks) if not rank.startswith("__")]:
                deck.append(Card(CardRanks[rank], CardSuits[suit]))

        # TODO: Use a non-crackable shuffle function instead
        random.shuffle(deck)
        return deck

    def take_card(self) -> Optional[Card]:
        if not len(self.deck):
            return self.deck.pop()
        else: 
            return None

    def add_player(self, username):
        self.player_list.append(Player(username))
