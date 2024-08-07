import pygame
import asyncio
import websockets
import InfectionLogic as infLog
import random
import json
import math

pygame.init()
uiSize = 300
uiSizeHalf = uiSize/2
screen = pygame.display.set_mode((uiSize, uiSize+50))
clock = pygame.time.Clock()

playerPos = [-1000,random.randint(-1000,1000)]
wallShareCheck = False

playerName = infLog.playerName
infStatus = infLog.infStatus
virus = infLog.virus
infDist = infLog.infDist
infStrength = infLog.infStrength

playerInfo = {}
wallDefs = []

playerInfo[playerName] = [playerPos[0],playerPos[1],infStatus,virus,infDist,infStrength,wallShareCheck]

pygame.display.set_caption(playerName)
uri = "ws://localhost:8765"

async def interlinked():
    async with websockets.connect(uri) as websocket:
        global wallDefs
        global playerInfo
        global wallShareCheck
        global playerPos
        global infStatus
        global virus
        global infDist
        global infStrength
        running = True
        upCol = "gray"
        downCol = "gray"
        leftCol = "gray"
        rightCol = "gray"
        
        await websocket.send(json.dumps(playerInfo))
        initialWallShare = await websocket.recv()
        wallDefs = json.loads(initialWallShare)
        wallShareCheck = True
                
        playerRadii = int(wallDefs[1] / 35)

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
                pygame.Rect(wallDefs[13])] # And we can do whatever we want with this info >:)
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill("purple")
            pygame.draw.circle(screen, upCol, (uiSizeHalf,uiSizeHalf-75), 20) # up arrow
            pygame.draw.circle(screen, downCol, (uiSizeHalf,uiSizeHalf+75), 20) # down arrow
            pygame.draw.circle(screen, leftCol, (uiSizeHalf-75,uiSizeHalf), 20) # left arrow
            pygame.draw.circle(screen, rightCol, (uiSizeHalf+75,uiSizeHalf), 20) # right arrow
            
            if infStatus == False:
                status = "Healthy :)"
            else:
                status = "Infected!"
            
            font = pygame.font.Font(None, 27)
            text_surface = font.render(status, True, "white")
            text_rect = text_surface.get_rect(center=(uiSizeHalf,uiSize))
            screen.blit(text_surface, text_rect)

            keys = pygame.key.get_pressed()
            
            baseStep = int(playerRadii * 2/5) # This makes sure that the speed of the player is always proportional to its radii.  
            if sum(keys) == 2:  
                step = math.sqrt((baseStep*baseStep)/2) 
            else:
                step = baseStep
            
            if keys[pygame.K_LEFT]:
                playerPos[0] -= step
                leftCol = "blue"
            else:
                leftCol = "gray"
            if keys[pygame.K_RIGHT]:
                playerPos[0] += step
                rightCol = "blue"
            else:
                rightCol = "gray"
            if keys[pygame.K_UP]:
                playerPos[1] -= step
                upCol = "blue"
            else:
                upCol = "gray"
            if keys[pygame.K_DOWN]:
                playerPos[1] += step
                downCol= "blue"
            else:
                downCol = "gray"

            pygame.display.flip()
            
            playerInfo[playerName] = [playerPos[0],playerPos[1],infStatus,virus,infDist,infStrength,wallShareCheck]
            await websocket.send(json.dumps(playerInfo))
            response = await websocket.recv()
            playerList = json.loads(response)
            playerStats = playerList[playerName]
            playerPos = [playerStats[0],playerStats[1]]
            
            infStatus, virus, infDist,infStrength = infLog.infectionLogicDef(playerList)

        pygame.quit()

asyncio.run(interlinked())