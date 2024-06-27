import asyncio
import websockets
import pygame
import random
import json

boardWidth = 750
boardHeight = 500
playerRadii = int(boardHeight / (100/3))
clock = pygame.time.Clock()
playerList = {}
websocketDict = {}

wallThickness = boardHeight / 10
wallDefs = [boardWidth,
            boardHeight,
            (-40, -40, 50, boardHeight+40), # The first four walls detailed are the boundary walls for the playable area.  Don't change these values! Don't even look them! 
            (-40, -40, boardWidth+40, 50),  # These numbers represent the rectangles X axis position, Y axis position, Length along X axis and length along Y axis.  Its also worth pointing out that this is measuring from the top-left corner, so the y-axis is upside down compared to a regular graph.  Its the same for JS though so it shouldnt be an issue.  
            (boardWidth - 10, 0, 50, boardHeight),
            (-40, boardHeight - 10, boardWidth+40, 50),
# - Horizontal lines
            (boardWidth * 1/8, boardHeight * 2/8, boardWidth * 2/8, wallThickness), # Top-left
            (boardWidth * 1/8, -wallThickness + boardHeight * 6/8, boardWidth * 2/8, wallThickness), # Bottom-left
            (boardWidth * 5/8, boardHeight * 2/8, boardWidth * 2/8, wallThickness), # Top-right
            (boardWidth * 5/8, -wallThickness + boardHeight * 6/8, boardWidth * 2/8, wallThickness), # Bottom-right
# - Vertical lines
            (-wallThickness + boardWidth * 3/8, -10, wallThickness, 10 + wallThickness + boardHeight * 2/8), # Top-left
            (-wallThickness + boardWidth * 3/8, -wallThickness + boardHeight * 6/8, wallThickness, 10 + wallThickness + boardHeight * 2/8), # Bottom-left
            (boardWidth * 5/8, -10, wallThickness, 10 + wallThickness + boardHeight * 2/8), # Top-right
            (boardWidth * 5/8, -wallThickness + boardHeight * 6/8, wallThickness, 10 + wallThickness + boardHeight * 2/8)] # Bottom-right

walls = [pygame.Rect(wallDefs[2]), # Left border
        pygame.Rect(wallDefs[3]), # Top border
        pygame.Rect(wallDefs[4]), # Right border
        pygame.Rect(wallDefs[5]), # Bottom border
         
        pygame.Rect(wallDefs[6]),
        pygame.Rect(wallDefs[7]),
        pygame.Rect(wallDefs[8]),
        pygame.Rect(wallDefs[9]),
        pygame.Rect(wallDefs[10]),
        pygame.Rect(wallDefs[11]),
        pygame.Rect(wallDefs[12]),
        pygame.Rect(wallDefs[13])]


async def echo(websocket, path):
    print("Client connected")
    try:
        global walls
        global playerRadii
        global playerList
        global wallDefs

        while True:
            message = await websocket.recv()
            messageDict = json.loads(message)
            playerName, playerStats = next(iter(messageDict.items()))
            websocketDict[websocket] = playerName
            await asyncio.sleep(1/60)
            
            if playerStats[6] == False:
                await websocket.send(json.dumps(wallDefs)) # We want to share the details of the window size and wall positions to the display, but we only want to send this info once; when the display first connects.  To this end, when the display connects to the server, the first message the server sends to it is the wall info instead of the player list.  The display is expecting this one-off message, so it is able to process that data as wall info before going to on process every following message as player info.  
            
            elif playerName != "Display1234567890": # This is an intentionally odd username to minimise the chance of a player picking it.  We don't want the display client to be put on playerList, because it isn't a player, so we filter it out by checking for its specific username.  
                playerList[playerName] = playerStats
                
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
                    playerStats[0] = (boardWidth/2)+int(random.randint(-boardWidth,boardWidth)/2)
                    playerStats[1] = (boardHeight/2)+int(random.randint(-boardHeight,boardHeight)/2)
                    
                await websocket.send(json.dumps(playerList))
                
            else:
                await websocket.send(json.dumps(playerList))
                
    except Exception as e:
        print("Client error - ",e)
        errorPlayer = websocketDict[websocket]
        if errorPlayer == "Display1234567890":
            print("Connect to display lost!")
            wallShareCheck = False
        else:
            del playerList[errorPlayer]
            print("Client Disconnected")
        
        
async def main():
    await websockets.serve(echo, "localhost", 8765)
    print("WebSocket server started on ws://localhost:8765")
    await asyncio.Future()
    
asyncio.run(main())