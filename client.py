import pygame
import asyncio
import websockets
import random
import math

pygame.init()
uiSize = 300
uiSizeHalf = uiSize/2
screen = pygame.display.set_mode((uiSize, uiSize))
clock = pygame.time.Clock()
dt = 0
fps = 40
infDist = 30
infCheckTime = 1 # A player that is infected will only check for other infected player near by once every this seconds. 

playerPos = pygame.Vector2(250, 250)
playerName = "james"
playerInfo = {}
infStatus = False

uri = "ws://localhost:8765"

async def interlinked():
    async with websockets.connect(uri) as websocket:
        global infStatus
        running = True
        counter = 2
        upCol = "gray"
        downCol = "gray"
        leftCol = "gray"
        rightCol = "gray"
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill("purple")
            pygame.draw.circle(screen, upCol, (uiSizeHalf,uiSizeHalf-75), 20) # up arrow
            pygame.draw.circle(screen, downCol, (uiSizeHalf,uiSizeHalf+75), 20) # down arrow
            pygame.draw.circle(screen, leftCol, (uiSizeHalf-75,uiSizeHalf), 20) # left arrow
            pygame.draw.circle(screen, rightCol, (uiSizeHalf+75,uiSizeHalf), 20) # right arrow

            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                playerPos.y -= 300 * dt
                upCol = "blue"
            else:
                upCol = "gray"
            if keys[pygame.K_DOWN]:
                playerPos.y += 300 * dt
                downCol= "blue"
            else:
                downCol = "gray"
            if keys[pygame.K_LEFT]:
                playerPos.x -= 300 * dt
                leftCol = "blue"
            else:
                leftCol = "gray"
            if keys[pygame.K_RIGHT]:
                playerPos.x += 300 * dt
                rightCol = "blue"
            else:
                rightCol = "gray"
                
            if keys[pygame.K_i]:
                infStatus = True
                
            if keys[pygame.K_u]:
                infStatus = False

            pygame.display.flip()
            
            playerInfo[playerName] = [playerPos.x,playerPos.y,infStatus, counter]

            await websocket.send(str(playerInfo))
            
            response = await websocket.recv()
            playerList = eval(response)
            
            newStats = playerList[playerName]
            playerPos.x = newStats[0]
            playerPos.y = newStats[1]
            
            if infStatus == False and counter >= (infCheckTime * fps):
                # The next chuck of script to see how close every other player in the dictionary is to current player, and then determines if current player can and should be infected by them.  I find it quite confusing - for loops inside for loops.  
                for nthPlayer, nthStats in playerList.items(): # Loop through the dicationary again
                    if nthPlayer != playerName: # We're only interested in the players that AREN'T current player, eg the "nth player". 
                        nthPosX = nthStats[0] # Pulls out nth players stats...
                        nthPosY = nthStats[1]
                        nthInfStatus = nthStats[2]
                        dist = math.hypot((playerPos.x-nthPosX),(playerPos.y-nthPosY)) # Calculates the distance between current player and nth player.  
                        if dist < infDist and nthInfStatus == True: # If its less than some predefined infection distance, and nth player is infected, then bingo the magic can happen.  
                            infOdds = random.randint(0,infDist) # We generate a new random number between 0 and whatever the predefined infection distance is... 
                            if dist < infOdds: # ...and use it to calculate if current player is infected by nth player.  If the distance between current and nth is very large, then the odds are that infOdds will be smaller than it, and thus current player is less likely to be infected.  Likewise, if the distance is very small, its more likely that infOdds will be larger than it, making infection more likely.  This corresponds to the behaviour we want; small distance = more likely to be infected, large distance = less likely.  
                                infStatus = True
                counter = 0
            elif infStatus == False:
                counter += 1
        
            dt = clock.tick(40) / 1000

        pygame.quit()

asyncio.run(interlinked())