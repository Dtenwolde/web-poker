from enum import Enum

from flaskr.lib.game.Player import Player
from flaskr.lib.game.Card import CardSuits, Card, CardRanks
import random
from typing import Optional, List

from flaskr.lib.models.models import UserModel


class Phases(Enum):
    NOT_YET_STARTED = 0
    PRE_FLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4
    POST_ROUND = 5


class PokerTable:
    """
    Stores information about the poker game being played
    """

    def __init__(self):
        self.player_list: List[Player] = []

        self.fold_list: List[Player] = []
        self.caller_list: List[Player] = []
        self.deck = None
        self.small_blind_index = 0
        self.phase: Phases = Phases.PRE_FLOP

        self.community_cards: List[Card] = []

        self.first = True
        self.pot = {}
        self.current_call_value = 0
        self.active_player_index = 0

    def initialize_round(self):
        # TODO: add pay
        self.deck = self.deck_generator()
        self.deal_cards()

        self.phase = Phases.PRE_FLOP
        self.pot = {
            "black": 0,
            "green": 0,
            "blue": 0,
            "red": 0,
            "pink": 0,
            "white": 0
        }
        self.current_call_value = 0

        self.first = True

        self.fold_list = []
        self.caller_list = []

        self.active_player_index = self.small_blind_index

        self.phase_start()

    def post_round(self):
        self.small_blind_index = (self.small_blind_index + 1) % len(self.player_list)

        for player in self.player_list:
            player.finish()

    def get_player(self, user: UserModel):
        for player in self.player_list:
            if player.user.id == user.id:
                return player
        return None

    def phase_start(self):
        if self.phase == Phases.PRE_FLOP:
            print("got here")
            small_blind = self.get_small_blind()
            big_blind = self.get_big_blind()
        elif self.phase == Phases.FLOP:
            # Flop deals 3 cards
            self.community_cards.append(self.take_card())
            self.community_cards.append(self.take_card())
            self.community_cards.append(self.take_card())
        elif self.phase == Phases.TURN:
            self.community_cards.append(self.take_card())
        elif self.phase == Phases.RIVER:
            self.community_cards.append(self.take_card())
        elif self.phase == Phases.POST_ROUND:
            self.post_round()

    def fold(self, player: Player):
        self.fold_list.append(player)
        print(self.fold_list, self.player_list)
        if len(self.fold_list) == len(self.player_list) - 1:
            print("Only one player remains")

    def round(self, action: str, value: int = 0):
        message = None
        player = self.get_current_player()
        print(action, self.first)
        if self.first and self.get_small_blind() == player:
            print("Got to small blind")
            # TODO Fix this
            self.first = False
            chips = player.pay(value)
            if chips is not None:
                self.add_pot(chips)
                self.current_call_value = 2
                message = "Started round successfully."
            else:
                raise ValueError("Programmer error: please check the player balances before starting the next round.")

        elif action == "call":
            chips = player.pay(self.current_call_value)
            if chips is not None:
                self.add_pot(chips)
                self.caller_list.append(player)
                message = "Successfully called."
            else:
                self.fold(player)
                message = "Folded, not enough currency to match the call value."

        elif action == "raise":
            chips = player.pay(value)
            if chips is not None:
                self.add_pot(chips)
                self.current_call_value = value
                self.caller_list = [player]
                message = "Raised successfully."
            else:
                return "Cannot raise by %d." % value

        elif action == "fold":
            self.fold(player)
            message = "Folded."

        self.increment_player()
        return message

    def increment_player(self):
        """
        If this freezes, you did something wrong elsewhere.
        This assumes the fold_list is not the same as all the joined players.
        """
        self.active_player_index = (self.active_player_index + 1) % len(self.player_list)
        if self.get_current_player() in self.fold_list:
            self.increment_player()

    def get_current_player(self):
        return self.player_list[self.active_player_index]

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
        if len(self.deck):
            return self.deck.pop()
        else:
            return None

    def add_player(self, user: UserModel, socket_id):
        for player in self.player_list:
            if player.user.id == user.id:
                # If the user is already in the list, overwrite the socket id to the newest one.
                player.socket = socket_id
                return

        self.player_list.append(Player(user, socket_id))

    def export_players(self):
        return [{
            "username": player.user.username,
            "balance": player.user.balance
        } for player in self.player_list]

    def get_small_blind(self):
        return self.player_list[self.small_blind_index]

    def get_big_blind(self):
        return self.player_list[(self.small_blind_index + 1) % len(self.player_list)]

    def add_pot(self, chips):
        self.pot = {k: self.pot.get(k, 0) + chips.get(k, 0) for k in set(chips)}

    def check_phase_finish(self):
        if len(self.player_list) != len(self.fold_list) + len(self.caller_list):
            return False

        # TODO: Dani mag rekenen
        self.small_blind_index = (self.small_blind_index + 1)

        self.phase = Phases(self.phase.value + 1)

        # Start new phase
        self.phase_start()

    def export_state(self, user: UserModel):
        player = self.get_player(user)
        hand = player.hand if player is not None else []

        return {
            "small_blind": self.get_small_blind().user.username,
            "current_call_value": self.current_call_value,
            "pot": self.pot,
            "phase": self.phase.name.capitalize(),
            "active_player_index": self.active_player_index,
            "community_cards": [card.to_json() for card in self.community_cards],
            "fold_list": [player.user.username for player in self.fold_list],
            "caller_list": [player.user.username for player in self.caller_list],
            "hand": [card.to_json() for card in hand]
        }
