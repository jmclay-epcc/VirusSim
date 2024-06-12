import pygame
import asyncio
import websockets
import InfectionLogic1 as infLog
import random
import json

pygame.init()
uiSize = 150
uiSizeHalf = uiSize/2
screen = pygame.display.set_mode((uiSize+150, uiSize))
clock = pygame.time.Clock()
dt = 0

playerPos = [-1000,random.randint(-1000,1000)]
playerInfo = {}
playerName = infLog.playerName
counter = infLog.counter

infStatus = infLog.infStatus
virus = infLog.virus
infDist = infLog.infDist
infStrength = infLog.infStrength

pygame.display.set_caption(playerName)
uri = "ws://localhost:8765"

async def interlinked():
    async with websockets.connect(uri) as websocket:
        global counter
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
            text_rect = text_surface.get_rect(center=(uiSizeHalf+75,uiSizeHalf))
            screen.blit(text_surface, text_rect)

            xOffset = random.randint(-1,1) * 7
            yOffset = random.randint(-1,1) * 7
            playerPos[0] += xOffset
            playerPos[1] += yOffset

            pygame.display.flip()
            
            playerInfo[playerName] = [playerPos[0],playerPos[1],infStatus,virus,infDist,infStrength]

            await websocket.send(json.dumps(playerInfo))
            
            response = await websocket.recv()
            playerList = json.loads(response)
            playerStats = playerList[playerName]
            playerPos = [playerStats[0],playerStats[1]]
            
            infStatus, virus, infDist,infStrength,counter = infLog.infectionLogicDef(playerList, counter)

        pygame.quit()

asyncio.run(interlinked())