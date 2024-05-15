import math
import random

playerName = "James Mclay"
infCheckTime = 2
counter = 12

infStatus = False
virus = "Shrinking Sickness"
infDist = 100

def infectionLogicDef(playerList, counter):
    
    playerStats = playerList[playerName]
    playerPos = (playerStats[0],playerStats[1])
    
    infStatus = playerStats[2]
    virus = playerStats[3]
    infDist = playerStats[4]
    
    if infStatus == False and counter >= (infCheckTime * 30):
        # The next chuck of script to see how close every other player in the dictionary is to current player, and then determines if current player can and should be infected by them.  
        for nthPlayer, nthStats in playerList.items(): # Loop through the list of players
            if nthPlayer != playerName: # We're only interested in the players that AREN'T current player, eg the "nth player". 
                nthPosX = nthStats[0] # Pulls out nth players stats...
                nthPosY = nthStats[1]
                nthInfStatus = nthStats[2]
                nthVirus = nthStats[3]
                nthInfDist = nthStats[4]
                dist = math.hypot((playerPos[0]-nthPosX),(playerPos[1]-nthPosY)) # Calculates the distance between current player and nth player.  
                if dist < nthInfDist and nthInfStatus == True: # If its less than some predefined infection distance, and nth player is infected, then bingo the magic can happen.  
                    print("----------",playerName,"----------")
                    print("You current have a", round((nthInfDist-dist)*100/nthInfDist, 2),'%', "chance of being infected by",nthPlayer,"!")
                    infOdds = random.randint(0,nthInfDist) # We generate a new random number between 0 and whatever the predefined infection distance is... 
                    if dist < infOdds: # ...and use it to calculate if current player is infected by nth player.  If the distance between current and nth is very large, then the odds are that infOdds will be smaller than it, and thus current player is less likely to be infected.  Likewise, if the distance is very small, its more likely that infOdds will be larger than it, making infection more likely.  This corresponds to the behaviour we want; small distance = more likely to be infected, large distance = less likely.  
                        infStatus = True
                        virus = nthVirus
                        infDist = nthInfDist
                        print("You've been infected with",virus,"!  This virus has a range of",infDist)
        counter = 0
    elif infStatus == False:
        counter += 1
        
    return infStatus, virus, infDist, counter