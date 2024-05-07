# Example file showing a circle moving on screen
import pygame
import random
import math

# pygame setup
pygame.init()

boardSize = 300
playerSpread = (boardSize/2) - round(boardSize/10)
screen = pygame.display.set_mode((boardSize, boardSize))
clock = pygame.time.Clock()
running = True
dt = 0
fps = 60
playerNum = 20
playerList = {}
infDist = round(boardSize/10)
infCheckTime = 0.5 # A player that is infected will only check for other infected player near by once every this seconds.  

infStatus = False # Initial infection status for all players

for i in range(playerNum):
    playerName = f"player{i}"

    # In the future, the value arrays recorded in this dictionary would be provided by the players.  
    pos = pygame.Vector2((screen.get_width()/2) + random.randint(playerSpread * -1,playerSpread), (screen.get_height() / 2) + random.randint(playerSpread * -1,playerSpread))

    if i == 13: # This if statement places a single infected player in the herd - player 13.  Unlucky.  BOO! .  
        infStatus = True;
    else:
        infStatus = False;
    
    counter = random.randint(10,50*infCheckTime) # The purpose of the counter is to make it so that players don't check for infected players on every frame.  Instead, each players counter will tick up by one every frame, and then the infection check will run when it hits, say, 500.  We give it a random initial value so that every player isn't checking on the same frame.  
    
    playerList[i] = [pos,infStatus,counter]



while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")
    keys = pygame.key.get_pressed()

    for player, stats in playerList.items(): # This for loop runs through each player in the player list, colours it depending on its infection status, moves it, and then later check if it should be infected by another nearby player.  I am going to call this player "current player" in future comments.  
        #This if statement controls changes about a players attributes when they are sick or healthy.  
        infStatus = stats[1] # Pulling the infection status out of the definiton array...
        if infStatus == True:
            colour = "red"
        elif infStatus == False:
            colour = "green"

        pos = stats[0] # ...And pulling out the position.  
        pygame.draw.circle(screen, colour, pos, 10)

        # This sets current player off on a random walk.  We'd replace this with direct player controls in the final sim.  
        xOffset = random.randint(-1,1) * 5
        yOffset = random.randint(-1,1) * 5
        newX = xOffset + pos.x
        newY = yOffset + pos.y

        if newY <= boardSize and newY >= 0:
            pos.y = newY
        if newX <= boardSize and newX >= 0:
            pos.x = newX

        counter = stats[2]

        if infStatus == False and counter == (infCheckTime * fps):
            # The next chuck of script to see how close every other player in the dictionary is to current player, and then determines if current player can and should be infected by them.  I find it quite confusing - for loops inside for loops.  
            for nthPlayer, nthStats in playerList.items(): # Loop through the dicationary again
                if nthPlayer != player: # We're only interested in the players that AREN'T current player, eg the "nth player". 
                    nthPos = nthStats[0] # Pulls out nth players stats...
                    nthInfStatus = nthStats[1]
                    dist = math.hypot((pos.x-nthPos.x),(pos.y-nthPos.y)) # Calculates the distance between current player and nth player.  
                    if dist < infDist and nthInfStatus == True: # If its less than some predefined infection distance, and nth player is infected, then bingo the magic can happen.  
                        infOdds = random.randint(0,infDist) # We generate a new random number between 0 and whatever the predefined infection distance is... 
                        if dist < infOdds: # ...and use it to calculate if current player is infected by nth player.  If the distance between current and nth is very large, then the odds are that infOdds will be smaller than it, and thus current player is less likely to be infected.  Likewise, if the distance is very small, its more likely that infOdds will be larger than it, making infection more likely.  This corresponds to the behaviour we want; small distance = more likely to be infected, large distance = less likely.  
                            infStatus = True
            counter = 0
        elif infStatus == False:
            counter += 1

        stats[1] = infStatus # And this final line saves the updated
        stats[2] = counter


    # ----- For loop ends here -----

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(fps) / 1000

# Note to yourself: When a new frame is drawn, everything within "while running" is run again.  It is essentially a time loop that you don't need to set up yourself.   
# dt is the time in seconds that each frame appears on screen.  So, when we see lines like this:-
# (when pressing w) player_pos.y += 300 * dt 
# What that is really saying is that the x value will increment up by some fraction of 300 (300*dt) such that, after 1 second of w being held down, the value will have gone up by 300.  
# If we didn't include that *dt, and just put += 300, then the value would increase by 300 every frame.  At 60 FPS, thats 18000 pixels a second.  Bad!

pygame.quit()