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
    this.state = {
        community_cards: [],
        hand: [],
        active_player: ""
    };

    this.fadeMessages = [{
        message: "Connected.",
        ticks: 60
    }, {
        message: "It is not your turn yet.",
        ticks: 120
    }, {
        message: "Duncan raised with 400.",
        ticks: 180
    }, {
        message: "Daniel called 400.",
        ticks: 240
    }, {
        message: "Fabienne folded.",
        ticks: 300
    }, {
        message: "Duncan called.",
        ticks: 300
    }];

    this.setHand = function(data) {
        this.hand = data;
    };

    this.setState = function(data) {
        this.state = {
            ...data
        };
    };

    this.MESSAGE_HEIGHT = 40;
    this.drawFadeMessages = function() {
        let origHeight = 100;
        if (this.fadeMessages.length > 0) {
            if (this.fadeMessages[0].ticks < 0) {
                this.fadeMessages = this.fadeMessages.slice(1);
            } else {
                origHeight -= (1 - Math.min(1, this.fadeMessages[0].ticks / 30)) * this.MESSAGE_HEIGHT * 1.5;
            }
        }
        let n_visible = Math.min(5, this.fadeMessages.length);
        for (let i = 0; i < n_visible; i++) {
            let fm = this.fadeMessages[i];
            let percent = Math.min(1, fm.ticks / 30);

            context.font = `${this.MESSAGE_HEIGHT}px Arial`;
            context.strokeStyle = `rgba(0, 0, 0, ${percent})`;
            context.lineWidth = 0.5;
            context.fillStyle = `rgba(165, 70, 50, ${percent})`;

            let len = context.measureText(fm.message);
            context.fillText(fm.message, 480 - len.width / 2, origHeight + i * this.MESSAGE_HEIGHT * 1.5);
            context.strokeText(fm.message, 480 - len.width / 2, origHeight + i * this.MESSAGE_HEIGHT * 1.5);
            context.stroke();

            fm.ticks--;
        }
    }
}


// Game rendering stuff
function render() {
    context.clearRect(0, 0, canvas.width, canvas.height);

    // Draw background
    context.drawImage(images["board"], 0, 0, canvas.width, canvas.height);

    for (let i = 0; i < pokerTable.state.community_cards.length; i++) {
        let img_name = `${pokerTable.state.community_cards[i].rank}_of_${pokerTable.state.community_cards[i].suit}`;
        let img = images[img_name];

        placeCommunityCard(i, img);
    }

    let handCardWidth = 100;
    let handCardHeight = 150;
    for (let i = 0; i < pokerTable.state.hand.length; i++) {
        let x = 400 + i * 110;
        let y = 450;
        context.fillStyle = "beige";
        context.fillRect(x, y, handCardWidth, handCardHeight);
        let image_name = `${pokerTable.state.hand[i].rank}_of_${pokerTable.state.hand[i].suit}`;
        context.drawImage(images[image_name], x, y, handCardWidth, handCardHeight);
    }

    context.fillStyle = "black";
    context.font = "20px Arial";
    context.fillText(`Current turn: ${pokerTable.state.active_player}`, 10, 20);

    pokerTable.drawFadeMessages();

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
     * Register all socket.io functions to the pokerTable object.
     */

    socket.on("hand", (data) => {
        console.log(data);
        pokerTable.setHand(data);
    });
    socket.on("table_state", (data) => {
        pokerTable.setState(data);
    });
    socket.on("message", (data) => {
        pokerTable.fadeMessages.push({
            message: data,
            ticks: 60
        })
    });


    socket.emit("table_state", {
        "room": ROOM_ID
    });
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

socket.emit("join", {
    "room": ROOM_ID,
});
initialize();


