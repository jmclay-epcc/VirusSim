#import pygame
import asyncio
import websockets
import random
import json
import math
import numpy as np
import nltk
from nltk.corpus import words
import matplotlib.pyplot as plt

nltk.download('words')

playerName = random.choice(words.words())
virus = random.choice(words.words())
infDist = random.randint(1,200) # This is a distance in units.  I think the unit is a pixel?  
infStrength = random.randint(0,100) # This is a percentage.  
infCheckTime = 2
counter = random.randint(1,115)
playerPos = [300,900]
playerDir = [random.randint(-1,1),random.randint(-1,1)]
wallShareCheck = False
playerInfo = {}
wallDefs = []
infStatus = True

originalVirusName = virus 
playerInfo[playerName] = [playerPos[0],playerPos[1],infStatus,virus,infDist,infStrength,wallShareCheck]

uri = "ws://localhost:8765"

# ----------------

def infectionLogicDef(playerList):
    
    global counter
    
    playerStats = playerList[playerName]
    playerPos = (playerStats[0],playerStats[1])
    
    infStatus = playerStats[2]
    virus = playerStats[3]
    infDist = playerStats[4]
    infStrength = playerStats[5]
    
    if infStatus == False and virus != originalVirusName: # When a player is infected, the virus name that the player enters at the start with is overwritten with the name of the virus that infected them (we do this so that when the player goes on to infect others, the right virus name is transfered).  As a result, if the player is cured and then is made a patient-zero by the GM, they retain the name of the virus that they were infected by rather than the name the player entered.  So, to combat this, we make a copy of the players original virus name and use it to correct the virus name when appropriate (when the player is uninfected and virus != originalVirusName, which only ever happens in the previously described scenario).  
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
                        
                    if infOdds > infOddsCheck: #... And compare it to the infOdds that we calculated earlier.  If the player and nth player are very close, infOdds with trend towards towards 100, which means infOddsCheck will be more likely to be lower, which means the player is more likely to be infected.  Vis versa applies.  
                        infStatus = True
                        virus = nthVirus
                        infDist = nthInfDist
                        infStrength = nthInfStrength
        counter = random.randint(1,115)
    else:
        counter += 1
        
    return infStatus, virus, infDist, infStrength

# ---------------

