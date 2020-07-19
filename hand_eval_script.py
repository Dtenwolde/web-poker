from flaskr.lib.game import Evaluator
from flaskr.lib.game.Card import Card, CardRanks, CardSuits
from flaskr.lib.game.PokerTable import PokerTable, HandRanking

poker_table = PokerTable("3")
deck = poker_table.deck_generator()

community_hands = [Card(CardRanks.TWO, CardSuits.DIAMONDS), Card(CardRanks.THREE, CardSuits.SPADES),
                   Card(CardRanks.FIVE, CardSuits.HEARTS), Card(CardRanks.SIX, CardSuits.DIAMONDS),
                   Card(CardRanks.KING, CardSuits.HEARTS)]

hand1 = [Card(CardRanks.ACE, CardSuits.DIAMONDS), Card(CardRanks.NINE, CardSuits.CLUBS)]
hand2 = [Card(CardRanks.ACE, CardSuits.HEARTS), Card(CardRanks.NINE, CardSuits.SPADES)]

hands = [hand1, hand2]


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


# handle_tie_breaker([hand1, hand2], community_hands, HandRanking.HIGH_CARD)
hand_scores = {}
for index, hand in enumerate(hands):
    royal_flush = Evaluator.royal_flush(hand, community_hands)
    if royal_flush[0]:
        hand_scores[index] = HandRanking.ROYAL_FLUSH, royal_flush[1]
        continue
    straight_flush = Evaluator.straight_flush(hand, community_hands)
    if straight_flush[0]:
        hand_scores[index] = HandRanking.STRAIGHT_FLUSH, straight_flush[1]
        continue
    full_house = Evaluator.full_house(hand, community_hands)
    if full_house[0]:
        hand_scores[index] = HandRanking.FULL_HOUSE, full_house[1]
        continue
    flush = Evaluator.flush(hand, community_hands)
    if flush[0]:
        hand_scores[index] = HandRanking.FLUSH, flush[1]
        continue
    straight = Evaluator.straight(hand, community_hands)
    if straight[0]:
        hand_scores[index] = HandRanking.STRAIGHT, straight[1]
        continue
    three_kind = Evaluator.three_kind(hand, community_hands)
    if three_kind[0]:
        hand_scores[index] = HandRanking.THREE_KIND, three_kind[1]
        continue
    two_pair = Evaluator.two_pair(hand, community_hands)
    if two_pair[0]:
        hand_scores[index] = HandRanking.TWO_PAIR, two_pair[1]
        continue
    one_pair = Evaluator.one_pair(hand, community_hands)
    if one_pair[0]:
        hand_scores[index] = HandRanking.ONE_PAIR, one_pair[1]
        continue
    high_card = Evaluator.highest_card(hand, community_hands)
    if high_card[0]:
        hand_scores[index] = HandRanking.HIGH_CARD, high_card[1]
        continue

highest_score = 0
rank_dict: dict = {}


def compare_ranks(rank, rank_dict, community_hands):
    print(rank)
    print(rank_dict)
    return
    for player, rank_cards in rank_dict.items():
        if rank_cards[0] == HandRanking.HIGH_CARD:
            pass
            # compare high cards
        if rank_cards[0] == HandRanking.ONE_PAIR:
            pass
            # compare one pair
            # if equal compare kicker cards
        if rank_cards[0] == HandRanking.TWO_PAIR:
            pass
            # compare highest pair
            # if equal compare second pair
            # if equal compare kicker cards
        if rank_cards[0] == HandRanking.THREE_KIND:
            pass
            # Compare three kind cards
            # if equal compare first two kicker cards
        if rank_cards[0] == HandRanking.STRAIGHT:
            pass
            # Compare highest card
            # if equal compare following cards
        if rank_cards[0] == HandRanking.FLUSH:
            pass
            # Compare highest card
            # if equal compare following cards
        if rank_cards[0] == HandRanking.FULL_HOUSE:
            pass
            # Compare highest three cards
            # if equal compare two cards
        if rank_cards[0] == HandRanking.FOUR_KIND:
            pass
            # Compare highest rank of four cards
            # Compare kicker card
        if rank_cards[0] == HandRanking.STRAIGHT_FLUSH:
            pass
            # Compare highest card
            # if equal compare following cards
        if rank_cards[0] ==  HandRanking.ROYAL_FLUSH:
            return "equal"

    return "greater"


for player, score in hand_scores.items():
    if score[0] > highest_score:
        highest_score = score[0]
        rank_dict = {player: score}
    elif score[0] == highest_score:
        rank_comparison = compare_ranks(score[1], next(iter(rank_dict.values())), community_hands)
        if rank_comparison == "equal":
            rank_dict[player] = score
        elif rank_comparison == "greater":
            rank_dict = {player: score}


print(rank_dict)