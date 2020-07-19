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


def royal_flush(cards):
    suits_count = get_suits(cards)
    for cards in suits_count.values():
        if len(cards) >= 5:  # Amount of same suit needed for royal flush to be possible
            royal_flush_cards = []
            for card in cards:
                if card >= 10:
                    royal_flush_cards.append(card)
            if len(royal_flush_cards) == 5:
                return True, royal_flush_cards
    return False, None


def straight_flush(cards):
    suits_count = get_suits(cards)
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
                    return False, None
            return True, in_row
    return False, None


def four_kind(cards):
    rank_dict = get_ranks(cards)
    for rank, cards in rank_dict.items():
        if len(cards) == 4:
            return True, cards
    return False, None


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
                return True, full_house_cards
    return False, None


def flush(cards):
    suit_dict = get_suits(cards)
    for suit, cards in suit_dict.items():
        if len(cards) >= 5:
            return True, cards
    return False, None


def straight(cards):
    values = []
    for card in cards:
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
            return False, None
    return True, in_row


def three_kind(cards):
    rank_dict = get_ranks(cards)
    highest_rank = None
    for rank, cards in rank_dict.items():
        if len(cards) == 3:
            if highest_rank is None:
                highest_rank = rank
            elif rank.value > highest_rank.value:
                highest_rank = rank
    if highest_rank is not None:
        return True, highest_rank
    return False, None


def two_pair(cards):
    rank_dict = get_ranks(cards)
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
        return False, None
    else:
        return True, highest_rank, second_highest_rank


def one_pair(cards):
    rank_dict = get_ranks(cards)
    highest_rank = None
    for rank, cards in rank_dict.items():
        if len(cards) == 2:
            if highest_rank is None:
                highest_rank = rank
            elif rank.value > highest_rank.value:
                highest_rank = rank
    if highest_rank is None:
        return False, None

    return True, highest_rank


def highest_card(cards):
    rank_dict = get_ranks(cards)
    highest_rank = None
    for rank, cards in rank_dict.items():
        if highest_rank is None:
            highest_rank = rank
        elif rank.value > highest_rank.value:
            highest_rank = rank

    return True, highest_rank

