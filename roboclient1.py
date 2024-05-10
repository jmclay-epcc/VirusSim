import pygame
import asyncio
import websockets
import InfectionLogic1 as infLog
import random

pygame.init()
uiSize = 150
uiSizeHalf = uiSize/2
boardSize = 500 # This needs to match the board size on the server.  I could set up a web socket to pull this number from the server script but i really dont want to!  
screen = pygame.display.set_mode((uiSize, uiSize))
clock = pygame.time.Clock()
dt = 0

playerPos = pygame.Vector2(375+random.randint(-300,300), 250+random.randint(-200,200))
playerInfo = {}
playerName = infLog.playerName
infStatus = infLog.infStatus
counter = infLog.counter

uri = "ws://localhost:8765"

async def interlinked():
    async with websockets.connect(uri) as websocket:
        global infStatus
        global counter
        global playerPos
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
            text_rect = text_surface.get_rect(center=(uiSizeHalf,uiSizeHalf))
            screen.blit(text_surface, text_rect)
            
            xOffset = random.randint(-1,1) * 15
            yOffset = random.randint(-1,1) * 15
            playerPos.x += xOffset
            playerPos.y += yOffset

            pygame.display.flip()
            
            playerInfo[playerName] = [playerPos.x,playerPos.y,infStatus]

            await websocket.send(str(playerInfo))
            
            response = await websocket.recv()
            playerList = eval(response)
            playerStats = playerList[playerName]
            playerPos = pygame.Vector2(playerStats[0],playerStats[1])
            
            infStatus, counter = infLog.infectionLogicDef(playerList, counter)
        
            dt = clock.tick(30) / 1000

        pygame.quit()

asyncio.run(interlinked())