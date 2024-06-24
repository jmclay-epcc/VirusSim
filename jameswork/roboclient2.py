import pygame
import asyncio
import websockets
import InfectionLogic2 as infLog
import random
import json

pygame.init()
uiSize = 300
uiSizeHalf = uiSize/2
screen = pygame.display.set_mode((uiSize, uiSizeHalf))
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
                
        playerRadii = int(wallDefs[1] / (100/3))

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
            
            if infStatus == False:
                status = "Healthy :)"
            else:
                status = "Infected!"
            
            font = pygame.font.Font(None, 27)
            text_surface = font.render(status, True, "white")
            text_rect = text_surface.get_rect(center=(uiSizeHalf,uiSizeHalf/2))
            screen.blit(text_surface, text_rect)
            
            xOffset = random.randint(-1,1) * 7
            yOffset = random.randint(-1,1) * 7
            playerPos[0] += xOffset
            playerPos[1] += yOffset

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