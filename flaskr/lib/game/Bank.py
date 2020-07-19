from flaskr.lib.game import Player
from flaskr.lib.game.chip_utils import get_value


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
