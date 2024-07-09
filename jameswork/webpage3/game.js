const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const uri = "ws://localhost:8765";
const div = document.getElementById("myDiv");
let running = true;
let wallShareCheck = false;
let wallDefs = [];
let playerList = [];
let playerRadii;
let dummyPlayerInfo = {"Display1234567890": [0, 0, 0, 0, 0, 0, wallShareCheck]};
let counter = 0;
let color;

async function interlinked() {
    const websocket = new WebSocket(uri);

    websocket.onopen = async () => {
        websocket.send(JSON.stringify(dummyPlayerInfo));
        waitForWebSocketMessage()
            .then((message) => {
                //console.log(message);
                wallDefs = JSON.parse(message);
                canvas.width = wallDefs[0];
                canvas.height = wallDefs[1];
                playerRadii = Math.floor(wallDefs[1] / (100 / 3));
                wallShareCheck = true;
                dummyPlayerInfo = {"Display1234567890": [0, 0, 0, 0, 0, 0, wallShareCheck]};
                updateGame();
            })
            .catch((error) => {
                console.error(error);
            });
    };

    function waitForWebSocketMessage() {
        return new Promise((resolve, reject) => {
            // Handle connection errors
            websocket.onerror = (error) => {
                reject(new Error(`WebSocket error: ${error.message}`));
            };

            // Handle connection close
            websocket.onclose = () => {
                reject(new Error('WebSocket connection closed'));
            };

            // Handle message received
            websocket.onmessage = (event) => {
                resolve(event.data);
            };
        });
    }

    function updateGame() {
        websocket.send(JSON.stringify(dummyPlayerInfo));
        waitForWebSocketMessage()
            .then((message) => {
                //console.log(message);

                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = 'white';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = 'blue';
                for (let i = 2; i < wallDefs.length; i++) {
                    const wall = wallDefs[i];
                    ctx.fillRect(wall[0], wall[1], wall[2], wall[3]);
                }

                playerList = JSON.parse(message);
                for (const [name, stats] of Object.entries(playerList)) {
                    const [x, y, playerInfStatus, playerVirus] = stats;
        
                    let rMod = 0, gMod = 0, bMod = 0;
                    if (playerVirus.length > 0) {
                        let virusIntefied = 0;
                        for (const char of playerVirus) {
                            virusIntefied += char.charCodeAt(0);
                        }
                        const virusStr = virusIntefied.toString();
                        const first_two_digits = parseInt(virusStr.slice(0, 2));
                        let last_two_digits = parseInt(virusStr.slice(-2));
                        if (last_two_digits < 6) last_two_digits = 99;
        
                        if (virusIntefied === 1998) {
                            rMod = 255;
                            gMod = 153;
                            bMod = 255;
                        } else {
                            rMod = 255 - (30 * (10 / last_two_digits));
                            gMod = 150 * (10 / first_two_digits);
                            bMod = 125 * (10 / last_two_digits);
                        }
        
                        color = playerInfStatus ? `rgb(${rMod}, ${gMod}, ${bMod})` : 'green';
                    }
                    
                    ctx.fillStyle = color;
                    ctx.fillRect(x - playerRadii, y - playerRadii, playerRadii * 2, playerRadii * 2);
        
                    //ctx.fillStyle = 'black';
                    //ctx.fillRect(0, 0, 100, 100);

                    ctx.fillStyle = 'black';
                    ctx.font = `${playerRadii}px Arial`;
                    ctx.textAlign = 'center';
                    ctx.fillText(name, x, y);
        
                    //document.getElementById('testDiv').innerHTML = x + ", " + y + ", " + color + ", " + playerRadii;
                }

                requestAnimationFrame(updateGame);  // Schedule the next frame
            })
            .catch((error) => {
                console.error(error);
                requestAnimationFrame(updateGame);  // Schedule the next frame even on error
            });
    }
}

document.addEventListener('DOMContentLoaded', (event) => {
    interlinked();
});
