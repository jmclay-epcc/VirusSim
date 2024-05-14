import asyncio
import websockets
import pygame
import random

pygame.init()
pygame.display.set_caption('Multi-infstatus modification')
boardWidth = 750
boardHeight = 500
playerRadii = 15
screen = pygame.display.set_mode((boardWidth+500, boardHeight))
clock = pygame.time.Clock()
running = True
playerList = {}
websocketDict = {}

walls = [pygame.Rect(-40, -40, 50, boardHeight+40), # Left border
        pygame.Rect(-40, -40, boardWidth+40, 50), # Top border
        pygame.Rect(boardWidth - 10, 0, 50, boardHeight), # Right border
        pygame.Rect(-40, boardHeight - 10, boardWidth+40, 50), # Bottom border
         
        pygame.Rect(400, 0, 125, 175),
        pygame.Rect(125, boardHeight - 150, 100, 200),
        pygame.Rect(115, 0, 75, 225),
        pygame.Rect(125, 185, 150, 40),
        pygame.Rect(475, boardHeight - 250, 150, 150),
        pygame.Rect(475, boardHeight - 250, 300, 50)]

screen.fill("white")
pygame.display.flip()

async def echo(websocket, path):
    print("Client connected")
    try:
        global running
        global walls
        global playerRadii
        global playerList
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            message = await websocket.recv()
            messageDict = eval(message)
            playerName, playerStats = next(iter(messageDict.items()))
            
            screen.fill("white")
            font = pygame.font.Font(None, playerRadii)         
            for wall in walls:
                pygame.draw.rect(screen, "blue", wall)
            
            for wall in walls:
                if playerStats[0] - playerRadii < wall.right and playerStats[0] + playerRadii > wall.left and playerStats[1] - playerRadii < wall.bottom and playerStats[1] + playerRadii > wall.top: 
                    xFace = min((playerStats[0] + playerRadii - wall.left),(playerStats[0] - playerRadii - wall.right),key=lambda x: abs(x)) # If the player hits the left wall, term 1 will be near 0 and positive, whereas term 2 will be large and negative.  If the player hits the right wall, term 1 will be large a positive, and term 2 will be near 0 and negative.  the abs part beings that this should always return the number closest to zero, so the near-zero positive or negative value.  
                    yFace = min((playerStats[1] + playerRadii - wall.top),(playerStats[1] - playerRadii - wall.bottom),key=lambda x: abs(x)) # This means that when considered together, xFace and yFace encode two pieces of information.  The value that is closer to zero indicates the axis of the wall that the player hit (xFace indicates that the player hit a vertical wall, defined by a value on the x-axis, and vis versa), and the sign on that smaller value indicates the direction of travel (positive for along the axis, negative for against it), and thus the wall that the player hit.  
                    
                    if abs(xFace) < abs(yFace):
                        if xFace > 0:
                            playerStats[0] = wall.left - playerRadii
                        else:
                            playerStats[0] = wall.right + playerRadii
                    else:
                        if yFace > 0:
                            playerStats[1] = wall.top - playerRadii
                        else:
                            playerStats[1] = wall.bottom + playerRadii


            playerList[playerName] = playerStats
            websocketDict[websocket] = playerName
            
            for name, stats in playerList.items():
                
                playerEvoStatus = stats[2]
                if playerEvoStatus == 1:
                    colour = "Red"
                elif playerEvoStatus == 2:
                    colour = "Orange"
                elif playerEvoStatus == 3:
                    colour = "Yellow"
                elif playerEvoStatus == 4:
                    colour = "Green"
                elif playerEvoStatus == 5:
                    colour = "Blue"
                    
                playerPos = [stats[0],stats[1]]
                text_surface = font.render(name, True, "black")
                text_rect = text_surface.get_rect(center=playerPos)
                pygame.draw.circle(screen, colour, playerPos, playerRadii)
                screen.blit(text_surface, text_rect)
            pygame.display.flip()

            await websocket.send(str(playerList))
    except Exception as e:
        print("Client error - ",e)
        errorPlayer = websocketDict[websocket]
        del playerList[errorPlayer]
        print("Client Disconnected")

async def main():
    # Start the WebSocket server on localhost at port 8765
    async with websockets.serve(echo, "localhost", 8765):
        print("WebSocket server started on ws://localhost:8765")
        # Keep the event loop running indefinitely
        while running:
            await asyncio.sleep(0.01)  # Sleep briefly to allow other tasks to run
            pygame.event.pump()  # Manually handle Pygame events
            clock.tick(30)

# Run the main coroutine
asyncio.run(main())