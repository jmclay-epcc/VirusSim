import pygame
import pandas as pd
import os

def is_file_in_use(file_path):
    try:
        with open(file_path, 'r') as file:
            return False  # File is not in use
    except IOError:
        return True  # File is in use

# pygame setup
pygame.init()
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()
running = True
dt = 0
playerName = "player0"

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Loads in the player detail spreadsheet and pulls the players stats from it.  
    if is_file_in_use('playerList.csv') == False:
        df = pd.read_csv('playerList.csv', header=None)
        playerList = df.set_index(df.columns[0]).agg(list, axis=1).to_dict()

        stats = playerList[playerName]
        posX = stats[0]
        posY = stats[1]
        infStatus = stats[2]
        counter = stats[3]

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("purple")

        pygame.draw.circle(screen, "blue", pygame.Vector2(posX,posY), 40)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            posY -= 5
        if keys[pygame.K_s]:
            posY += 5
        if keys[pygame.K_a]:
            posX -= 5
        if keys[pygame.K_d]:
            posX += 5

        stats[0] = int(posX) # I don't know if these are STRICTLY nessesary in this case, but i'll out them here for now.  
        stats[1] = int(posY)
        stats[2] = infStatus
        stats[3] = counter

        playerList[playerName] = stats

        df = pd.DataFrame.from_dict(playerList, orient='index')
        df.to_csv('playerList.csv', header=None)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(15) / 1000 # This doesn't really need to be high-fps.  It probably doesn't even need to be pygame.  

pygame.quit()