
let canvas = document.getElementById("canvas");
let context = canvas.getContext("2d");

// Game rendering stuff
function render() {

}

let images = {};
function initialize() {
    images["hearts_queen"] = new Image();
    images["hearts_queen"].src = `static/images/${}`
}

initialize();
setInterval(render, 1000/60);