def pathFinder(playerPos, targetPos, xWalls, yWalls):
    
    def magiciansStaff(testPoint, TPCount):
        newTestPoints = []
        for i in range(int(TPCount/2)):
            intersects = []
            intersectsSetTwo = []
            m = math.tan(math.radians(i*(math.ceil(360/TPCount)))) + 0.1 # These numbers might seem arbitrary and weird, 17 steps of 11 degrees?  Well, if you do this, you can cover the full 360 without hitting values that produce infinite gradients (remember, for every angle step here we are actually returning two legitimate test points.  The magicians staff has two ends :) ).  
            c = -(m*testPoint[0] - testPoint[1])
            for wall in xWalls:
                possibleIntersectY = m*wall[0] + c # The formula of a line given the gradient, c, and X
                if possibleIntersectY >= wall[1] and possibleIntersectY <= wall[2]:
                    realIntersect = (wall[0],possibleIntersectY)
                    intersects.append(realIntersect)
            for wall in yWalls:
                possibleIntersectX = (wall[0] - c)/m # The formula of a line given the gradient, c, and Y.  I think.  I did it in my head, it could be wrong IDFK
                if possibleIntersectX >= wall[1] and possibleIntersectX <= wall[2]:
                    realIntersect = (possibleIntersectX, wall[0])
                    intersects.append(realIntersect)

            nearestIDist = 500000
            secondNearestIDist = 500000
            for point in intersects:
                dist = math.hypot((testPoint[0]-point[0]),(testPoint[1]-point[1]))
                if dist < nearestIDist:
                    nearestIDist = dist
                    nearestI = point # The nearest intersect to the test point will always be the first wall that the hypothetical magicians staff hits.  The difficulty comes after this - we want the positions of the first two walls that the staff hits, however the second nearest intersect might well just be the other side of the first wall, which we are not interested in.  
            for point in intersects: # So here what we're doing is checking if nearestI lies between the testPoint and any of the other intersects.  If it DOESN'T, then we know that this newly found intersect cannot possibly be on the "other side" from the testPoints point of view, which is good because we are not interested in any of those points.  THis leaves us with a new set of intersects which definitely contains the second of the first two walls that the magicians staff hits, this being the one that is nearest to the testPoint.  
                betweenX = min(testPoint[0], point[0]) <= nearestI[0] <= max(testPoint[0], point[0])
                betweenY = min(testPoint[1], point[1]) <= nearestI[1] <= max(testPoint[1], point[1])
            
                if betweenX == False and betweenY == False:
                    intersectsSetTwo.append(point)
        
            for point in intersectsSetTwo:
                dist = math.hypot((testPoint[0]-point[0]),(testPoint[1]-point[1]))
                if dist < secondNearestIDist:
                    secondNearestIDist = dist
                    secondNearestI = point
                
            newTestPoints.append(nearestI)
            newTestPoints.append(secondNearestI)
        return newTestPoints
        #Otuers Nose: the vast majority of this point-finding logic worked first time, without any visual testing, perfectly.  I am very smug about that.  
        
        
    def magicMissile(playerTPList,targetTPList,playerPos,targetPos):
        
        def xWallChecker(playerTP,targetTP):
            if targetTP[0] == playerTP[0]:
                m = 1000000 # If both the players and targets y values are the same (e.g. the TPs are landing on the same vertical wall) then the gradient will be infinite.  I am substituting this with a very larger number.  
            else:
                m = (targetTP[1] - playerTP[1])/(targetTP[0]-playerTP[0])
            c = -(m*targetTP[0] - targetTP[1])
            
            for wall in xWalls:
                betweenX = min(playerTP[0], targetTP[0]) <= wall[0] <= max(playerTP[0], targetTP[0]) # We check to see if any x-walls lie between the X values of the current playerTP and targetTP.  Since we have not yet considered the y-axis limits of the walls, this will pretty much always return True, but if by some chance it doesnt then we know there must be a clear path on the X-axis.  
                if betweenX == True and playerTP[0] != targetTP[0]:
                    y = m*wall[0] + c # We calculate the y-value of the intersection between the wall and the line between the player and target TPs...
                    withinWallLims = min(wall[1], wall[2]) <= y <= max(wall[1], wall[2]) # ... And then check if this lies between the limits of the wall.  If it does, then this wall blocks the path.  
                    if withinWallLims == True:
                        return False
            return True
                        
        def yWallChecker(playerTP,targetTP):
            if targetTP[0] == playerTP[0]:
                m = 1000000
            else:
                m = (targetTP[1] - playerTP[1])/(targetTP[0]-playerTP[0])
                if m == 0:
                    m = 0.01 # IF the player and target PTs x values are the same (e.g. they lie on the same horizontal wall), then the gradient will be 0.  This is not a problem for checking the x walls, but it is for the y walls, so i am just manually correcting it to a tiny value. It introduces a small error but clears up a massive headache.  
            c = -(m*targetTP[0] - targetTP[1])
            for wall in yWalls:
                betweenY = min(playerTP[1], targetTP[1]) <= wall[0] <= max(playerTP[1], targetTP[1])
                if betweenY == True and playerTP[1] != targetTP[1]:
                    x = (wall[0] - c)/m
                    withinWallLims = min(wall[1], wall[2]) <= x <= max(wall[1], wall[2])
                    if withinWallLims == True:
                        return False
            return True
        
        furthestPlayerTPDist = -1
        bestTPDist = 50000 # Im getting myself brain-tied here.  The bestTP is being to be the playerTP that is the closest to a targetTP that it has a clear line of sight to.  So bestTPDist will be the distance between the playerTP and the targetTP, and we want this to be as small as possible.  
            
        clearPathX = xWallChecker(playerPos,targetPos)
        clearPathY = yWallChecker(playerPos,targetPos)
        
        if clearPathX == True and clearPathY == True:
            return targetPos # If the player has a clear line of sight to the target, then we really don't want to piss around with checking and moving towards any test points - we can just move right to the target.  
        
        for playerTP in playerTPList:
            dist1 = math.hypot((playerTP[0]-playerPos[0]),(playerTP[1]-playerPos[1])) # This is the distance between the player and the current playerTP.  We want to keep track of which playerTP has the largest value here.  
            if dist1 > furthestPlayerTPDist:
                furthestPlayerTPDist = dist1
                furthestPlayerTP = playerTP
            for targetTP in targetTPList:
                clearPathX = xWallChecker(playerTP,targetTP)
                clearPathY = yWallChecker(playerTP,targetTP)
                                    
                if clearPathX == True and clearPathY == True:
                    dist2 = math.hypot((playerTP[0]-targetTP[0]),(playerTP[1]-targetTP[1])) # this is the distance between the current playerTP and the current targetTP.  We want to keep track of the playerTP with the smallest value here.  
                    if dist2 < bestTPDist:
                        bestTPDist = dist2
                        bestTP = playerTP
                        
        if bestTPDist == 50000:       
            return furthestPlayerTP # If we aren't able to identify a playerTP with a clear line of sight to either the target or a targetTP, then we will return this value by default.  This should at the very least coax the player into a more favorable map position (logically i think it should push them towards the centre but im more than expecting there to be some edge-case where it gets wedged in a corner or something).  
        else:
            return bestTP # If we are able to identify one or more playerTPs with a clear line of sight to a targetTP, we will return the playerTP value with the shortest distance between it and its targetTP.  
    
    
    targetTestPoints = magiciansStaff(targetPos, 22) # The number here should REALLY be a 2* a prime.  Its just better that way. 
    playerTestPoints = magiciansStaff(playerPos, 22)
    
    bestTP = magicMissile(playerTestPoints,targetTestPoints,playerPos,targetPos)

    ax.cla()
    
    for point in targetTestPoints:
        ax.scatter(point[0], point[1], color = 'r')
        ax.scatter(targetPos[0], targetPos[1], color = 'y', marker = '*')
        
    for point in playerTestPoints:
        ax.scatter(point[0], point[1], color = 'b')
        ax.scatter(playerPos[0], playerPos[1], color = 'g', marker = '*')
        
    ax.scatter(bestTP[0], bestTP[1], color = 'gold', s = 100)
        
    ax.set_xlim(0,1800)
    ax.set_ylim(1000,0)
        
    plt.draw() # This plot gives us i think the third unique method of visualising the playable area that ive created in this project so far - a scatter plot that shows the location of a given player, and a point-cloud of the walls that they can "see".  
    
    plt.pause(1/79)
    
    return bestTP

