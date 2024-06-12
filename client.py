import pygame
import asyncio
import websockets
import InfectionLogic as infLog
import random
import json

pygame.init()
uiSize = 300
uiSizeHalf = uiSize/2
screen = pygame.display.set_mode((uiSize, uiSize+50))
clock = pygame.time.Clock()

playerPos = pygame.Vector2(375+random.randint(-300,300), 250+random.randint(-200,200))
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
            if keys[pygame.K_UP]:
                playerPos.y -= 7
                upCol = "blue"
            else:
                upCol = "gray"
            if keys[pygame.K_DOWN]:
                playerPos.y += 7
                downCol= "blue"
            else:
                downCol = "gray"
            if keys[pygame.K_LEFT]:
                playerPos.x -= 7
                leftCol = "blue"
            else:
                leftCol = "gray"
            if keys[pygame.K_RIGHT]:
                playerPos.x += 7
                rightCol = "blue"
            else:
                rightCol = "gray"

            pygame.display.flip()
            
            playerInfo[playerName] = [playerPos.x,playerPos.y,infStatus,virus,infDist,infStrength]

            await websocket.send(json.dumps(playerInfo))
            
            response = await websocket.recv()
            playerList = json.loads(response)
            playerStats = playerList[playerName]
            playerPos = pygame.Vector2(playerStats[0],playerStats[1])
            
            infStatus, virus, infDist,infStrength,counter = infLog.infectionLogicDef(playerList, counter)

        pygame.quit()

asyncio.run(interlinked())