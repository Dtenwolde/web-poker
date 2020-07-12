from flask_socketio import join_room, leave_room, rooms

from flaskr import sio


# from flaskr.lib.poker  import Poker, Player


@sio.on('join')
def on_join(data):
    username = data['id']
    room = data['room']
    join_room(room=room)
    print(f"User {username} joined room {room}")

    print(rooms())
    print(type(room))
    sio.emit("join", username, json=True, room=room)


@sio.on('leave')
def on_leave(data):
    username = data['id']
    room = data['room']
    leave_room(room)
    print(f"User {username} left room {room}")
    sio.emit("leave", username, json=True, room=room)


@sio.on("chat message")
def message(data):
    room = int(data.get('room'))
    if message != "":  # Stop empty messages
        sio.emit('chat message', data, room=room, include_self=True)


print("Loaded socket")
