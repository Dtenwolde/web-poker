from flaskr.lib.game.Card import Card, CardRanks, CardSuits
from flaskr.lib.game.PokerTable import PokerTable, HandRanking


# def get_ranks(cards):
#     rank_dict = {}
#     for card in cards:
#         if card.rank in rank_dict:
#             rank_dict[card.rank].append(card)
#         else:
#             rank_dict[card.rank] = [card]
#     return rank_dict
#
#
# def get_suits(cards):
#     suits_count = {"HEARTS": [],
#                    "DIAMONDS": [],
#                    "SPADES": [],
#                    "CLUBS": []}
#
#     for card in cards:
#         suits_count[card.suit.name].append(card.rank.value)
#     return suits_count
#
#
# def royal_flush(hand, community_cards):
#     suits_count = get_suits(hand + community_cards)
#     for cards in suits_count.values():
#         if len(cards) >= 5:  # Amount of same suit needed for royal flush to be possible
#             royal_flush_count = 0
#             for card in cards:
#                 if card >= 10:
#                     royal_flush_count += 1
#             if royal_flush_count == 5:
#                 return True
#
#     return False
#
#
# def straight_flush(hand, community_cards):
#     suits_count = get_suits(hand + community_cards)
#     for suit in suits_count.values():
#         if len(suit) >= 5:
#             index = -1  # To get highest possible straight flush go from highest to lowest cards
#             in_row = []
#             suit_sorted = sorted(suit)
#             while len(in_row) < 5:
#                 try:
#                     if suit_sorted[index] - 1 == suit_sorted[index - 1]:
#                         in_row.append(suit_sorted[index])
#                     else:
#                         in_row = []
#                     index -= 1
#                 except IndexError:
#                     return False
#             return True, in_row
#     return False
#
#
# def four_kind(hand, community_cards):
#     rank_dict = get_ranks(hand + community_cards)
#     for rank, cards in rank_dict.items():
#         if len(cards) == 4:
#             return True, cards
#     return False
#
#
# def full_house(card, community_cards):
#     rank_dict = get_ranks(card + community_cards)
#     if three_kind(card, community_cards) and one_pair(card, community_cards):
#         print("Full house")
#     full_house_cards = []
#     for rank, cards in rank_dict.items():
#         if len(cards) == 3:
#             full_house_cards += cards
#             highest_rank = CardRanks.TWO  # Lowest possible
#             for rank_, cards_ in rank_dict.items():
#                 if len(cards_) >= 2 and rank_ != rank and rank_.value >= highest_rank.value:
#                     highest_rank = rank_
#             if highest_rank == CardRanks.TWO and len(rank_dict[highest_rank]) >= 2:
#                 full_house_cards += rank_dict[highest_rank]
#                 return True
#             elif highest_rank != CardRanks.TWO:
#                 full_house_cards += rank_dict[highest_rank]
#                 return True, full_house_cards
#     return False
#
#
# def flush(hand, community_cards):
#     suit_dict = get_suits(hand + community_cards)
#     for suit, cards in suit_dict.items():
#         if len(suit) >= 5:
#             return True, cards
#     return False
#
#
# def straight(hand, community_cards):
#     values = []
#     for card in hand + community_cards:
#         values.append(card.rank.value)
#     sorted_values = list(set(sorted(values)))  # Only keep unique ranks
#     index = -1
#     in_row = [sorted_values[index]]
#     while len(in_row) < 5:
#         try:
#             if sorted_values[index] - 1 == sorted_values[index - 1]:
#                 in_row.append(sorted_values[index - 1])
#             else:
#                 in_row = [sorted_values[index - 1]]
#             index -= 1
#         except IndexError:
#             return False
#     return True, in_row
#
#
# def three_kind(hand, community_cards):
#     rank_dict = get_ranks(hand + community_cards)
#     highest_rank = None
#     for rank, cards in rank_dict.items():
#         if len(cards) == 3:
#             if highest_rank is None:
#                 highest_rank = rank
#             elif rank.value > highest_rank.value:
#                 highest_rank = rank
#     if highest_rank is not None:
#         return True, highest_rank
#     return False
#
#
# def two_pair(hand, community_hands):
#     rank_dict = get_ranks(hand + community_hands)
#     highest_rank = second_highest_rank = None
#     for rank, cards in rank_dict.items():
#         if len(cards) == 2:
#             if highest_rank is None:
#                 highest_rank = rank
#             elif second_highest_rank is None:
#                 if rank.value > highest_rank.value:
#                     second_highest_rank = highest_rank
#                     highest_rank = rank
#                 else:
#                     second_highest_rank = rank
#             elif rank.value > highest_rank.value:
#                 second_highest_rank = highest_rank
#                 highest_rank = rank
#             elif rank.value > second_highest_rank.value:
#                 second_highest_rank = rank
#     if second_highest_rank is None:
#         return False
#     else:
#         return True, highest_rank, second_highest_rank
#
#
# def one_pair(hand, community_hands):
#     rank_dict = get_ranks(hand + community_hands)
#     highest_rank = None
#     for rank, cards in rank_dict.items():
#         if len(cards) == 2:
#             if highest_rank is None:
#                 highest_rank = rank
#             elif rank.value > highest_rank.value:
#                 highest_rank = rank
#     if highest_rank is None:
#         return False
#
#     return True, highest_rank
#
# def highest_card(hand, community_hands):
#     rank_dict = get_ranks(hand + community_hands)
#     highest_rank = None
#     for rank, cards in rank_dict.items():
#         if highest_rank is None:
#             highest_rank = rank
#         elif rank.value > highest_rank.value:
#             highest_rank = rank
#
#     return True, highest_rank
        

