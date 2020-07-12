from enum import Enum

class CardRanks(Enum):
    ACE = 0
    KING = 1
    QUEEN = 2
    JACK = 3
    TEN = 10
    NINE = 9
    EIGHT = 8
    SEVEN = 7
    SIX = 6
    FIVE = 5
    FOUR = 4
    THREE = 3
    TWO = 2

class CardSuits(Enum):
    SPADES = 0
    HEARTS = 1
    CLUBS = 2
    DIAMONDS = 3


class CardColours(Enum):
    RED = 0
    BLACK = 1


class Card:
    def __init__(self, rank: CardRanks, suit: CardSuits):
        self.rank = rank
        self.suit = suit

    def colour(self):
        if self.suit == CardSuits.HEARTS or self.suit == CardSuits.DIAMONDS:
            return CardColours.RED
        return CardColours.BLACK

    def __repr__(self):
        return "%s of %s" % (self.rank.name.capitalize(), self.suit.name.capitalize())

    __str__ = __repr__