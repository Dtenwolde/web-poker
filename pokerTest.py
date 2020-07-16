from flaskr.lib.game.Player import Player
from flaskr.lib.game.PokerTable import PokerTable, Phases
from flaskr.lib.models.models import UserModel


def create_user(name, uid, balance):
    user = UserModel(name)
    user.id = uid
    user.balance = balance
    return user


def main():
    poker_table = PokerTable("3")

    duncan = create_user("Duncan", 1, 1000)
    daniel = create_user("Daniel", 2, 1000)

    player_duncan = Player(duncan, "1")
    player_daniel = Player(daniel, "2")

    poker_table.player_list.extend([player_duncan, player_daniel])

    print(poker_table.export_players())
    poker_table.initialize_round()
    print(f"Small blind: {poker_table.get_small_blind().user.username}")
    print(f"Big blind: {poker_table.get_big_blind().user.username}")

    while poker_table.phase != Phases.POST_ROUND:
        print(poker_table.export_state(player_duncan)['hand'])

        print(poker_table.get_current_player().user.username, end=" ")
        poker_table.round("call")
        print(poker_table.get_current_player().user.username, end=" ")
        poker_table.round("raise", 500)
        print(poker_table.get_current_player().user.username, end=" ")
        poker_table.round("call")

    print(poker_table.export_state(Player(duncan, "1")))


if __name__ == "__main__":
    main()
