import asyncio
import websockets
import pygame
import random

pygame.init()
boardWidth = 750
boardHeight = 500
playerRadii = 15
screen = pygame.display.set_mode((boardWidth, boardHeight))
clock = pygame.time.Clock()
running = True
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

screen.fill("white")
pygame.display.flip()

async def echo(websocket, path):
    print("Client connected")
    try:
        global running
        global walls
        global playerRadii
        global playerList
        while running:
            
            message = await websocket.recv()
            messageDict = eval(message)
            playerName, playerStats = next(iter(messageDict.items()))
            
            screen.fill("white")
            font = pygame.font.Font(None, playerRadii)         
            for wall in walls:
                pygame.draw.rect(screen, "blue", wall)
            
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

            playerList[playerName] = playerStats
            websocketDict[websocket] = playerName
            
            for name, stats in playerList.items():
                playerInfStatus = stats[2]
                playerVirus = stats[3]
                virusStringified = list(playerVirus)
                virusIntefied = 0
                
                if len(virusStringified) == 0:
                    gMod = 0
                    rMod = 0
                else:
                    for i in virusStringified: # The purpose of this for loop is to turn convert the name of a virus into a number, which we can then use to modify the colour of the infected player.  This means that we can easily ("easily") tell what virus a player has by looking at it.  
                        virusIntefied += ord(i)
                    number_str = str(virusIntefied)
                    first_two_digits = int(number_str[:2])
                    last_two_digits = int(number_str[-2:])
                    if last_two_digits < 6:
                        last_two_digits = 99 # The last two digits of the virus name seed can be between 00 and 09.  If this is the case, then the 10/last_two_digits fraction can produce a number greater than 1, which is not so bad in most cases, but it still something i'd like to avoid.  
                    if virusIntefied == 1998: # Players that manage to stumble on a virus name that translates to 1998 - the year i was born - are automatically awarded a special dot colour.  According to a quick program i wrote, the only two words in the entire english dictionary that meet this criteria are "ventrocystorrhaphy" and "unostentatiousness".  And despite my initial excitment, "ventrocystorrhaphy" is a medical procedure, not a disease.  There are a HUGE number of combinations of two words (with a space) that equal 1998. 
                        rMod = 255
                        gMod = 153
                        bMod = 255
                    else:
                        rMod = 255 - (30 * (10/last_two_digits))
                        gMod = 150 * (10/first_two_digits)
                        bMod = 125 * (10/last_two_digits)
                
                if playerInfStatus == True:
                    colour = (rMod,gMod,bMod)
                    status = ":("
                else:
                    colour = "Green"
                    status = ":)"
                    
                playerPos = [stats[0],stats[1]]
                text_surface = font.render(name, True, "black")
                text_rect = text_surface.get_rect(center=playerPos)
                pygame.draw.circle(screen, colour, playerPos, playerRadii)
                screen.blit(text_surface, text_rect)
            pygame.display.flip()

            await websocket.send(str(playerList))
    except Exception as e:
        print("Client error - ",e)
        errorPlayer = websocketDict[websocket]
        del playerList[errorPlayer]
        print("Client Disconnected")
            
async def main():
    # Start the WebSocket server on localhost at port 8765
    async with websockets.serve(echo, "localhost", 8765):
        print("WebSocket server started on ws://localhost:8765")
        # Keep the event loop running indefinitely
        global running
        while running:
            global walls
            global playerList
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            if playerList == {}: # We want some game events to always run, even when no one is connected to the server.  So, when playerList is empty, we run this very stripped down version of the game code that just prints the background and the walls, and refreshes the page every frame.  
                    
                screen.fill("white")        
                for wall in walls:
                    pygame.draw.rect(screen, "blue", wall)
                    
                font = pygame.font.Font(None, 40)     
                text_surface = font.render("No players connected...", True, "black")
                text_rect = text_surface.get_rect(center=((boardWidth/2)+80,(boardHeight/2)-43))
                screen.blit(text_surface, text_rect)
                pygame.display.flip()
            
            await asyncio.sleep(0.01)  # Sleep briefly to allow other tasks to run
            pygame.event.pump()  # Manually handle Pygame events
            clock.tick(40)

# Run the main coroutine
asyncio.run(main())