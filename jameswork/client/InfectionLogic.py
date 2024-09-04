import math
import random
import numpy as np

playerName = "James Mclay"
infStatus = False
virus = "Ringworm"
infDist = 75 # This is a distance in units.  I think the unit is a pixel?  
infStrength = 90 # This is a percentage.  

infCheckTime = 2
counter = random.randint(1,115)

originalVirusName = virus

def compassDir(nthPlayer, infOdds, nthPosX, nthPosY, playerPos, dist): # This definition is purely for fun, and is an example of what extra functions players could stick on.  It is not needed for the actual sim.  
    if abs(nthPosX - playerPos[0]) >= 50:
        if nthPosX < playerPos[0]:
            xCard = "west"
        elif nthPosX > playerPos[0]:
            xCard = "east"
    elif abs(nthPosX - playerPos[0]) < 50:
        xCard = ""
                    
    if abs(nthPosY - playerPos[1]) >= 50:
        if nthPosY < playerPos[1]:
            yCard = "north"
        elif nthPosY > playerPos[1]:
            yCard = "south"
    elif abs(nthPosY - playerPos[1]) < 50:
        yCard = ""
                    
    print("----------",playerName,"----------")
    print("You current have a", round(infOdds,2),'%', "chance of being infected by",nthPlayer,"!")
    
    if xCard == yCard:
        print(nthPlayer,"is right next to you!") 
    else:
        print(nthPlayer,"is",round(dist,1),"metres away, to your",yCard,xCard) 

def infectionLogicDef(playerList):
    
    global counter
    global originalVirusName
    
    playerStats = playerList[playerName]
    playerPos = (playerStats[0],playerStats[1])
    
    infStatus = playerStats[2]
    virus = playerStats[3]
    infDist = playerStats[4]
    infStrength = playerStats[5]
    
    if infStatus == False:
        virus = originalVirusName
    
    if counter >= (infCheckTime * 80) and infStatus == False:
        # The next chuck of script to see how close every other player in the dictionary is to current player, and then determines if current player can and should be infected by them.  
        for nthPlayer, nthStats in playerList.items(): # Loop through the list of players
            if nthPlayer != playerName: # We're only interested in the players that AREN'T current player, eg the "nth player". 
                nthPosX = nthStats[0] # Pulls out nth players stats...
                nthPosY = nthStats[1]
                nthInfStatus = nthStats[2]
                nthVirus = nthStats[3]
                nthInfDist = nthStats[4]
                nthInfStrength = nthStats[5]
                dist = math.hypot((playerPos[0]-nthPosX),(playerPos[1]-nthPosY)) # Calculates the distance between current player and nth player.  
                if dist < nthInfDist and nthInfStatus == True: # If its less than nthInfDist, and nth player is infected, then bingo the magic can happen.  
                    halfOdds = (0.8*nthInfDist*(nthInfStrength/100)) + 0.1*nthInfDist # halfOdds defines the distance from the player that nth player needs to be to have a 50% chance of becoming infected by them.  This feeds into the Sigmoid curve.  
                    k = ((np.square((nthInfStrength/100)-0.5)/1.25) + 0.05) * (150/nthInfDist) # Broadly speaking, k controls the gradiant on the centre of the Sigmoid curve.  k = 0 makes the line horizontal, while k > infinite makes it vertical.  The reason this isn't just a constant value is because we want it to vary for different infection distances and strengths, in order to get consistent curves.  
                    infOdds = 100 / (1 + np.exp(k*(dist-halfOdds))) # This is the equation of a Sigmoid curve that has a Y-axis range of 0 to 100, and an X-axis range of 0 to nthInfDist.  At dist = 0 the odds of infection are always 100%, at dist = nthInfDist the odds are always 0%, and between this the odds curve smoothly with the dist value required for a 50% chance of being infected being proportional by nthInfStrength.  Higher nthInfStrength, greater dist value needed for 50%, and vis versa.  I got in at 9:30 am today.  It took me until 4:10pm to finalise and tune this solution.  I am not a mathematician.  
                    infOddsCheck = random.randint(0,10000)/100 # We generate a new random number between 0 and 100...
                    
                    compassDir(nthPlayer, infOdds, nthPosX, nthPosY, playerPos, dist)
                        
                    if infOdds > infOddsCheck: #... And compare it to the infOdds that we calculated earlier.  If the player and nth player are very close, infOdds with trend towards towards 100, which means infOddsCheck will be more likely to be lower, which means the player is more likely to be infected.  Vis versa applies.  
                        infStatus = False # When the player is successfully infected, we don't just want to switch out infStatus variable from False to True.  We also want to copy over the virus characteristics from the player that we were infected by.  This way, when we go on to infected some other player, we pass on the same viral "strain".  
                        virus = nthVirus 
                        infDist = nthInfDist
                        infStrength = nthInfStrength
                        print("You've been infected with",virus,"!")
        counter = 0
    else:
        counter += 1
        
    return infStatus, virus, infDist, infStrength