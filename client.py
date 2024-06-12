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
            
            baseStep = 10 # As is probably quite clear, the player moves by making a step along the X axis, Y axis, or box axis, each frame.  If this step was constant, then the player would end up moving a greater distance when travelling diagonally (if they player held down up and left, the player would move 10 pixels up, 10 left, and ultimately about 14 diagonally).  We want the player to make the same sized step every frame regardless of direction, so we correct the step size based on what keys are being held down here.  
            if sum(keys) == 2: # Thats a long way of saying im using pythagoras to make sure the player always moves the same distance per frame regardless of direction.  
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
            
            playerInfo[playerName] = [playerPos[0],playerPos[1],infStatus,virus,infDist,infStrength]

            await websocket.send(json.dumps(playerInfo))
            
            response = await websocket.recv()
            playerList = json.loads(response)
            playerStats = playerList[playerName]
            playerPos = [playerStats[0],playerStats[1]]
            
            infStatus, virus, infDist,infStrength,counter = infLog.infectionLogicDef(playerList, counter)

        pygame.quit()

asyncio.run(interlinked())