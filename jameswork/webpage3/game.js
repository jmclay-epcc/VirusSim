const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const plotCanvas = document.getElementById('plotCanvas');
const ctx2 = plotCanvas.getContext('2d');
const barCanvas = document.getElementById('barCanvas');
const ctx3 = barCanvas.getContext('2d');

const uri = "ws://localhost:8765";
const goodGreen = 'rgb(0,255,38)';
const barCanvasHeight = 400;
let running = true;
let wallShareCheck = false;

let wallDefs = [];
let playerList = [];
let uniqueVirus = [];
let viralCount = {};
let viralCountHist = [];
let healthyPlayers;
let playerRadii;
let dummyPlayerInfo = {"Display1234567890": [0, 0, 0, 0, 0, 0, wallShareCheck]};
let counter = 0;
let color;
let frameNo = [];
let playerCount = []; //this is a really hideous solution to this problem.  Do not judge me let ye be judged.  

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
                plotCanvas.width = 300;
                plotCanvas.height = wallDefs[1];
                barCanvas.width = wallDefs[0];
                barCanvas.height = barCanvasHeight;
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

    function colourFinder(virus, infStatus) {
        let rMod = 0, gMod = 0, bMod = 0;
        if (virus.length > 2) {
            let virusIntefied = 0;
            for (const char of virus) {
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

            return color = infStatus ? `rgb(${rMod}, ${gMod}, ${bMod})` : goodGreen;
        }
    }

    function updateGame() {
        websocket.send(JSON.stringify(dummyPlayerInfo));
        waitForWebSocketMessage()
            .then((message) => {
                //console.log(message);

                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx2.clearRect(0, 0, plotCanvas.width, plotCanvas.height);
                ctx3.clearRect(0, 0, barCanvas.width, barCanvas.height);
                ctx3.fillStyle = "gray";
                ctx3.fillRect(0, 0, barCanvas.width, barCanvas.height);

                ctx.fillStyle = 'blue';
                for (let i = 2; i < wallDefs.length; i++) {
                    const wall = wallDefs[i];
                    ctx.fillRect(wall[0], wall[1], wall[2], wall[3]);
                }

                playerList = JSON.parse(message);
                for (const [name, stats] of Object.entries(playerList)) {
                    const [x, y, playerInfStatus, playerVirus] = stats;

                    if (playerInfStatus) {
                        uniqueVirus.push(playerVirus);
                    }
                    else {
                        healthyPlayers += 1;
                    }
                    
                    color = colourFinder(playerVirus, playerInfStatus);
           
                    ctx.fillStyle = color;
                    ctx.fillRect(x - playerRadii, y - playerRadii, playerRadii * 2, playerRadii * 2);
        
                    //ctx.fillStyle = 'black';
                    //ctx.fillRect(0, 0, 100, 100);

                    ctx.fillStyle = 'black';
                    ctx.font = `${playerRadii}px Arial`;
                    ctx.textAlign = 'center';
                    ctx.fillText(name, x, y+(playerRadii/4));

                }

                uniqueVirus.forEach(function(num) {
                    viralCount[num] = (viralCount[num] || 0) + 1;
                });

                let totalPlayers = Object.keys(playerList).length;

                ctx2.fillStyle = goodGreen;
                ctx2.fillRect(0, 0, 300*(healthyPlayers/totalPlayers), 100);

                ctx2.fillStyle = "blue";
                ctx2.fillRect(0, 100, 300, 10);

                ctx2.fillStyle = 'black';
                ctx2.font = "30px Arial";
                ctx2.textAlign = 'center';
                if (healthyPlayers <= 0 && totalPlayers > 0) {
                    ctx2.fillText("Everyone is infected!", 150, 60);
                }
                else if (totalPlayers == 0) {
                    ctx2.fillText("No one is online :(", 150, 60);
                }
                else {
                    ctx2.fillText("Healthy players: " + healthyPlayers, 150, 60);
                }

                for (let key in viralCount) {
                    counter += 1;
                    ctx2.fillStyle = colourFinder(key,true);
                    ctx2.fillRect(0, 10+(100*counter), 300*(viralCount[key]/totalPlayers), 100);

                    ctx2.fillStyle = 'black';
                    ctx2.font = "30px Arial";
                    ctx2.textAlign = 'center';
                    ctx2.fillText(key + ": " + viralCount[key], 150, 70 + (100*counter));
                }

                uniqueVirus = [];
                healthyPlayers = 0;
                counter = 0;

                viralCountHist.push(viralCount);
                playerCount.push(totalPlayers);
                frameNo.push(frameNo.length + 1); // Use index as label
                viralCount = {};

                for (let frame of frameNo) {
                    barData = viralCountHist[frame-1];
                    let pastPlayerCount = playerCount[frame-1];
                    //document.getElementById("testDiv").innerText = JSON.stringify(barData);
                    let prevBarHeight = 0;
                    let totalInfected = 0;
                    for (let key in barData) {
                        //document.getElementById("testDiv2").innerText = prevKey;
                        ctx3.fillStyle = colourFinder(key,true)
                        ctx3.fillRect(((wallDefs[0]/frameNo.length)*(frame-1)), prevBarHeight, 2*(wallDefs[0]/frameNo.length), (barCanvasHeight*barData[key]/pastPlayerCount));
                        
                        prevBarHeight += barCanvasHeight*barData[key]/pastPlayerCount;
                        totalInfected += barData[key];
                    }
                    ctx3.fillStyle = goodGreen;
                    ctx3.fillRect(((wallDefs[0]/frameNo.length)*(frame-1)), prevBarHeight, 2*(wallDefs[0]/frameNo.length), (barCanvasHeight*(pastPlayerCount-totalInfected)/pastPlayerCount)); 
                }

                //document.getElementById("testDiv").innerText = frameNo;

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
