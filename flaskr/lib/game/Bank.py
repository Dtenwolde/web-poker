

def get_value(chip: str):
    """
    Returns value of chip in cents
    """
    if chip == "black":
        return 10000
    if chip == "green":
        return 2500
    if chip == "blue":
        return 1000
    if chip == "red":
        return 500
    if chip == "pink":
        return 250
    if chip == "white":
        return 100


def cash_in(player: Player):
    """
    Gets current money status from the database and adds the value of all current chips in the player.
    """


    pass

def add_chips(player: Player, chip: str, amount: int = 1):
    if amount < 1:
        raise ValueError("Someone is trying to cheat the system >:(")

    cost = get_value(chip) * amount
    if player.user.pay(cost):
        player.chips[chip] += amount
    else:
        # TODO: Give the user feedback on his sad current(cy) situation
        pass