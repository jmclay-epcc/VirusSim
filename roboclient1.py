import pygame
import asyncio
import websockets
import InfectionLogic1 as infLog

pygame.init()
uiSize = 300
uiSizeHalf = uiSize/2
screen = pygame.display.set_mode((uiSize, uiSize))
clock = pygame.time.Clock()
dt = 0

playerPos = pygame.Vector2(250, 250)
playerInfo = {}
playerName = infLog.playerName
infStatus = infLog.infStatus
counter = infLog.counter

uri = "ws://localhost:8765"

async def interlinked():
    async with websockets.connect(uri) as websocket:
        global infStatus
        global counter
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
            
            font = pygame.font.Font(None, 35)
            text_surface = font.render(status, True, "white")
            text_rect = text_surface.get_rect(center=(uiSizeHalf,uiSizeHalf))
            screen.blit(text_surface, text_rect)

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
            
            playerInfo[playerName] = [playerPos.x,playerPos.y,infStatus]

            await websocket.send(str(playerInfo))
            
            response = await websocket.recv()
            playerList = eval(response)
            
            infStatus, counter = infLog.infectionLogicDef(playerList, counter)
        
            dt = clock.tick(30) / 1000

        pygame.quit()

asyncio.run(interlinked())