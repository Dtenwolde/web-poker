from enum import Enum

from flaskr import sio
from flaskr.lib.game import Evaluator
from flaskr.lib.game.Player import Player
from flaskr.lib.game.Card import CardSuits, Card, CardRanks
import random
from typing import Optional, List

from flaskr.lib.models.models import UserModel


SMALL_BLIND_CALL_VALUE = 200


class PokerException(Exception):
    def __init__(self, message=""):
        super().__init__(self.message)
        self.message = message


class Phases(Enum):
    NOT_YET_STARTED = 0
    PRE_FLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4
    POST_ROUND = 5

class HandRanking:
    ROYAL_FLUSH = 10
    STRAIGHT_FLUSH = 9
    FOUR_KIND = 8
    FULL_HOUSE = 7
    FLUSH = 6
    STRAIGHT = 5
    THREE_KIND = 4
    TWO_PAIR = 3
    ONE_PAIR = 2
    HIGH_CARD = 1


class PokerTable:
    """
    Stores information about the poker game being played
    """

    def __init__(self, room_id):
        self.room_id = room_id
        self.player_list: List[Player] = []

        self.fold_list: List[Player] = []
        self.caller_list: List[Player] = []
        self.deck = None
        self.small_blind_index = 0
        self.phase: Phases = Phases.PRE_FLOP

        self.community_cards: List[Card] = []

        self.first = True
        self.pot = {}
        self.current_call_value = SMALL_BLIND_CALL_VALUE
        self.active_player_index = 0

        self.all_in = False

    def initialize_round(self):
        """
        Initializes the Poker game, resets the pot to 0

        :return: An error string, or None if no error occured.
        """
        if len(self.player_list) < 2:
            raise PokerException("Need at least two players to start the game.")

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
        self.current_call_value = SMALL_BLIND_CALL_VALUE

        self.first = True

        self.fold_list = []
        self.caller_list = []

        self.active_player_index = self.small_blind_index

        self.phase_start()

        self.broadcast("New round starting.")

    def broadcast(self, message):
        sio.emit("message", message, room=self.room_id)

    def post_round(self):
        self.small_blind_index = (self.small_blind_index + 1) % len(self.player_list)
        
        hand_scores = {}
        for player in self.caller_list:

            hand_scores[player] = self.evaluate_hand(player.hand)
            print(hand_scores[player])
        highest_score = None
        tie_players = {}
        for player, hand_rank in hand_scores.items():
            if highest_score is None:
                highest_score = hand_rank
                tie_players[player] = hand_rank
            elif hand_rank > highest_score:
                highest_score = hand_rank
                tie_players = {player: hand_rank}
            elif hand_rank == highest_score:
                tie_players[player] = hand_rank
        self.handle_tie_breaker(tie_players)
        # TODO: Go to tiebreaker depending on rank
        for player in self.player_list:
            player.finish()

    def get_player(self, user: UserModel):
        for player in self.player_list:
            if player.user.id == user.id:
                return player
        return None

    def phase_start(self):
        self.broadcast("Starting phase " + self.phase.name.capitalize().replace("_", " "))

        if self.phase == Phases.PRE_FLOP:
            self.first = True
        elif self.phase == Phases.FLOP:
            # Flop deals 3 cards
            self.community_cards.append(self.take_card())
            self.community_cards.append(self.take_card())
            self.community_cards.append(self.take_card())
        elif self.phase == Phases.TURN:
            self.community_cards.append(self.take_card())
        elif self.phase == Phases.RIVER:
            self.community_cards.append(self.take_card())
            # print(f"{self.caller_list=}")
        elif self.phase == Phases.POST_ROUND:
            # print(f"{self.caller_list=}")
            self.post_round()

    def round(self, action: str, value: int = 0):
        message = None
        player = self.get_current_player()
        if self.first:
            if self.get_small_blind() != player:
                raise ValueError("The small blind was not the first player to do an action.")

            self.first = False
            chips = player.pay(self.current_call_value)  # Current small blind
            if chips is not None:
                self.broadcast("%s started the round with %d." % (player.user.username, self.current_call_value))
                self.add_pot(chips)
                self.current_call_value = SMALL_BLIND_CALL_VALUE * 2  # In cents
            else:
                raise ValueError("Programmer error: please check the player balances before starting the next round.")

        elif action == "call":
            orig_value = player.current_call_value

            chips = player.pay(self.current_call_value)
            if chips is not None:
                self.action_call(chips, player, self.current_call_value - orig_value)
            else:
                self.action_fold(player)
                message = "Folded, not enough currency to match the call value."

        elif action == "raise":
            if self.all_in:
                return "Cannot raise when all-in already happened."

            if value < 100:
                return "Minimum raise is 1 euro."

            chips = player.pay(value)
            if chips is not None:
                self.action_raise(chips, player, value)
            else:
                return "Cannot raise by %d." % value

        elif action == "fold":
            self.action_fold(player)
            message = "Folded."

        self.increment_player()

        self.check_phase_finish()
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
        self.pot = {k: self.pot.get(k, 0) + chips.get(k, 0) for k in set(chips) | set(self.pot)}

    def check_phase_finish(self):
        if len(self.player_list) != len(self.fold_list) + len(self.caller_list):
            return False

        self.phase = Phases(self.phase.value + 1)

        self.caller_list = []

        # Start new phase
        self.phase_start()

    def export_state(self, player: Player):
        hand = player.hand if player is not None else []

        return {
            "small_blind": self.get_small_blind().user.username,
            "current_call_value": self.current_call_value,
            "pot": self.pot,
            "phase": self.phase.name.capitalize(),
            "active_player_index": self.active_player_index,
            "active_player": self.get_current_player().user.username,
            "community_cards": [card.to_json() for card in self.community_cards],
            "fold_list": [player.user.username for player in self.fold_list],
            "caller_list": [player.user.username for player in self.caller_list],
            "hand": [card.to_json() for card in hand],
            "chips": player.chips,
            "chip_sum": player.sum_chips(),
            "to_call": self.current_call_value - player.current_call_value
        }

    def evaluate_hand(self, hand: List[Card]):
        print(hand, self.community_cards)
        if Evaluator.royal_flush(hand, self.community_cards):
            return HandRanking.ROYAL_FLUSH
        if Evaluator.straight_flush(hand, self.community_cards):
            return HandRanking.STRAIGHT_FLUSH
        if Evaluator.full_house(hand, self.community_cards):
            return HandRanking.FULL_HOUSE
        if Evaluator.flush(hand, self.community_cards):
            return HandRanking.FLUSH
        if Evaluator.straight(hand, self.community_cards):
            return HandRanking.STRAIGHT
        if Evaluator.three_kind(hand, self.community_cards):
            return HandRanking.THREE_KIND
        if Evaluator.two_pair(hand, self.community_cards):
            return HandRanking.TWO_PAIR
        if Evaluator.one_pair(hand, self.community_cards):
            return HandRanking.ONE_PAIR
        if Evaluator.highest_card(hand, self.community_cards):
            return HandRanking.HIGH_CARD

    def handle_tie_breaker(self, tie_players):
        pass

    def action_raise(self, chips, player, value):
        if player.sum_chips() == 0:
            self.all_in = True

        self.add_pot(chips)
        self.current_call_value += value
        self.caller_list = [player]
        self.broadcast("%s raised by %d." % (player.user.username, value))

    def action_fold(self, player: Player):
        self.fold_list.append(player)
        if len(self.fold_list) == len(self.player_list) - 1:
            last_player_set = set(self.player_list).difference(set(self.fold_list))
            winner = last_player_set.pop()
            winner.payout(self.pot)

            self.initialize_round()

    def action_call(self, chips, player, value):
        self.add_pot(chips)
        self.caller_list.append(player)
        self.broadcast("%s called %d." % (player.user.username, value))
