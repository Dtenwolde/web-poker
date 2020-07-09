let socket = io();

socket.on("join", function(data) {
    users[data] = "Temp";
    console.log("Socket detected");
});

function joinRoom(user, room) {
    socket.emit("join", {
        "room": room,
        "username": user
    });
    console.log(user, room)
}
// socket.emit('join', { 'room': room, .. }}
// socket.emit('send message', {'message': message, 'channel': channel});