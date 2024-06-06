import asyncio
import websockets
import pygame
import random
import json

boardWidth = 750
boardHeight = 500
playerRadii = 15
clock = pygame.time.Clock()
playerList = {}
websocketDict = {}

walls = [pygame.Rect(-40, -40, 50, boardHeight+40), # Left border
        pygame.Rect(-40, -40, boardWidth+40, 50), # Top border
        pygame.Rect(boardWidth - 10, 0, 50, boardHeight), # Right border
        pygame.Rect(-40, boardHeight - 10, boardWidth+40, 50), # Bottom border
         
        pygame.Rect(400, 0, 125, 175),
        pygame.Rect(125, boardHeight - 150, 100, 200),
        pygame.Rect(115, 0, 75, 225),
        pygame.Rect(125, 185, 150, 40),
        pygame.Rect(475, boardHeight - 250, 150, 150),
        pygame.Rect(475, boardHeight - 250, 400, 50)]


async def echo(websocket, path):
    print("Client connected")
    try:
        global walls
        global playerRadii
        global playerList

        while True:
            message = await websocket.recv()
            messageDict = json.loads(message)
            playerName, playerStats = next(iter(messageDict.items()))
            
            if playerName != "Display1234567890": # This is an intentionally odd username to minimise the chance of a player picking it.  
                playerList[playerName] = playerStats
                websocketDict[websocket] = playerName
                
                for wall in walls:
                    if playerStats[0] - playerRadii < wall.right and playerStats[0] + playerRadii > wall.left and playerStats[1] - playerRadii < wall.bottom and playerStats[1] + playerRadii > wall.top: 
                        xFace = min((playerStats[0] + playerRadii - wall.left),(playerStats[0] - playerRadii - wall.right),key=lambda x: abs(x)) # If the player hits the left wall, term 1 will be near 0 and positive, whereas term 2 will be large and negative.  If the player hits the right wall, term 1 will be large a positive, and term 2 will be near 0 and negative.  the abs part beings that this should always return the number closest to zero, so the near-zero positive or negative value.  
                        yFace = min((playerStats[1] + playerRadii - wall.top),(playerStats[1] - playerRadii - wall.bottom),key=lambda x: abs(x)) # This means that when considered together, xFace and yFace encode two pieces of information.  The value that is closer to zero indicates the axis of the wall that the player hit (xFace indicates that the player hit a vertical wall, defined by a value on the x-axis, and vis versa), and the sign on that smaller value indicates the direction of travel (positive for along the axis, negative for against it), and thus the wall that the player hit.  
                    
                        if abs(xFace) < abs(yFace):
                            if xFace > 0:
                                playerStats[0] = wall.left - playerRadii
                            else:
                                playerStats[0] = wall.right + playerRadii
                        else:
                            if yFace > 0:
                                playerStats[1] = wall.top - playerRadii
                            else:
                                playerStats[1] = wall.bottom + playerRadii
                            
                if playerStats[0] < 0 or playerStats[0] > boardWidth or playerStats[1] < 0 or playerStats[1] > boardHeight: # This if statement is basically an idiot-check to make sure that any players that randomly spawn inside a wall such that they get bumped outside of the map get stuck back into the map.  In theory this does not cover every case where a player can be put somewhere they should't be - they can, for example, get wedged between two walls and spend eternity getting bumped from one to the other between frames.  If this happens to a player, then the player can bloody well just quit and rejoin because i CANNOT figured out how to automatically catch this.   
                    playerStats[0] = pygame.Vector2((boardWidth/2)+random.randint(-50,50))
                    playerStats[1] = pygame.Vector2((boardHeight/2)+random.randint(-50,50))

            await asyncio.sleep(1/120)
            await websocket.send(json.dumps(playerList))
            
    except Exception as e:
        print("Client error - ",e)
        errorPlayer = websocketDict[websocket]
        del playerList[errorPlayer]
        print("Client Disconnected")
        
        
async def main():
    await websockets.serve(echo, "localhost", 8765)
    print("WebSocket server started on ws://localhost:8765")
    await asyncio.Future()
    
asyncio.run(main())