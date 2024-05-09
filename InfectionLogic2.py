import math
import random

playerName = "K. Dot"
infCheckTime = 2
infDist = 75
counter = 12
infStatus = False

def infectionLogicDef(playerList, counter):
    
    playerStats = playerList[playerName]
    playerPos = (playerStats[0],playerStats[1])
    infStatus = playerStats[2]
    
    if infStatus == False and counter >= (infCheckTime * 30):
        # The next chuck of script to see how close every other player in the dictionary is to current player, and then determines if current player can and should be infected by them.  I find it quite confusing - for loops inside for loops.  
        for nthPlayer, nthStats in playerList.items(): # Loop through the dicationary again
            if nthPlayer != playerName: # We're only interested in the players that AREN'T current player, eg the "nth player". 
                nthPosX = nthStats[0] # Pulls out nth players stats...
                nthPosY = nthStats[1]
                nthInfStatus = nthStats[2]
                dist = math.hypot((playerPos[0]-nthPosX),(playerPos[1]-nthPosY)) # Calculates the distance between current player and nth player.  
                if dist < infDist and nthInfStatus == True: # If its less than some predefined infection distance, and nth player is infected, then bingo the magic can happen.  
                    print("I AM IN DANGER OF BEING INFECTED!")
                    infOdds = random.randint(0,infDist) # We generate a new random number between 0 and whatever the predefined infection distance is... 
                    if dist < infOdds: # ...and use it to calculate if current player is infected by nth player.  If the distance between current and nth is very large, then the odds are that infOdds will be smaller than it, and thus current player is less likely to be infected.  Likewise, if the distance is very small, its more likely that infOdds will be larger than it, making infection more likely.  This corresponds to the behaviour we want; small distance = more likely to be infected, large distance = less likely.  
                        infStatus = True
        counter = 0
    elif infStatus == False:
        counter += 1
        
    return infStatus, counter