import json

from flaskr import sio
from flask_socketio import emit, join_room, leave_room
from flaskr.lib.poker  import Poker, Player

@sio.on('join')
def on_join(data):
    name = data.get("username")
    print(name)

@sio.on("send message")
def message(data):
    room = data['channel']
    emit('broadcast message', data['message'], room=room)

print("Loaded socket")