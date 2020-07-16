from flaskr.lib.game.Card import CardRanks

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
                return True

    return False


def straight_flush(hand, community_cards):
    suits_count = get_suits(hand + community_cards)
    for suit in suits_count.values():
        if len(suit) >= 5:
            index = -1  # To get highest possible straight flush go from highest to lowest cards
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
            return True, in_row
    return False


def four_kind(hand, community_cards):
    rank_dict = get_ranks(hand + community_cards)
    for rank, cards in rank_dict.items():
        if len(cards) == 4:
            return True, cards
    return False


def full_house(card, community_cards):
    rank_dict = get_ranks(card + community_cards)
    full_house_cards = []
    for rank, cards in rank_dict.items():
        if len(cards) == 3:
            full_house_cards += cards
            highest_rank = None  # Lowest possible
            for rank_, cards_ in rank_dict.items():
                if len(cards_) >= 2 and rank_ != rank:
                    if highest_rank is None:
                        highest_rank = rank_
                    elif rank_.value > highest_rank.value:
                        highest_rank = rank_
            if highest_rank is not None:
                full_house_cards += rank_dict[highest_rank]
                return True
    return False


def flush(hand, community_cards):
    suit_dict = get_suits(hand + community_cards)
    for suit, cards in suit_dict.items():
        if len(cards) >= 5:
            return True, cards
    return False


def straight(hand, community_cards):
    values = []
    for card in hand + community_cards:
        values.append(card.rank.value)
    sorted_values = list(set(sorted(values)))  # Only keep unique ranks
    index = -1
    in_row = [sorted_values[index]]
    while len(in_row) < 5:
        try:
            if sorted_values[index] - 1 == sorted_values[index - 1]:
                in_row.append(sorted_values[index - 1])
            else:
                in_row = [sorted_values[index - 1]]
            index -= 1
        except IndexError:
            return False
    return True


def three_kind(hand, community_cards):
    rank_dict = get_ranks(hand + community_cards)
    highest_rank = None
    for rank, cards in rank_dict.items():
        if len(cards) == 3:
            if highest_rank is None:
                highest_rank = rank
            elif rank.value > highest_rank.value:
                highest_rank = rank
    if highest_rank is not None:
        return True
    return False


def two_pair(hand, community_hands):
    rank_dict = get_ranks(hand + community_hands)
    highest_rank = second_highest_rank = None
    for rank, cards in rank_dict.items():
        if len(cards) == 2:
            if highest_rank is None:
                highest_rank = rank
            elif second_highest_rank is None:
                if rank.value > highest_rank.value:
                    second_highest_rank = highest_rank
                    highest_rank = rank
                else:
                    second_highest_rank = rank
            elif rank.value > highest_rank.value:
                second_highest_rank = highest_rank
                highest_rank = rank
            elif rank.value > second_highest_rank.value:
                second_highest_rank = rank
    if second_highest_rank is None:
        return False
    else:
        return True


def one_pair(hand, community_hands):
    rank_dict = get_ranks(hand + community_hands)
    highest_rank = None
    for rank, cards in rank_dict.items():
        if len(cards) == 2:
            if highest_rank is None:
                highest_rank = rank
            elif rank.value > highest_rank.value:
                highest_rank = rank
    if highest_rank is None:
        return False

    return True


def highest_card(hand, community_hands):
    rank_dict = get_ranks(hand + community_hands)
    highest_rank = None
    for rank, cards in rank_dict.items():
        if highest_rank is None:
            highest_rank = rank
        elif rank.value > highest_rank.value:
            highest_rank = rank

    return True