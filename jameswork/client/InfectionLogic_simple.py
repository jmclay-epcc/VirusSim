# ----- The player should NOT remove anything from this part unless they're very sure what they're doing! -----

import math
import random
import numpy as np

# ----- The player should change the values here (apart from infStatus, should should stay False unless otherwise told), but should not remove any of the variables -----

playerName = "James Mclay"
infStatus = True
virus = "Ringworm"
infDist = 75 # This is a distance in units.  I think the unit is a pixel?  
infStrength = 90 # This is a percentage.  

# ----- These are important to the function of the sim, so should not be touched -----

infCheckTime = 2
counter = random.randint(1,115)
originalVirusName = virus

# ----------

# This is the definition where all of the infection logic goes.  Beyond some specific rules, which are noted in the comments, anything in here can be changed or modifed to your whim.
# When this def is called by client.py, it is provided with the playerList as an argument.  This is a list of the dictionary that contains the following information about every player connected to the server:-

# playerName: posX, posY, infStatus, virus, infDist, infStrength, wallShareCheck

# You can do what you like with this information, or ignore any of it, but bare in mind that legitimate values of infStatus, virus, infDist and infStrength MUST be returned by this def, otherwise client.py crashes.  

def infectionLogicDef(playerList):
    
    global counter
    global originalVirusName
    global infStatus
    global virus
    global infDist
    global infStrength
    
    playerStats = playerList[playerName]
    playerPos = (playerStats[0],playerStats[1]) # The server is able to modify position, infection status and viral character characteristics, so it is a good idea to copy the value provided in the playerList to make sure you're working with your own most up-to-date data.  
    
    infStatus = playerStats[2]
    virus = playerStats[3]
    infDist = playerStats[4]
    infStrength = playerStats[5]
    
    if infStatus == False:
        virus = originalVirusName
    
    if counter >= (infCheckTime * 80) and infStatus == False: # The value of counter increments up by one for every simulation step, which is set to 80 per second by the server.  Since infCheckTime is set to 2 by default, we can see that the script will check to infection whenever the counter reaches 160, or in other words, every two seconds.  
        for nthPlayer, nthStats in playerList.items(): # Loop through the list of players
            if nthPlayer != playerName: # We're only interested in the players that AREN'T current player.  
                nthPosX = nthStats[0] # Pulls out nth players stats
                nthPosY = nthStats[1]
                nthInfStatus = nthStats[2]
                nthVirus = nthStats[3]
                nthInfDist = nthStats[4]
                nthInfStrength = nthStats[5]
                dist = math.hypot((playerPos[0]-nthPosX),(playerPos[1]-nthPosY)) # Calculates the distance between current player and nth player.  
                if dist < nthInfDist and nthInfStatus == True: # If its less than nthInfDist, and nth player is infected, then bingo the magic can happen. 
                    infOdds = (((100-nthInfStrength)/(-dist/2)) * dist) + 100 # This is a (relatively) simple formula that is used to calculate the odds of becoming infected, given nthInfDist, nthInfStrength, and the distance between the player and nth player.  It is a linear relation wherein infOdds always = 100 when dist = 0, and infOdds always = nthInfStrength when dist = nthInfDist/2.  Changing these values changes the odds of infection at any given distance.  
                    # The way that infOdds is calculated is a good place to explore alternate solutions.  You can make this less complicated and less realistic, or almost endlessly more complicated and more realistic.  
                    infOddsCheck = random.randint(0,100) # We generate a new random number between 0 and 100 (with a few decimal points)...                  
                    if infOdds > infOddsCheck: #... And compare it to the infOdds.  If the infOdds is higher than the infOddsCheck, then the player will becoming infected.  
                        infStatus = True # When the player is successfully infected, we don't just want to switch out infStatus variable from False to True.  We also want to copy over the virus characteristics from the player that we were infected by.  This way, when we go on to infected some other player, we pass on the same viral "strain".  
                        virus = nthVirus 
                        infDist = nthInfDist
                        infStrength = nthInfStrength
                        print("You've been infected with",virus,"!")
        counter = 0 # The counter essentially acts as a stopwatch which tells the program to check for infection after it reaches a certain value.  So, once counter has reached that value and performed an infection check, we need to reset it back to zero so that it can start counting back up to the next check.  
    else:
        counter += 1
        
    return infStatus, virus, infDist, infStrength # When this def in called by client.py, it is expecting exactly these four variables to be returned.  No more, and no less.  So do not remove or modify this line.  