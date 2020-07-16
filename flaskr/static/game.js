let canvas = document.getElementById("canvas");
canvas.width = 1000;
canvas.height = 600;
let context = canvas.getContext("2d");
context.imageSmoothingEnabled = true;

let socket = io();

socket.on("join", (data) => {
    console.log("New user detected: " + data);
});

/*
 * Userlist and chat related socket io handlers.
 */
socket.on("user_list", (data) => {
    let userList = $(".user-list");
    userList.empty();
    data.forEach(player => {
        userList.append(`
            <div class="user-entry">
            <div class="user-entry-name">${player.username}</div>
            <div class="user-entry-balance">€${player.balance}</div>
            </div>
        `);
    })
});

$('#messageform').submit(function(e) {
    e.preventDefault(); // prevents page reloading
    console.log("prevented default");
    let m = $('#m');
    data = {
        "message": m.val(),
        "room": $('#roomid').val(),
        "username": $('#username').val()
    };
    socket.emit('chat message', data);
    m.val('');
    return false;
});

socket.on("chat message", (data) => {
    let messages = $('#messages');
    messages.append($('<li class="chat-message-entry">').text(data.username + ": " + data.message));
    document.getElementById("messages").lastChild.scrollIntoView();
});

function loadMainContent(gameWrapper) {
    let divs = document.getElementsByClassName("main-content");
    Array.from(divs).forEach((div) => {
        div.style.display = "none";
    });

    document.getElementById(gameWrapper).style.display = "flex";
}

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

    this.COMMUNITY_CARD_FLIP_MAXTICKS = 30;
    this.community_card_flip_ticks = [
        this.COMMUNITY_CARD_FLIP_MAXTICKS,
        this.COMMUNITY_CARD_FLIP_MAXTICKS * 1.5,
        this.COMMUNITY_CARD_FLIP_MAXTICKS * 3,
        this.COMMUNITY_CARD_FLIP_MAXTICKS,
        this.COMMUNITY_CARD_FLIP_MAXTICKS
    ];

    this.fadeMessages = [];

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
        placeCommunityCard(i);
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

function placeCommunityCard(index) {
    let img_name = `${pokerTable.state.community_cards[index].rank}_of_${pokerTable.state.community_cards[index].suit}`;
    let card = images[img_name];

    let x = 283.5 + 85.5 * index;
    let y = 258;
    let tableCardWidth = 60;
    let tableCardHeight = 90;

    context.fillStyle = "beige";
    if (pokerTable.community_card_flip_ticks[index] > 0) {
        let half = pokerTable.COMMUNITY_CARD_FLIP_MAXTICKS / 2;
        let ticks = pokerTable.community_card_flip_ticks[index]--;
        // First half of turning animation (back side up)

        let animation_percent = Math.sin(Math.min((ticks - half), pokerTable.COMMUNITY_CARD_FLIP_MAXTICKS - half) / half * Math.PI / 2);
        let width = tableCardWidth * animation_percent;
        let yOffset = -(1 - Math.abs(animation_percent)) * 7;

        let xOffset = (tableCardWidth - width) / 2 - (-(1 - Math.abs(animation_percent)) * 7);
        if (ticks > half) {
            context.drawImage(images["cardback"], x + xOffset, y + yOffset, width, tableCardHeight);
        } else {
            context.fillRect(x + xOffset, y + yOffset, width, tableCardHeight);
            context.drawImage(card, x + xOffset, y + yOffset, width, tableCardHeight);
        }
    } else {
        // Flat card on the table
        context.fillRect(x, y, tableCardWidth, tableCardHeight);
        context.drawImage(card, x, y, tableCardWidth, tableCardHeight);
    }
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
    socket.on("table_state", (data) => {
        pokerTable.setState(data);
        updateChips();
        document.getElementById("call-button").innerHTML = "Call with " + pokerTable.state.to_call
    });
    socket.on("message", (data) => {
        pokerTable.fadeMessages.push({
            message: data,
            ticks: 120
        });

        let log = document.getElementById("event-log");
        log.innerHTML += `
            <div class="event-log-entry">
                <div class="event-log-date">${new Date().toLocaleTimeString()}</div>
                <div class="event-log-value">${data}</div>
            </div>`;

        log.lastChild.scrollIntoView();
    });


    socket.emit("table_state", {
        "room": ROOM_ID
    });

    // Load all chips
    let chips = ["black", "blue", "green", "pink", "red", "white"];
    let div = document.getElementById("chip-wrapper");
    chips.forEach((chip) => {
        div.innerHTML += `
            <div class="chip-display">
                <div class="chip-image-wrapper">
                    <img class="chip-image" src="/static/images/chips/${chip}_chip.png"/>
                </div>
                <div class="chip-bottom" id="chip-value-${chip}">0 left.</div>
            </div>
        `;
    });
}

function updateChips() {
    let chips = ["black", "blue", "green", "pink", "red", "white"];

    chips.forEach((chip) => {
        document.getElementById(`chip-value-${chip}`).innerHTML = `${pokerTable.state.chips[chip]} left.`
    });

    rangeSlider.max = pokerTable.state.chip_sum / 100;
}

function postInit() {
    setInterval(render, 1000 / 60);
}


function raise() {
    sendAction("raise", rangeSlider.value * 100);
}

function fold() {
    sendAction("fold", 0);
}

function call() {
    sendAction("call", 0);
}

function sendAction(action, value) {
    socket.emit("action", {"room": ROOM_ID, "action": action, "value": value})
}

socket.on("start", (data) => {
    console.log("Got here");
    loadMainContent("game-wrapper");
    initialize();
});

function startRoom() {
    socket.emit("start", {
        room: ROOM_ID
    });
}

socket.emit("join", {
    "room": ROOM_ID,
});


/*
 * Load slider stuff
 */
let rangeSlider = document.getElementById("rs-range-line");
let rangeBullet = document.getElementById("rs-bullet");

rangeSlider.addEventListener("input", showSliderValue, false);

function showSliderValue() {
    if (rangeSlider.value === rangeSlider.max) {
        rangeBullet.innerHTML = "All In"
    } else {
        rangeBullet.innerHTML = rangeSlider.value;
    }
    let bulletPosition = (rangeSlider.value / rangeSlider.max);
    rangeBullet.style.left = (bulletPosition * 200) + "px";
}