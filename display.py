import pygame
import asyncio
import websockets
import InfectionLogic as infLog
import json

pygame.init()
boardWidth = 1000
boardHeight = 750
playerRadii = 15
screen = pygame.display.set_mode((boardWidth, boardHeight))
clock = pygame.time.Clock()
running = True
dt = 0

dummyPlayerInfo = {}
dummyPlayerInfo["Display1234567890"] = [] # This is an intentionally odd username to minimise the chance of a user picking it.  Even if they did it wouldn't crash the server - the user would just not be included in playerList, and so wouldn't be able to interact with anyone or be displayed on the map.  

walls = [pygame.Rect(-40, -40, 50, boardHeight+40), # Left border
        pygame.Rect(-40, -40, boardWidth+40, 50), # Top border
        pygame.Rect(boardWidth - 10, 0, 50, boardHeight), # Right border
        pygame.Rect(-40, boardHeight - 10, boardWidth+40, 50), # Bottom border
         
        pygame.Rect(boardWidth - 300, 0, 125, 175),
        pygame.Rect(boardWidth - 800, boardHeight - 150, 100, 200),
        pygame.Rect(boardWidth - 700, 0, 75, 225),
        pygame.Rect(boardWidth - 800, 185, 150, 40),
        pygame.Rect(boardWidth - 400, boardHeight - 250, 150, 150),
        pygame.Rect(boardWidth - 400, boardHeight - 250, 400, 50)]

uri = "ws://localhost:8765"

async def interlinked():
    global running
    async with websockets.connect(uri) as websocket:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            screen.fill("White")
            
            font = pygame.font.Font(None, playerRadii)         
            for wall in walls:
                pygame.draw.rect(screen, "blue", wall)
                
            await websocket.send(json.dumps(dummyPlayerInfo))
            response = await websocket.recv()
            playerList = json.loads(response)
            
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

        pygame.quit()

asyncio.run(interlinked())