from typing import Dict

from flask_socketio import join_room, leave_room, rooms

from flaskr import sio


# from flaskr.lib.poker  import Poker, Player
from flaskr.lib.game.Player import Player
from flaskr.lib.game.PokerTable import PokerTable
from flaskr.lib.repository import room_repository
from flaskr.lib.user_session import session_user


tables: Dict[int, PokerTable] = {}


@sio.on('join')
def on_join(data):
    username = data['id']
    room = int(data['room'])
    join_room(room=room)

    if room not in tables:
        tables[room] = PokerTable()

    # TODO: Make sure a player is only joining a room once
    user = session_user()
    print(sio.id)
    tables[room].add_player(user, sio.id)

    sio.emit("join", username, json=True, room=room)
    sio.emit("user_list", tables[room].export_players(), json=True, room=room)


@sio.on('leave')
def on_leave(data):
    username = data['id']
    room = int(data['room'])
    leave_room(room)
    print(f"User {username} left room {room}")
    sio.emit("leave", username, json=True, room=room)


@sio.on("chat message")
def message(data):
    room = int(data.get('room'))
    if message != "":  # Stop empty messages
        sio.emit('chat message', data, room=room, include_self=True)


@sio.on("start")
def start(data):
    room_id = int(data.get("room"))

    room = room_repository.get_room(room_id)

    # Only the owner may start the game
    if room.author.id != session_user().id:
        print(room.author.id, session_user().id)
        return
    # Assume everybody is ready
    sio.emit("start", "None", room=room_id)


print("Loaded socket")
