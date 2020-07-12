let socket = io();

socket.on("join", (data) => {
    console.log("New user detected: " + data);
});

function joinRoom(userId, room, username) {
    socket.emit("join", {
        "room": room,
        "id": userId,
    });
    $(".about").append("<p>" + username + "</p>");
}

// socket.emit('join', { 'room': room, .. }}
// socket.emit('send message', {'message': message, 'channel': channel});

$('#messageform').submit(function(e) {
    e.preventDefault(); // prevents page reloading
    console.log("prevented default");
    data = {
        "message": $('#m').val(),
        "room": $('#roomid').val(),
        "username": $('#username').val()
    }
    socket.emit('chat message', data);
    $('#m').val('');
    return false;
});

socket.on("chat message", (data) => {
    $('#messages').append($('<li>').text(data.username + ": " + data.message));
});

socket.on("start", (data) => {
    console.log(data);
    document.location.replace(GAME_URL);
});

function startRoom() {
    socket.emit("start", {
        room: ROOM_ID
    });
}