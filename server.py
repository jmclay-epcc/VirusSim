import asyncio
import websockets
import pygame

pygame.init()
boardSize = 500
screen = pygame.display.set_mode((boardSize, boardSize))
clock = pygame.time.Clock()
running = True
playerList = {}

screen.fill("white")
pygame.display.flip()

async def echo(websocket, path):
    print("Client connected")
    try:
        global running
        while running:
            # Handle pygame events manually
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            message = await websocket.recv()
            messageDict = eval(message)
            playerName, playerStats = next(iter(messageDict.items()))
            
            if playerStats[0] > boardSize:
                playerStats[0] = boardSize
            if playerStats[0] < 0:
                playerStats[0] = 0
            if playerStats[1] > boardSize:
                playerStats[1] = boardSize
            if playerStats[1] < 0:
                playerStats[1] = 0
                
            playerList[playerName] = playerStats
            
            screen.fill("white")
            
            for name, stats in playerList.items():
                
                playerInfStatus = stats[2]
                if playerInfStatus == True:
                    colour = "Red"
                else:
                    colour = "green"
                    
                playerPos = [stats[0],stats[1]]
                pygame.draw.circle(screen, colour, playerPos, 20)

            pygame.display.flip()

            await websocket.send(str(playerList))
    except websockets.exceptions.ConnectionClosedError:
        print("Client disconnected")

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