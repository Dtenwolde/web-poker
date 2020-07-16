from flaskr.lib.game import Evaluator
from flaskr.lib.game.Card import Card, CardRanks, CardSuits
from flaskr.lib.game.PokerTable import PokerTable, HandRanking

poker_table = PokerTable("3")
deck = poker_table.deck_generator()
# hand = [deck.pop() for _ in range(2)]
# community_hands = [deck.pop() for _ in range(5)]
community_hands = [Card(CardRanks.TWO, CardSuits.DIAMONDS), Card(CardRanks.THREE, CardSuits.SPADES),
                   Card(CardRanks.FIVE, CardSuits.HEARTS), Card(CardRanks.SIX, CardSuits.DIAMONDS),
                   Card(CardRanks.KING, CardSuits.HEARTS)]

hand1 = [Card(CardRanks.ACE, CardSuits.DIAMONDS), Card(CardRanks.EIGHT, CardSuits.CLUBS)]
hand2 = [Card(CardRanks.ACE, CardSuits.HEARTS), Card(CardRanks.NINE, CardSuits.SPADES)]


def handle_tie_breaker(hands, rank):
    if rank == HandRanking.HIGH_CARD:
        sorted_hands = []
        for hand in hands:
            hand_ = []
            for card in hand:
                hand_.append(card.rank.value)
            sorted_hands.append(sorted(hand_, reverse=True))

        remaining_list = sorted_hands
        best = remaining_list[0]
        tied = True
        index = 0
        new_list = []
        while tied and index < 5:
            if index > 0:
                remaining_list = new_list
            new_list = []
            for hand in remaining_list[1:]:
                if hand[index] > best[index]:
                    best = hand
                    new_list.append(best)
                elif hand[index] == best[index]:
                    new_list.extend([best, hand])
                else:
                    new_list.append(best)
            index += 1
            if len(new_list) == 1:
                print(new_list[0])


handle_tie_breaker([hand1 + community_hands, hand2 + community_hands], HandRanking.HIGH_CARD)

if Evaluator.royal_flush(hand1, community_hands):
    print(HandRanking.ROYAL_FLUSH)
if Evaluator.straight_flush(hand1, community_hands):
    print(HandRanking.STRAIGHT_FLUSH)
if Evaluator.full_house(hand1, community_hands):
    print(HandRanking.FULL_HOUSE)
if Evaluator.flush(hand1, community_hands):
    print(HandRanking.FLUSH)
if Evaluator.straight(hand1, community_hands):
    print(HandRanking.STRAIGHT)
if Evaluator.three_kind(hand1, community_hands):
    print(HandRanking.THREE_KIND)
if Evaluator.two_pair(hand1, community_hands):
    print(HandRanking.TWO_PAIR)
if Evaluator.one_pair(hand1, community_hands):
    print(HandRanking.ONE_PAIR)
if Evaluator.highest_card(hand1, community_hands):
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
