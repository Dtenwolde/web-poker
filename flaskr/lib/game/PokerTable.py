from enum import Enum

from flaskr import sio
from flaskr.lib.game import Evaluator
from flaskr.lib.game.Exceptions import PokerException
from flaskr.lib.game.Player import Player
from flaskr.lib.game.chip_utils import get_value
from flaskr.lib.game.Card import CardSuits, Card, CardRanks
import random
from typing import Optional, List

from flaskr.lib.models.models import UserModel

SMALL_BLIND_CALL_VALUE = 200
MINIMUM_RAISE = 100


class Phases(Enum):
    NOT_YET_STARTED = 0
    PRE_FLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4
    POST_ROUND = 5


class HandRanking:
    ROYAL_FLUSH = 0
    STRAIGHT_FLUSH = 1
    FOUR_KIND = 2
    FULL_HOUSE = 3
    FLUSH = 4
    STRAIGHT = 5
    THREE_KIND = 6
    ONE_PAIR = 7
    HIGH_CARD = 8


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
        self.phase: Phases = Phases.NOT_YET_STARTED

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

        for player in self.player_list:
            player.reset()

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
        self.community_cards: List[Card] = []

        self.phase_start()

        self.broadcast("New round starting.")

    def broadcast(self, message):
        sio.emit("message", message, room=self.room_id)

    def post_round(self):
        self.small_blind_index = (self.small_blind_index + 1) % len(self.player_list)
        self.caller_list = [player for player in self.player_list if player not in self.fold_list]

        # The game actually finished after all phases
        if len(self.fold_list) != len(self.player_list) - 1:
            hand_scores = {}
            for player in self.caller_list:
                hand_scores[player] = self.evaluate_hand(player.hand)

            winning_players = [self.caller_list[0]]
            for player in self.caller_list[1:]:
                equal = True
                for (_, tier1), (_, tier2) in zip(hand_scores[player], hand_scores[winning_players[0]]):
                    if tier1 < tier2:
                        winning_players = [player]
                        equal = False
                        break
                    if tier1 > tier2:
                        equal = False
                        break

                if equal:
                    for (card1, _), (card2, _) in zip(hand_scores[player], hand_scores[winning_players[0]]):
                        if card1.rank.value > card2.rank.value:
                            winning_players = [player]
                            equal = False
                            break
                        if card1.rank.value < card2.rank.value:
                            equal = False
                            break
                    if equal:
                        winning_players.append(player)


        else:
            winning_players = [self.caller_list[0]]

        shared_pot = self.payout_pot(len(winning_players))

        self.broadcast("%s won." % ",".join([player.user.username for player in winning_players]))

        # Payout the game
        for player in winning_players:
            player.payout(shared_pot)

        for player in self.player_list:
            player.original_chips = player.chips.copy()

        self.phase = Phases.NOT_YET_STARTED

        self.update_players()

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
        elif self.phase == Phases.POST_ROUND:
            self.post_round()

    def round(self, user, action: str, value: int = 0):
        if self.phase == Phases.NOT_YET_STARTED or self.phase == Phases.POST_ROUND:
            return "The next round has not yet started."

        if self.get_current_player().user.id != user.id:
            return "It is not yet your turn."

        message = None
        player = self.get_current_player()
        if self.first:
            if self.get_small_blind() != player:
                raise ValueError("The small blind was not the first player to do an action.")

            self.first = False
            chips = player.pay(self.current_call_value)  # Current small blind
            if chips is not None:
                self.broadcast("%s started the round with %d." % (player.user.username, self.current_call_value / 100))
                self.add_pot(chips)
                self.current_call_value = SMALL_BLIND_CALL_VALUE * 2  # In cents
            else:
                raise ValueError("Programmer error: please check the player balances before starting the next round.")

        elif action == "call":
            orig_value = player.current_call_value

            chips = player.pay(self.current_call_value)
            if chips is not None:
                self.action_call(chips, player, self.current_call_value - orig_value)
            elif self.all_in:
                chips = player.pay(player.sum_chips())
                self.action_call(chips, player, player.sum_chips() - orig_value)
            else:
                self.action_fold(player)
                message = "Folded, not enough currency to match the call value."

        elif action == "raise":
            if self.all_in:
                return "Cannot raise when all-in already happened."

            if value < MINIMUM_RAISE:
                return "Minimum raise is 1 euro."

            chips = player.pay(self.current_call_value + value)
            if chips is not None:
                self.action_raise(chips, player, value)
            else:
                return "Cannot raise by %d." % value

        elif action == "fold":
            if not self.action_fold(player):
                return None

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
        return {
            "small_blind": self.get_small_blind().user.username,
            "current_call_value": self.current_call_value,
            "pot": self.pot,
            "pot_sum": sum(get_value(key) * amount for key, amount in self.pot.items()) / 100,
            "phase": self.phase.name.capitalize(),
            "active_player_index": self.active_player_index,
            "active_player": self.get_current_player().user.username,
            "community_cards": [card.to_json() for card in self.community_cards],
            "fold_list": [player.user.username for player in self.fold_list],
            "caller_list": [player.user.username for player in self.caller_list],
            "hand": player.export_hand(),
            "players": self.export_player_game_data(player),
            "chips": player.chips,
            "chip_sum": player.sum_chips(),
            "to_call": (self.current_call_value - player.current_call_value),
            "started": self.phase != Phases.NOT_YET_STARTED
        }

    def evaluate_hand(self, hand: List[Card]):
        # TODO: Four of a kind

        all_cards = hand + self.community_cards

        best_cards = []

        evaluators = [
            Evaluator.royal_flush,
            Evaluator.straight_flush,
            Evaluator.four_kind,
            Evaluator.full_house,
            Evaluator.flush,
            Evaluator.straight,
            Evaluator.three_kind,
            Evaluator.one_pair,
            Evaluator.highest_card
        ]

        highest_evaluator = 0
        while len(best_cards) < 5:
            for highest_evaluator in range(highest_evaluator, len(evaluators)):
                match, cards = evaluators[highest_evaluator](all_cards)
                if match:
                    # Remove all matches from all cards list
                    all_cards = [card for card in all_cards if card not in cards]

                    # Add evaluator rank to card
                    result = list(zip(cards, len(cards) * [highest_evaluator]))
                    best_cards.extend(result)
                    if len(best_cards) == 4:  # In case four of a kind with pair
                        highest_evaluator = 8
                    break

        return best_cards[0:5]

    def action_raise(self, chips, player, value):
        if player.sum_chips() == 0:
            self.all_in = True

        self.add_pot(chips)
        self.current_call_value += value
        self.caller_list = [player]
        self.broadcast("%s raised by %d." % (player.user.username, value / 100))

    def action_fold(self, player: Player):
        """
        Returns False if the fold made the game finish.

        :param player:
        :return:
        """
        self.fold_list.append(player)
        if len(self.fold_list) == len(self.player_list) - 1:
            self.phase = Phases.POST_ROUND
            self.phase_start()
            return False
        return True

    def action_call(self, chips, player, value):
        self.add_pot(chips)
        self.caller_list.append(player)
        self.broadcast("%s called %d." % (player.user.username, value / 100))

    def payout_pot(self, shares=1):
        pot = {}

        missed_value = 0

        for key in self.pot.keys():
            pot[key] = self.pot[key] // shares
            missed_value += (pot[key] * shares - self.pot[key]) * get_value(key)

        pot["white"] += (missed_value // get_value("white")) // shares

        return pot

    def update_players(self):
        for player in self.player_list:
            sio.emit("table_state", self.export_state(player), json=True, room=player.socket)

    def export_player_game_data(self, player):
        data = []

        for other in self.player_list:
            if other == player:
                continue

            if other in self.fold_list:
                state = "Folded"
            elif other in self.caller_list:
                state = "Called"
            else:
                state = "Waiting"

            if self.phase == Phases.NOT_YET_STARTED and state != "Folded":
                hand = other.export_hand()
            else:
                hand = None

            data.append({
                "active": self.get_current_player() == other,
                "name": other.user.username,
                "state": state,
                "balance": other.user.balance,
                "hand": hand
            })

        return data

    def cleanup(self):
        for player in self.player_list:
            player.leave()
