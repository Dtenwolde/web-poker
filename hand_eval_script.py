from flaskr.lib.game.Card import Card, CardRanks, CardSuits
from flaskr.lib.game.PokerTable import PokerTable, HandRanking

def get_suits(cards):
    suits_count = {"HEARTS": [],
                   "DIAMONDS": [],
                   "SPADES": [],
                   "CLUBS": []}

    for card in cards:
        suits_count[card.suit.name].append(card.rank.value)
    return suits_count


def royal_flush(hand, community_cards):
    suits_count = get_suits(hand + community_cards)
    for cards in suits_count.values():
        if len(cards) >= 5:  # Amount of same suit needed for royal flush to be possible
            royal_flush_count = 0
            for card in cards:
                if card >= 10:
                    royal_flush_count += 1
            if royal_flush_count == 5:
                print("ROYAL FLUSH WOOOOOOOO", cards)
                return True

    return False

def straight_flush(hand, community_cards):
    suits_count = get_suits(hand + community_cards)
    for suit in suits_count.values():
        if len(suit) >= 5:
            index = -1 # To get highest possible straight flush go from highest to lowest cards
            in_row = []
            suit_sorted = sorted(suit)
            while len(in_row) < 5:
                try:
                    if suit_sorted[index] - 1 == suit_sorted[index - 1]:
                        in_row.append(suit_sorted[index])
                    else:
                        in_row = []
                    index -= 1
                except IndexError:
                    return False
            return True
    return False

def four_kind(hand, community_cards):
    pass



poker_table = PokerTable()
deck = poker_table.deck_generator()
hand = [Card(CardRanks.NINE, CardSuits.HEARTS), Card(CardRanks.EIGHT, CardSuits.HEARTS)]
royal_flush_cards = [Card(CardRanks.SEVEN, CardSuits.HEARTS),
                     Card(CardRanks.JACK, CardSuits.HEARTS),
                     Card(CardRanks.QUEEN, CardSuits.HEARTS),
                     Card(CardRanks.KING, CardSuits.HEARTS),
                     Card(CardRanks.ACE, CardSuits.HEARTS)
                    ]
# community_cards = [deck.pop() for _ in range(5)]
print(royal_flush(hand, royal_flush_cards))
print(straight_flush(hand, royal_flush_cards))