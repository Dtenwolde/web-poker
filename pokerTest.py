from flaskr.lib.database import request_session
from flaskr.lib.game.PokerTable import PokerTable, Phases
from flaskr.lib.models.models import UserModel


def create_user(name, uid, balance):
    user = UserModel(name)
    user.id = uid
    user.balance = balance
    return user


def main():
    poker_table = PokerTable()

    duncan = create_user("Duncan", 1, 1000)
    daniel = create_user("Daniel", 2, 1000)

    poker_table.add_player(duncan, "1")
    poker_table.add_player(daniel, "2")

    print(poker_table.export_players())
    poker_table.initialize_round()
    print(f"Small blind: {poker_table.get_small_blind().user.username}")
    print(f"Big blind: {poker_table.get_big_blind().user.username}")

    while poker_table.phase != Phases.POST_ROUND:
        print(poker_table.get_current_player().user.username)
        poker_table.round("call")
        print(poker_table.get_current_player().user.username)
        poker_table.round("raise", 500)
        print(poker_table.get_current_player().user.username)
        poker_table.round("call")


if __name__ == "__main__":
    main()
