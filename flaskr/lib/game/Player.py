


class Player:
    """
        Stores information about a player participating in a poker game.
    """
    def __init__(self, username):
        self.username = username

        self.hand = []
        self.chips = {
            "black": 0,
            "green": 1
            "blue": 1
            "red": 0
            "pink": 1
            "white": 1
        }

    def deal(self, cards):
        self.hand = cards