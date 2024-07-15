import pygame
import asyncio
import websockets
import VirusSim.jameswork.pyClient.InfectionLogic as infLog
import json

pygame.init()
clock = pygame.time.Clock()
running = True
wallShareCheck = False

wallDefs = []
dummyPlayerInfo = {}
dummyPlayerInfo["Display1234567890"] = [0,0,0,0,0,0,wallShareCheck] # This is an intentionally odd username to minimise the chance of a user picking it.  Even if they did it wouldn't crash the server - the user would just not be included in playerList, and so wouldn't be able to interact with anyone or be displayed on the map.  

uri = "ws://localhost:8765"

async def interlinked():
    async with websockets.connect(uri) as websocket:
        global running
        global wallDefs
        global wallShareCheck
        
        await websocket.send(json.dumps(dummyPlayerInfo)) # Before we get into the while loop, we want to poke the server to send up a one-off message containing the definitions for the window size and wall positions.  After this, ever message that this script receives from the server will be a playerList.  
        initialWallShare = await websocket.recv()
        wallDefs = json.loads(initialWallShare)
     
# ------------------------        
#        
# The wallDefs list is formatted like this:-
#boardWidth, 
#boardHeight, 
#(wallXPos,wallYPos,wallwidth,wallHeight),
#(wallXPos,wallYPos,wallwidth,wallHeight),
#.....
#
# ------------------------
       
        wallShareCheck = True
        
        screen = pygame.display.set_mode((wallDefs[0], wallDefs[1]))
        playerRadii = int(wallDefs[1] / (100/3)) # By defining the players radii like this, we can always have them and their text properly scaled to the window.  No more tiny players hiking across huge empty maps.  
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
                pygame.Rect(wallDefs[13])] # There is always going to be 12 walls in the map - 4 perimeter walls, four vertial, and four horizontal interior walls.  Im not going to change this now unless someone asks.  
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            screen.fill("White")
            
            font = pygame.font.Font(None, playerRadii)         
            for wall in walls:
                pygame.draw.rect(screen, "blue", wall)
                
            dummyPlayerInfo["Display1234567890"] = [0,0,0,0,0,0,wallShareCheck]    
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