poker_table = PokerTable()
deck = poker_table.deck_generator()
hand = [deck.pop() for _ in range(2)]
community_hands = [deck.pop() for _ in range(5)]
# hand = [Card(CardRanks.ACE, CardSuits.DIAMONDS), Card(CardRanks.KING, CardSuits.DIAMONDS)]
# community_hands = [Card(CardRanks.TEN, CardSuits.DIAMONDS), Card(CardRanks.QUEEN, CardSuits.DIAMONDS),
#                    Card(CardRanks.JACK, CardSuits.DIAMONDS), Card(CardRanks.FIVE, CardSuits.SPADES),
#                    Card(CardRanks.FOUR, CardSuits.HEARTS)]

if royal_flush(hand, community_hands):
    print(HandRanking.ROYAL_FLUSH)
if straight_flush(hand, community_hands):
    print(HandRanking.STRAIGHT_FLUSH)
if full_house(hand, community_hands):
    print(HandRanking.FULL_HOUSE)
if flush(hand, community_hands):
    print(HandRanking.FLUSH)
if straight(hand, community_hands):
    print(HandRanking.STRAIGHT)
if three_kind(hand, community_hands):
    print(HandRanking.THREE_KIND)
if two_pair(hand, community_hands):
    print(HandRanking.TWO_PAIR)
if one_pair(hand, community_hands):
    print(HandRanking.ONE_PAIR)
if highest_card(hand, community_hands):
    print(HandRanking.HIGH_CARD)

# print("Royal flush: ", royal_flush(hand, community_hands))
# print("Straight flush: ", straight_flush(hand, community_hands))
# print("Full house: ", full_house(hand, community_hands))
# print("Flush: ", flush(hand, community_hands))
# print("Straight: ", straight(hand, community_hands))
# print("Three of a kind: ", three_kind(hand, community_hands))
# print("Two pair: ", two_pair(hand, community_hands))
# print("One pair: ", one_pair(hand, community_hands))
# print("Highest card: ", highest_card(hand, community_hands))

print(hand, community_hands)
