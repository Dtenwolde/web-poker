let canvas = document.getElementById("canvas");
canvas.width = 1000;
canvas.height = 600;
let context = canvas.getContext("2d");
context.imageSmoothingEnabled = true;

const CARD_WIDTH = 222;
const CARD_HEIGHT = 323;

function getRelativeMousePosition(canvas, evt) {
    let rect = canvas.getBoundingClientRect();
    return {
        x: evt.clientX - rect.left,
        y: evt.clientY - rect.top
    };
}

function PokerTable() {
    this.hand = [];
    this.state = {};

    this.setHand = function(data) {
        this.hand = data;
    };

    this.setState = function(data) {
        this.state = data;
    };
}

// Game rendering stuff
function render() {
    context.clearRect(0, 0, canvas.width, canvas.height);

    // Draw background
    context.drawImage(images["board"], 0, 0, canvas.width, canvas.height);

    let img = images["ace_of_spades"];
    for (let i = 0; i < 5; i++) {
        placeCommunityCard(i, img);
    }

    let handCardWidth = 120;
    let handCardHeight = 180;
    for (let i = 0; i < pokerTable.hand.length; i++) {
        let x = 400 + i * 100;
        let y = 450;
        context.fillStyle = "beige";
        context.fillRect(x, y, handCardWidth, handCardHeight);
        let image_name = `${pokerTable.hand[i].rank}_of_${pokerTable.hand[i].suit}`;
        context.drawImage(images[image_name], x, y, handCardWidth, handCardHeight);
    }
}

function placeCommunityCard(index, card) {
    let x = 283.5 + 85.5 * index;
    let y = 258;
    let tableCardWidth = 60;
    let tableCardHeight = 90;

    context.fillStyle = "beige";
    context.fillRect(x, y, tableCardWidth, tableCardHeight);
    context.drawImage(card, x, y, tableCardWidth, tableCardHeight);
}

canvas.addEventListener("click", (e) => console.log(getRelativeMousePosition(canvas, e)));


let images = {};
let pokerTable = new PokerTable();

function initialize() {
    /*
     * Preload all images to reduce traffic later.
     */
    const ranks = ["ace", "king", "queen", "jack", "10", "9", "8", "7", "6", "5", "4", "3", "2"];
    const suits = ["hearts", "spades", "clubs", "diamonds"];
    let nLoads = 2;

    images["board"] = new Image();
    images["board"].onload = () => {
        nLoads--;
        if (nLoads === 0) postInit()
    };
    images["board"].src = `/static/images/board.png`;

    images["cardback"] = new Image();
    images["cardback"].onload = () => {
        nLoads--;
        if (nLoads === 0) postInit()
    };
    images["cardback"].src = `/static/images/cards/back.png`;

    ranks.forEach(rank => {
        suits.forEach(suit => {
            let card = `${rank}_of_${suit}`;
            images[card] = new Image();
            images[card].onload = () => {
                nLoads--;
                if (nLoads === 0) postInit()
            };
            images[card].src = `/static/images/cards/${card}.png`;
            nLoads++;
        });
    });

    /*
     * Register all socketio functions to the pokerTable object.
     */

    socket.on("hand", pokerTable.setHand);
    socket.on("table_state", pokerTable.setState);
    socket.on("message", (data) => console.log(data));
}

function postInit() {
    setInterval(render, 1000 / 60);
}

function call(action, value) {
    console.log("call")
    socket.emit("action", {"room": ROOM_ID, "action": action, "value": value})
}

function raise(action, value) {
    console.log("raise")
    socket.emit("action", {"room": ROOM_ID, "action": action, "value": value})
}

function fold(action, value) {
    console.log("fold")
    socket.emit("action", {"room": ROOM_ID, "action": action, "value": value})
}


initialize();
