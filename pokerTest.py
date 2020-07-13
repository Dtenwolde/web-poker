from flaskr.lib.database import request_session
from flaskr.lib.game.PokerTable import PokerTable
from flaskr.lib.models.models import UserModel
from flaskr.lib.repository.user_repository import get_users, get_user


# def add_user_to_db(username, password):
#     db = request_session()
#     usermodel = UserModel(username, password)
#     db.add(usermodel)
#     db.commit()

def main():
    poker_table = PokerTable()
    poker_table.add_player(get_user("Daniel"), "1")
    poker_table.add_player(get_user("Duncan"), "2")
    users = get_users()
    for user in users:
        print(user.id)
    print(poker_table.export_players())
    poker_table.initialize_round()
    print(f"Small blind: {poker_table.get_small_blind().user.username}")
    print(f"Big blind: {poker_table.get_big_blind().user.username}")
    for player in poker_table.player_list:
        player_action = poker_table.round("call")
        print(poker_table.export_state(player.user))

if __name__ == "__main__":
    main()