# ---------------

def chase(playerList, xWalls, yWalls, playerRadii):

    playerStats = playerList[playerName]
    playerPos = (playerStats[0],playerStats[1])
    
    lowestDist = 50000
    for nthPlayer, nthStats in playerList.items():
        if nthPlayer != playerName:
            nthPosX = nthStats[0]
            nthPosY = nthStats[1]
            nthInfStatus = nthStats[2]
            dist = math.hypot((playerPos[0]-nthPosX),(playerPos[1]-nthPosY))
            if dist < lowestDist and nthInfStatus == False:
                lowestDist = dist
                targetPos = [nthStats[0],nthStats[1]]
    if lowestDist == 50000:
        return (0,0) # If there are no uninfected players in the map, then we skip all the pathfinding bullshit and just tell the autoClient not to move at all.  

    pathfinderPos = pathFinder(playerPos, targetPos, xWalls, yWalls) # These are the co-ordinates of either the target, a point that has a direct line of sight to both the player and the target, or a point tht has direct line of sight to the player and to another point that has direct line of sight to the target.  Or, in the worst case, a point that is just sufficently far away from the player (repeated moves in this direction should trend the player towards the centre of the map but hell what do i know)

    
    pfXYDist = (pathfinderPos[0]-playerPos[0],pathfinderPos[1]-playerPos[1]) # The X and Y displacement between the player and the pathfinder target.  
    pfDist = math.hypot(pfXYDist[0],pfXYDist[1]) + 0.1 # The direct distance between the player and the pathfinder target.  
    playerDir = ((pfXYDist[0]/pfDist),(pfXYDist[1]/pfDist)) # The X and Y displacement between the player and the pathfinder target normalised so that the direct distance is one.  We can now feed this value directly into the player so make them move towards the target.  
 
    return playerDir

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
        xWalls = []
        yWalls = []
                
        playerRadii = int(wallDefs[1] / 35)
        walls = [(wallDefs[2]), # Left border
                (wallDefs[3]), # Top border
                (wallDefs[4]), # Right border
                (wallDefs[5]), # Bottom border
         
                (wallDefs[6]),
                (wallDefs[7]),
                (wallDefs[8]),
                (wallDefs[9]),
                (wallDefs[10]),
                (wallDefs[11]),
                (wallDefs[12]),
                (wallDefs[13])]
        
        for wall in walls:  # So the point of this function is to break the walls list up into two lists of vertical and horizontal wall edges.  These edges are represented in the lists as their X or Y coordinate, and the Y or X co-ordinates that define the edges ends.  Using this we can hopefully simply the act of finding the intersection points of walls and paths.  
            wallLeft = wall[0]
            wallRight = wall[0] + wall[2]
            wallTop = wall[1]
            wallBottom = wall[1] + wall[3]
            
            xWallOne = [wallLeft, wallTop, wallBottom]
            xWallTwo = [wallRight, wallTop, wallBottom]
            xWalls.append(xWallOne)
            xWalls.append(xWallTwo)
            
            yWallOne = [wallTop, wallLeft, wallRight]
            yWallTwo = [wallBottom, wallLeft, wallRight]
            yWalls.append(yWallOne)
            yWalls.append(yWallTwo)
            
        
        while running:            
            playerInfo[playerName] = [playerPos[0],playerPos[1],infStatus,virus,infDist,infStrength,wallShareCheck]
            await websocket.send(json.dumps(playerInfo))
            response = await websocket.recv()
            playerList = json.loads(response)
            playerStats = playerList[playerName]
            playerPos = [playerStats[0],playerStats[1]]
            infStatus = playerStats[2]
            
            if infStatus == True:
                playerDir = chase(playerList, xWalls, yWalls, playerRadii)
            #else:
            #    playerDir = flee(playerList, walls, playerRadii)
                
            step = int(playerRadii * 1/6) # This is quite a lot slower than the human players.  Currently this is just for testing but it could be make quicker later.  
            xOffset = playerDir[0] * step
            yOffset = playerDir[1] * step
            playerPos[0] += xOffset
            playerPos[1] += yOffset
            
            infStatus, virus, infDist,infStrength = infectionLogicDef(playerList)
            
# ----------------

plt.ion()
fig, ax = plt.subplots()
 
asyncio.run(interlinked())
