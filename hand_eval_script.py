from flaskr.lib.game.Card import Card, CardRanks, CardSuits
from flaskr.lib.game.PokerTable import PokerTable, HandRanking

def get_ranks(cards):
    rank_dict = {}
    for card in cards:
        if card.rank in rank_dict:
            rank_dict[card.rank].append(card)
        else:
            rank_dict[card.rank] = [card]
    return rank_dict


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
    rank_dict = get_ranks(hand + community_cards)
    # TODO: Add kicker card
    for rank, cards in rank_dict.items():
        print(rank, cards)
        if len(cards) == 4:
            print(rank, cards)
            return True
    return False

def full_house(card, community_cards):
    rank_dict = get_ranks(card + community_cards)
    full_house_cards = []
    for rank, cards in rank_dict.items():
        if len(cards) == 3:
            full_house_cards += cards
            highest_rank = CardRanks.TWO # Lowest possible
            for rank_, cards_ in rank_dict.items():
                if len(cards_) >= 2 and rank_ != rank and rank_.value >= highest_rank.value:
                    highest_rank = rank_
            if highest_rank == CardRanks.TWO and len(rank_dict[highest_rank]) >= 2:
                full_house_cards += rank_dict[highest_rank]
                return True
            elif highest_rank != CardRanks.TWO:
                full_house_cards += rank_dict[highest_rank]
                return True
    return False

def flush(hand, community_cards):
    suit_dict = get_suits(hand + community_cards)
    for suit in suit_dict:
        if len(suit) >= 5:
            return True
    return False


poker_table = PokerTable()
deck = poker_table.deck_generator()
hand = [Card(CardRanks.THREE, CardSuits.HEARTS), Card(CardRanks.TWO, CardSuits.HEARTS)]
community_hands = [Card(CardRanks.TEN, CardSuits.HEARTS),
                   Card(CardRanks.EIGHT, CardSuits.HEARTS),
                   Card(CardRanks.SIX, CardSuits.SPADES),
                   Card(CardRanks.ACE, CardSuits.SPADES),
                   Card(CardRanks.KING, CardSuits.SPADES)]
# community_cards = [deck.pop() for _ in range(5)]
# print(royal_flush(hand, royal_flush_cards))
# print(straight_flush(hand, royal_flush_cards))
# print(full_house(hand, community_hands))
print(flush(hand, community_hands))