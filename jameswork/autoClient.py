#import pygame
import asyncio
import websockets
import random
import json
import math
import numpy as np
import nltk
from nltk.corpus import words

nltk.download('words')

playerName = random.choice(words.words())
virus = random.choice(words.words())
infDist = random.randint(1,200) # This is a distance in units.  I think the unit is a pixel?  
infStrength = random.randint(0,100) # This is a percentage.  
infCheckTime = 2
counter = random.randint(1,115)
playerPos = [-1000,random.randint(-1000,1000)]
playerDir = [random.randint(-1,1),random.randint(-1,1)]
wallShareCheck = False
playerInfo = {}
wallDefs = []
infStatus = False

playerInfo[playerName] = [playerPos[0],playerPos[1],infStatus,virus,infDist,infStrength,wallShareCheck]

uri = "ws://localhost:8765"

# ----------------

def infectionLogicDef(playerList):
    
    global counter
    global immunity
    
    playerStats = playerList[playerName]
    playerPos = (playerStats[0],playerStats[1])
    
    infStatus = playerStats[2]
    virus = playerStats[3]
    infDist = playerStats[4]
    infStrength = playerStats[5]
        
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
                        
                    if infOdds > infOddsCheck: #... And compare it to the infOdds that we calculated earlier.  If the player and nth player are very close, infOdds with trend towards towards 100, which means infOddsCheck will be more likely to be lower, which means the player is more likely to be infected.  Vis versa applies.  
                        infStatus = True
                        virus = nthVirus
                        infDist = nthInfDist
                        infStrength = nthInfStrength
        counter = 0
    else:
        counter += 1
        
    return infStatus, virus, infDist, infStrength

# ---------------

async def interlinked():
    async with websockets.connect(uri) as websocket:
        global wallDefs
        global playerInfo
        global wallShareCheck
        global playerPos
        global infStatus
        global virus
        global infDist
        global infStrength
        running = True
        
        await websocket.send(json.dumps(playerInfo))
        initialWallShare = await websocket.recv()
        wallDefs = json.loads(initialWallShare)
        wallShareCheck = True
                
        playerRadii = int(wallDefs[1] / 35)
        #walls = [pygame.Rect(wallDefs[2]), # Left border
        #        pygame.Rect(wallDefs[3]), # Top border
        #        pygame.Rect(wallDefs[4]), # Right border
        #        pygame.Rect(wallDefs[5]), # Bottom border
         
        #        pygame.Rect(wallDefs[6]),
        #        pygame.Rect(wallDefs[7]),
        #        pygame.Rect(wallDefs[8]),
        #        pygame.Rect(wallDefs[9]),
        #        pygame.Rect(wallDefs[10]),
        #        pygame.Rect(wallDefs[11]),
        #        pygame.Rect(wallDefs[12]),
        #        pygame.Rect(wallDefs[13])] # And we can do whatever we want with this info >:)
        
        while running:            
            if playerDir[0] == 0:
                playerDir[0] = random.choice([1, -1])
            elif playerDir[1] == 0:
                playerDir[1] = random.choice([1, -1])
            else:
                playerDir[random.choice([0,1])] = 0
                
            baseStep = int(playerRadii * 2/5) 
            if (playerDir[0] == 1 or playerDir[0] == -1) and (playerDir[1] == 1 or playerDir[1] == -1):
                step = math.sqrt((baseStep*baseStep)/2) 
            else:
                step = baseStep
                
            xOffset = playerDir[0] * step
            yOffset = playerDir[1] * step
            playerPos[0] += xOffset
            playerPos[1] += yOffset
            
            playerInfo[playerName] = [playerPos[0],playerPos[1],infStatus,virus,infDist,infStrength,wallShareCheck]
            await websocket.send(json.dumps(playerInfo))
            response = await websocket.recv()
            playerList = json.loads(response)
            playerStats = playerList[playerName]
            playerPos = [playerStats[0],playerStats[1]]
            
            infStatus, virus, infDist,infStrength = infectionLogicDef(playerList)
            
# ----------------

asyncio.run(interlinked())
