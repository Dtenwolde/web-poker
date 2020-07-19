import functools
from typing import Dict

from flask import request
from flask_socketio import join_room, leave_room

from flaskr import sio, logger
# from flaskr.lib.poker  import Poker, Player
from flaskr.lib.game.PokerTable import PokerTable, PokerException, Phases
from flaskr.lib.repository import room_repository
from flaskr.lib.user_session import session_user

tables: Dict[int, PokerTable] = {}


@sio.on('join')
def on_join(data):
    logger.debug("%s sent a %s request." % (request.sid, "join"))

    room_id = int(data['room'])
    join_room(room=room_id)

    if room_id not in tables:
        tables[room_id] = PokerTable(room_id)

    # TODO: Make sure a player is only joining a room once
    user = session_user()
    tables[room_id].add_player(user, request.sid)

    sio.emit("join", user.username, json=True, room=room_id)
    sio.emit("user_list", tables[room_id].export_players(), json=True, room=room_id)


@sio.on('leave')
def on_leave(data):
    logger.debug("%s sent a %s request." % (request.sid, "leave"))

    username = data['id']
    room = int(data['room'])
    leave_room(room)
    print(f"User {username} left room {room}")
    sio.emit("leave", username, json=True, room=room)


@sio.on("chat message")
def message(data):
    logger.debug("%s sent a %s request." % (request.sid, "chat message"))

    room = int(data.get('room'))
    if message != "":  # Stop empty messages
        sio.emit('chat message', data, room=room, include_self=True)


@sio.on("start")
def start(data):
    logger.debug("%s sent a %s request." % (request.sid, "start"))

    room_id = int(data.get("room"))
    room = room_repository.get_room(room_id)
    user = session_user()

    table = tables[room_id]
    player = table.get_player(user)

    # Only the owner may start the game
    if room.author.id != user.id:
        sio.emit("message", "You are not the room owner.", room=player.socket)
        return

    try:
        table.initialize_round()
        # Assume everybody is ready, maybe implement ready check later
        sio.emit("start", "None", room=room_id)
    except PokerException as e:
        print(e.message, player.socket)
        sio.emit("message", e.message, room=player.socket)


@sio.on("begin")
def begin(data):
    room_id = int(data.get("room"))
    room = room_repository.get_room(room_id)
    user = session_user()

    table = tables[room_id]
    player = table.get_player(user)
    # Only the owner may start the game
    if room.author.id != user.id:
        sio.emit("message", "You are not the room owner.", room=player.socket)
        return

    table.phase = Phases.PRE_FLOP

    sio.emit("begin", None, room=room_id)


@sio.on("action")
def action(data):
    logger.debug("%s sent a %s request." % (request.sid, "action"))

    room_id = int(data.get("room"))

    table = tables[room_id]
    user = session_user()

    current_player = table.get_current_player()
    player = table.get_player(user)
    if current_player.user.id != user.id:
        sio.emit("message", "It is not yet your turn.", room=player.socket)
        return

    response = table.round(data.get("action"), int(data.get("value", 0)))

    if response is not None:
        sio.emit("message", response, room=player.socket)

    for table_player in table.player_list:
        sio.emit("table_state", table.export_state(table_player), json=True, room=table_player.socket)


@sio.on("table_state")
def action(data):
    logger.debug("%s sent a %s request." % (request.sid, "table_state"))

    room_id = int(data.get("room"))

    table = tables[room_id]
    user = session_user()
    player = table.get_player(user)
    sio.emit("table_state", table.export_state(player), json=True, room=player.socket)


print("Loaded socket")
