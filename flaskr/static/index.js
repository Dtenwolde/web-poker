let socket = io();

socket.on("join", (data) => {
    console.log("New user detected: " + data);
});

socket.on("user_list", (data) => {


});

function joinRoom(userId, room, username) {
    socket.emit("join", {
        "room": room,
        "id": userId,
    });

}

function askPassword(password, room_id) {
    console.log("got here")
    let input = prompt("Password: ")
    while (input != password) {
        if (input === null) {
            return
        }
        input = prompt("Password incorrect, please try again: ")
    }

    window.location.replace(`/${room_id}/join`)
}

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