from flaskr.lib.game import Evaluator
from flaskr.lib.game.Card import Card, CardRanks, CardSuits
from flaskr.lib.game.PokerTable import PokerTable, HandRanking

poker_table = PokerTable("3")
deck = poker_table.deck_generator()

community_hands = [Card(CardRanks.ACE, CardSuits.DIAMONDS), Card(CardRanks.QUEEN, CardSuits.HEARTS),
                   Card(CardRanks.KING, CardSuits.DIAMONDS),  Card(CardRanks.QUEEN, CardSuits.SPADES),
                   Card(CardRanks.KING, CardSuits.CLUBS)]

# hand1 = [Card(CardRanks.ACE, CardSuits.DIAMONDS), Card(CardRanks.QUEEN, CardSuits.DIAMONDS)]
hand2 = [Card(CardRanks.TWO, CardSuits.HEARTS), Card(CardRanks.THREE, CardSuits.DIAMONDS)]

hands = [hand2]

poker_table.community_cards = community_hands
print(poker_table.evaluate_hand(hand2))
exit(1)

def get_highest_card(hands, community_cards):
    sorted_hands = []
    for hand in hands:
        hand_ = []
        for card in hand + community_cards:
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
            return new_list
    return new_list


def get_highest_pair(hands, community_cards):
    pass


def handle_tie_breaker(hands, community_cards, rank):
    winner = None
    if rank == HandRanking.HIGH_CARD:
        winner = get_highest_card(hands, community_cards)
    elif rank == HandRanking.ONE_PAIR:
        winner = get_highest_pair(hands, community_cards)

    if len(winner) == 1:
        print(f"Winner is {winner[0]}")
    else:
        print(f"Pot is split between {winner}")

