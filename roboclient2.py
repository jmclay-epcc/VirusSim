import pygame
import asyncio
import websockets
import InfectionLogic2 as infLog
import random

pygame.init()
uiSize = 150
uiSizeHalf = uiSize/2
screen = pygame.display.set_mode((uiSize, uiSize))
clock = pygame.time.Clock()
dt = 0

playerPos = pygame.Vector2(375+random.randint(-300,300), 250+random.randint(-200,200))
playerInfo = {}
playerName = infLog.playerName
evoStatus = infLog.evoStatus
hand = infLog.hand

uri = "ws://localhost:8765"

async def interlinked():
    async with websockets.connect(uri) as websocket:
        global evoStatus
        global playerPos
        global hand
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
            
            if evoStatus == 1:
                status = "Pion"
            elif evoStatus == 2:
                status = "Serf"
            elif evoStatus == 3:
                status = "Apprentice"
            elif evoStatus == 4:
                status = "Master"
            elif evoStatus == 5:
                status = "King"
            
            font = pygame.font.Font(None, 27)
            text_surface = font.render(status, True, "white")
            text_rect = text_surface.get_rect(center=(uiSizeHalf,uiSizeHalf))
            screen.blit(text_surface, text_rect)
            
            xOffset = random.randint(-1,1) * 5
            yOffset = random.randint(-1,1) * 5
            playerPos.x += xOffset
            playerPos.y += yOffset

            pygame.display.flip()
            
            playerInfo[playerName] = [playerPos.x,playerPos.y,evoStatus,hand]

            await websocket.send(str(playerInfo))
            
            response = await websocket.recv()
            playerList = eval(response)
            playerStats = playerList[playerName]
            playerPos = pygame.Vector2(playerStats[0],playerStats[1])
            
            evoStatus, hand = infLog.infectionLogicDef(playerList)
        
            dt = clock.tick(30) / 1000

        pygame.quit()

asyncio.run(interlinked())