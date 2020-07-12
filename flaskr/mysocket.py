from typing import Dict

from flask_socketio import join_room, leave_room

from flaskr import sio
from flask import request

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
    tables[room].add_player(user, request.sid)

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
    tables[room_id].initialize_round()


@sio.on("action")
def action(data):
    room_id = int(data.get("room"))

    table = tables[room_id]
    user = session_user()

    player = table.get_current_player()
    if player.user.id != user.id:
        sio.emit("message", "It is not yet your turn.", room=player.socket)
        return
    response = table.round(data.get("action"), int(data.get("value", 0)))
    sio.emit("message", response, room=player.socket)
    sio.emit("table_state", table.export_state(user), json=True, room=room_id)

    if table.check_phase_finish():
        sio.emit("message", "SYSTEM: Next round starting.")


@sio.on("table_state")
def action(data):
    room_id = int(data.get("room"))

    table = tables[room_id]
    user = session_user()

    sio.emit("table_state", table.export_state(user), json=True)


print("Loaded socket")
