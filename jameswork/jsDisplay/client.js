const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const uri = "ws://localhost:8765";
const goodGreen = 'rgb(0,255,38)';
const margin = 40;
const borderWidth = 25;
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
let viralStats = {} //This is an even uglier solution to a different problem.  Oops! 

async function interlinked() {
    const websocket = new WebSocket(uri);

    websocket.onopen = async () => {
        websocket.send(JSON.stringify(dummyPlayerInfo));
        waitForWebSocketMessage()
            .then((message) => {
                //console.log(message);
                wallDefs = JSON.parse(message);

                boardWidth = wallDefs[0];
                boardHeight = wallDefs[1];
                dataWidth = 600
                dataHeight = boardHeight;
                barWidth = boardWidth + dataWidth + (margin*2);
                barHeight = 400;
                canvas.width = boardWidth + dataWidth + (margin*4);
                canvas.height = boardHeight + barHeight + (margin*4);

                canvasOrigX = 0;
                canvasOrigY = 0;
                boardOrigX = canvasOrigX + margin;
                boardOrigY = canvasOrigY + margin;
                dataOrigX = boardOrigX + boardWidth + (margin*2);
                dataOrigY = boardOrigY;
                barOrigX = boardOrigX;
                barOrigY = boardOrigY + boardHeight + (margin*2); //Im being quite redunant with these variables, as a few of them are set to be equal to each other.  But for the sake of clear variable naming (and my own sanity) i've given them all unique names.  

                playerRadii = Math.floor(wallDefs[1] / 35);
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

                ctx.clearRect(canvasOrigX, canvasOrigY, canvas.width, canvas.height);
                ctx.fillStyle = "gray";
                ctx.fillRect(barOrigX, barOrigY, barWidth, barHeight);

                ctx.fillStyle = 'blue';
                for (let i = 2; i < wallDefs.length; i++) {
                    const wall = wallDefs[i];
                    ctx.fillRect(wall[0]+margin, wall[1]+margin, wall[2], wall[3]);
                }

                playerList = JSON.parse(message);
                for (const [name, stats] of Object.entries(playerList)) {
                    const [x, y, playerInfStatus, playerVirus, infDist, infStrength] = stats;

                    if (playerInfStatus) {
                        uniqueVirus.push(playerVirus);
                        viralStats[playerVirus] = [infDist,infStrength];
                    }
                    else {
                        healthyPlayers += 1;
                    }
                    
                    color = colourFinder(playerVirus, playerInfStatus);
           
                    ctx.fillStyle = color;
                    ctx.fillRect(x - playerRadii+margin, y - playerRadii+margin, playerRadii * 2, playerRadii * 2);

                    ctx.fillStyle = 'black';
                    ctx.font = `${playerRadii}px Arial`;
                    ctx.textAlign = 'center';
                    ctx.fillText(name, x+margin, y+(playerRadii/4)+margin);

                }

                uniqueVirus.forEach(function(num) {
                    viralCount[num] = (viralCount[num] || 0) + 1;
                });

                let totalPlayers = Object.keys(playerList).length;

                ctx.fillStyle = goodGreen;
                ctx.fillRect(dataOrigX, dataOrigY, 300*(healthyPlayers/totalPlayers), 100);

                ctx.fillStyle = "blue";
                ctx.fillRect(dataOrigX, dataOrigY + 100, 600, 10);
                ctx.fillRect(dataOrigX + 300, dataOrigY, 10, wallDefs[1]);

                ctx.fillStyle = 'black';
                ctx.font = "30px Arial";
                ctx.textAlign = 'center';
                if (healthyPlayers <= 0 && totalPlayers > 0) {
                    ctx.fillText("Everyone is infected!", dataOrigX + 150, dataOrigY + 60);
                }
                else if (totalPlayers == 0) {
                    ctx.fillText("No one is online :(", dataOrigX + 150, dataOrigY + 60);
                }
                else {
                    ctx.fillText("Healthy players: " + healthyPlayers, dataOrigX + 150, dataOrigY + 60);
                }

                ctx.fillText("Range & Strength", dataOrigX + 450, dataOrigY + 60);

                let sortedKeys = Object.keys(viralCount).sort();
                sortedKeys.forEach(key => {
                    counter += 1;
                    ctx.fillStyle = colourFinder(key,true);
                    ctx.fillRect(dataOrigX, dataOrigY + 10+(100*counter), 300*(viralCount[key]/totalPlayers), 100);

                    ctx.fillStyle = 'black';
                    ctx.font = "30px Arial";
                    ctx.textAlign = 'center';
                    ctx.fillText(key + ": " + viralCount[key], dataOrigX + 150, dataOrigY + 70 + (100*counter));
                    ctx.fillText(viralStats[key], dataOrigX + 450, dataOrigY + 70 + (100*counter));
                });

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

                    let sortedKeys2 = Object.keys(barData).sort();
                    sortedKeys2.forEach(key => {
                        //document.getElementById("testDiv2").innerText = prevKey;
                        ctx.fillStyle = colourFinder(key,true);
                        ctx.fillRect(barOrigX + ((barWidth/frameNo.length)*(frame-1)), barOrigY + prevBarHeight, (barWidth/frameNo.length), (barHeight*barData[key]/pastPlayerCount));
                        ctx.lineWidth = 5;
                        ctx.strokeStyle = colourFinder(key,true);
                        ctx.strokeRect(barOrigX + ((barWidth/frameNo.length)*(frame-1)), barOrigY + prevBarHeight, (barWidth/frameNo.length), (barHeight*barData[key]/pastPlayerCount));

                        prevBarHeight += barHeight*barData[key]/pastPlayerCount;
                        totalInfected += barData[key];
                    });
                    ctx.fillStyle = goodGreen;
                    ctx.fillRect(barOrigX + ((barWidth/frameNo.length)*(frame-1)), barOrigY + prevBarHeight, (barWidth/frameNo.length), (barHeight*(pastPlayerCount-totalInfected)/pastPlayerCount)); 
                    ctx.lineWidth = 5;
                    ctx.strokeStyle = goodGreen;
                    ctx.strokeRect(barOrigX + ((barWidth/frameNo.length)*(frame-1)), barOrigY + prevBarHeight, (barWidth/frameNo.length), (barHeight*(pastPlayerCount-totalInfected)/pastPlayerCount)); 
                }

                ctx.lineWidth = borderWidth;
                ctx.strokeStyle = "blue";
                ctx.strokeRect(boardOrigX - (borderWidth/2), boardOrigY - (borderWidth/2), boardWidth + borderWidth, boardHeight + borderWidth);
                ctx.strokeRect(dataOrigX - (borderWidth/2), dataOrigY - (borderWidth/2), dataWidth + borderWidth, dataHeight + borderWidth);
                ctx.strokeRect(barOrigX - (borderWidth/2), barOrigY - (borderWidth/2), barWidth + borderWidth, barHeight + borderWidth);

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
