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
import matplotlib.lines as mlines

nltk.download('words')

playerName = random.choice(words.words())
virus = random.choice(words.words())
infDist = random.randint(1,200) # This is a distance in units.  I think the unit is a pixel?  
infStrength = random.randint(0,100) # This is a percentage.  
infCheckTime = 2
counter = random.randint(1,115)
playerPos = [900,500]
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
    
    ax.cla()
    
    def magiciansStaff(parentTP, TPCount):
        
        viableChildTPList = [] # This is the list that we ultimately want to populate and return.  
        
        numerator = targetPos[1]-playerPos[1]
        denominator = targetPos[0]-playerPos[0]      
        if denominator == 0:
            denominator = 0.000001
            
        angle2target = math.degrees(math.tanh(numerator/denominator))
        
        if denominator < 0:
            angle2target += 180
        elif numerator < 0:
            angle2target += 360
        
        for i in range(int(TPCount/2)):
            childTPset_a = [] # We want these to only ever be points that lie above their parents on the X axis.  
            childTPset_b = [] # We want these to only ever be points that lie below their parents on the X axis.  
            parentTPset = []
            
            lineAngleDegrees = i*(math.ceil(360/TPCount)) + angle2target
            if lineAngleDegrees >= 360:
                lineAngleDegrees -= 360
            if lineAngleDegrees >= 180:
                lineAngleDegrees -= 180
                
            lineAngle = math.radians(lineAngleDegrees)
            
            outerTPOffset = 0.75 # I've put a footnote at the bottom on this script to explain why we do this, and why we need truePlayerRadii
            truePlayerRadii = outerTPOffset * playerRadii + abs(((playerRadii * math.sqrt(2)) - playerRadii) * math.sin(2*lineAngle)) 
            xStep = truePlayerRadii * math.sin(lineAngle) # The purpose of these X and Y steps is to take a given point on a line, and find a new point that is offset from the initial point, perpendicularly to the line, by playerRadii * outerTPOffset. 
            yStep = truePlayerRadii * math.cos(lineAngle) # Although in truth these values do double-duty.  We can move a point parallel to its line by adding yStep to its x-component and xStep to its y-component (altering the sign of each component accordingly).  They should really be renamed "sinStep" and "cosStep".  Maybe later.  Maybe never! Ho ho!  
            for j in range(3): 
                intersects = []
                intersectsSetTwo = []
                
                if j == 0:
                    offset_parentTP = parentTP # In this case, the offset_parentTP is not actually offset from the parentTP, but for the sake of an easy life lets just say it has an offset of 0.  
                elif j == 1:
                    offset_parentTP = (parentTP[0] - xStep, parentTP[1] + yStep)
                elif j == 2:
                    offset_parentTP = (parentTP[0] + xStep, parentTP[1] - yStep)
                    
                parentTPset.append(offset_parentTP)
                    
                ax.scatter(offset_parentTP[0], offset_parentTP[1], color = 'black', s = 1)
                    
                m = math.tan(lineAngle) + 0.00001 
                c = -(m*offset_parentTP[0] - offset_parentTP[1])
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

                nearestChildTPDist = 500000
                secondNearestChildTPDist = 500000
                for I in intersects: # I stands for Intersects.  Not all intersects are valid childTPs, though, which is what we're checking for here.  
                    dist = math.hypot((offset_parentTP[0]-I[0]),(offset_parentTP[1]-I[1]))
                    if dist < nearestChildTPDist:
                        nearestChildTPDist = dist
                        nearestChildTP = I # The nearest intersect to the test point will always be the first wall that the hypothetical magicians staff hits.  The difficulty comes after this - we want the positions of the first two walls that the staff hits, however the second nearest intersect might well just be the other side of the first wall, which we are not interested in.  
                for I in intersects: # So here what we're doing is checking if nearestI lies between the testPoint and any of the other intersects.  If it DOESN'T, then we know that this newly found intersect cannot possibly be on the "other side" from the testPoints point of view, which is good because we are not interested in any of those points.  THis leaves us with a new set of intersects which definitely contains the second of the first two walls that the magicians staff hits, this being the one that is nearest to the testPoint.  
                    betweenX = min(offset_parentTP[0], I[0]) <= nearestChildTP[0] <= max(offset_parentTP[0], I[0])
                    betweenY = min(offset_parentTP[1], I[1]) <= nearestChildTP[1] <= max(offset_parentTP[1], I[1])
                
                    if betweenX == False and betweenY == False:
                        intersectsSetTwo.append(I)
            
                for I in intersectsSetTwo:
                    dist = math.hypot((offset_parentTP[0]-I[0]),(offset_parentTP[1]-I[1]))
                    if dist < secondNearestChildTPDist:
                        secondNearestChildTPDist = dist
                        secondNearestChildTP = I
                        
                if nearestChildTP[0] > offset_parentTP[0]:
                    childTPset_a.append(nearestChildTP) # These lists will fill in this order: Tp with no offset (this is the mainline), TP with positive offset (e.g. this line is above the mainline when the gradient is positive), TP with negative offset (e.g. this line is below the mainline when the gradient is positive).  
                    childTPset_b.append(secondNearestChildTP)
                else:
                    childTPset_a.append(secondNearestChildTP)
                    childTPset_b.append(nearestChildTP)
                
                # --- graphing stuff ---
                
                if j == 0:
                    colour = '#c9c9c9'
                    X = (nearestChildTP[0],secondNearestChildTP[0])
                    Y = (nearestChildTP[1],secondNearestChildTP[1])
                    plt.plot(X,Y, c = colour, zorder=-10)
                
                # --- graphing stuff OVER ---
                
            def furthestViableTP(childTPset, parentTPSet):
                childTPsetDists = []
                
                for i in range(3):
                    current_childTP = childTPset[i]
                    current_parentTP = parentTPSet[i]
                    
                    TPDist = math.hypot((current_parentTP[0]-current_childTP[0]),(current_parentTP[1]-current_childTP[1]))
                    childTPsetDists.append(TPDist)
                    
                nearestChildTP_Index = childTPsetDists.index(min(childTPsetDists)) # We want to find which of the three test points in TPset is the nearest to the parentTP, because that point represents the furthest distance the player can travel in the direction of the mainlineTP before bumping into a wall.  
                nearestChildTP = childTPset[nearestChildTP_Index]
                nearestChildTPsParent = parentTPSet[nearestChildTP_Index]
                
                # This next block of script takes the nearestChildTP which we just found, and applies some transformations so that it is inline with the mainline (while remaining the same distance away, so we're just moving it perpendicularly to the mainline), and so that it is 
                # 1 playerRadii closer to the parentTP. This might sound arbitrary to a future reader (or me 2 weeks from now), but its important - by performing these transformations, we know for definite that the point we are left with is the furthest (or a little shy of the furthest) 

                if nearestChildTP_Index == 0: 
                    furthestVCTP = nearestChildTP
                else:
                    if (nearestChildTP[1] > nearestChildTPsParent[1]): # Don't ask me what any of this shit means i don't know anymore.  
                        if nearestChildTP_Index == 1:
                            furthestVCTP = (nearestChildTP[0] + xStep - yStep,nearestChildTP[1] - yStep - xStep)
                        elif nearestChildTP_Index == 2:
                            furthestVCTP = (nearestChildTP[0] - xStep - yStep,nearestChildTP[1] + yStep - xStep)
                            
                    if (nearestChildTP[1] <= nearestChildTPsParent[1]):
                        if nearestChildTP_Index == 1:
                            furthestVCTP = (nearestChildTP[0] + xStep + yStep,nearestChildTP[1] - yStep + xStep)
                        elif nearestChildTP_Index == 2:
                            furthestVCTP = (nearestChildTP[0] - xStep + yStep,nearestChildTP[1] + yStep + xStep)
                    
                return furthestVCTP
                #return nearestChildTP
            
            furthestVCTP_a = furthestViableTP(childTPset_a, parentTPset)
            furthestVCTP_b = furthestViableTP(childTPset_b, parentTPset)
                 
            viableChildTPList.append(furthestVCTP_a)
            viableChildTPList.append(furthestVCTP_b)
            
        return viableChildTPList
           
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
                    m = 0.00001 # IF the player and target PTs x values are the same (e.g. they lie on the same horizontal wall), then the gradient will be 0.  This is not a problem for checking the x walls, but it is for the y walls, so i am just manually correcting it to a tiny value. It introduces a small error but clears up a massive headache.  
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
            
        for playerTP in playerTPList:
            dist1 = math.hypot((playerTP[0]-playerPos[0]),(playerTP[1]-playerPos[1])) # This is the distance between the player and the current playerTP.  We want to keep track of which playerTP has the largest value here.  
            if dist1 > furthestPlayerTPDist:
                furthestPlayerTPDist = dist1
                furthestPlayerTP = playerTP
            for targetTP in targetTPList:
                clearPathX = xWallChecker(playerTP,targetTP)
                clearPathY = yWallChecker(playerTP,targetTP)
                                    
                if clearPathX == True and clearPathY == True:
                    dist2 = math.hypot((playerTP[0]-targetTP[0]),(playerTP[1]-targetTP[1])) # this is the distance between the current playerTP and the target.  We want to keep track of the playerTP with the smallest value here.  
                    if dist2 < bestTPDist:
                        bestTPDist = dist2
                        bestTP = playerTP
                        
        if bestTPDist == 50000:       
            return furthestPlayerTP # If we aren't able to identify a playerTP with a clear line of sight to either the target or a targetTP, then we will return this value by default.  This should at the very least coax the player into a more favorable map position (logically i think it should push them towards the centre but im more than expecting there to be some edge-case where it gets wedged in a corner or something).  
        else:
            return bestTP # If we are able to identify one or more playerTPs with a clear line of sight to a targetTP, we will return the playerTP value with the shortest distance between it and its targetTP.      

    
    targetTestPoints = magiciansStaff(targetPos, 2 * MagStaffCalls)
    targetTestPoints.append(targetPos)
    playerTestPoints = magiciansStaff(playerPos, 2 * MagStaffCalls)
    
    bestTP = magicMissile(playerTestPoints,targetTestPoints,playerPos,targetPos)
    
    for point in targetTestPoints:
        ax.scatter(point[0], point[1], color = 'r')
        ax.scatter(targetPos[0], targetPos[1], color = 'y', marker = '*')
        
    for point in playerTestPoints:
        ax.scatter(point[0], point[1], color = 'b')
        ax.scatter(playerPos[0], playerPos[1], color = 'g', marker = '*')
        
    ax.scatter(bestTP[0], bestTP[1], color = 'gold', s = 100)
        
    ax.set_xlim(0,1800)
    ax.set_ylim(0,1000)
    
    ax.set_aspect('equal', adjustable='box')
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
    #return (0,0) # Use this when you want to clip your players wings and have it not move.  

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
        global playerRadii
        global MagStaffCalls
        
        MagStaffCalls = 11 # This is basically half the number of test points that we want to create around each parentTP.  This can be set to any odd number.  To grossly summarise the process, this script is set up such that each TP found will be seperated by an angle of 360/2*magStaffCalls, so if magStaffCalls = 1 then the TPs will be 180 degrees apart.  If magStaffCalls is even, for example 2, then there will be TPs at 90 and 270 degrees, which mean that they lie on a line with infinite gradient, which is a problem that is best just avoided outright.  11 seems to be a sweet spot.  
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



# Footnote
# -------------
# When trying to draw a square on a co-ordiante grid, we have two (maybe three) pieces of information to go off of: the squares side 
# length, the angle we're looking at it from, and the fact that it is indeed a square.  I, being bad at maths, approached this naively - If we approximate the square by drawing points at a distance sidelength/2 (or playerRadii), 
# (e.g. drawing a circle) then we know that this will be exactly correct at four points (the points that lie exactly on the X and Y axis), will be massively wrong at 4 more points (the points where X and Y have the 
# same absolute value), and sort of iffy in between.  So, i thought, we can fix this by having the distance we plot the points at be variable, in order to "pin" them at correct values given the angle that we're looking at the square from.  
# Wed want this extra term vary with the angle so that it doesn't add anything when the circle approximate is correct (e.g. at angles 0, 90, 180 and 270), ands a lot when its very incorrect (45, 135, 225, and 315), and 
# then add whatever is appropriate in between these values.  So i did that - i added a sin term to the distance (thus giving us the variable truePlayerRadii), and found that while it was now exactly correct at 8 points, 
# it still had considerable error everywhere else.   "No matter", i thought to myself, "i'll just add another sin term that pins the values where its still wrong".  But then the obvious struck me and i realised that i was essentially 
# chasing a fourier series, something that would only actually be accurate if it had INFINITE terms.  I could add as many terms as i wanted, and while it would narrow in on something functional without 3 or 4, it would never be perfect, 
# and the effort to chase that point would be disproportionate.  
# 
# So how to fix this without going that a fourier transform rabbit hole?  Well, the shape that truePlayerRadii gives us when we plot is is sort of like a lumpy square - its up, down, left, right and diagonal points are correct, but every
# other point is too far away.  It is unexpectable for any point to lie significantly further out from the centre of the player than its true size, because that can result in the pathfinding logic peaking through walls further down the line.  
# So instead, we add a scaling factor to draw each point slightly closer in than it otherwise would be.  This makes it so that the furthest out point of the "lumps" are roughly the right distance away from the centre of the shape, and the points 
# that were previously exactly correct are a little bit closer in.  This isn't ideal, but it significantly better than approximating the player as a circle, or overestimating its physical size.  

# Ok i've finally realised a misassumption i've been making.  I have been splitting the childTPs that i find into two sets - set a with the nearest childTPs, and set b with the second nearest childTPs - and have been operating under the 
# mistaken thought that each set are all on the same side.  I've been imagining that these points are found by first looking up the line in the position y direction, and then in the negative y direction, and thus all of set a is in the positive y
# and all of set b is in the negative.  This is obviously, obviously wrong.  The sets are filled, OBVIOUSLY, nearest in a and second nearest in b.  Whether or not the nearest in in the positive or negative y is immaterial.  Since i've been labouring
# under this bizarre misinterpretation of my own work, i've essentially been shooting myself in the foot over and over.  God almighty.  When you make an assumption, you make an ass out of An and Umption.  

# I have discovered another releated misassumption that i was making.  I am still a little sick so despite having finally realised this mistake, i can't articulate it very well.  
# So, the program picks an angle.  It then draws a line that follows this angle and which passes through the parentTP across the map.  It finds the first wall that the point intersects and places it in set A, and then finds the second point and places 
# it in set B.  It then offsets the parentTP in the positive direction, and repeats the process.  It then finally offsets the parentTP in the negative direction and repeats a final time.  This gives us set A, which is filled with nearest wall intersects 
# to each of the three parent point, and set B, which is filled with the second nearest points.  
# I have already established that when this is repeated for different angles, the new set A and B aren't nessesarily going to be on the same side of the Y-axis (which is to say, if the first set A is positive Y, then the second isn't nessesarily also going
# to be positive Y).  However the big oversight i made is that within each set, the nearest wall intersect of each of the 3 lines we test aren't nessesarily going to be on the same side of the Y-axis either.  If the nearest and second nearest points are 
# about the same distance apart, then the offset in the parentTPs position that it made for the latter two lines can be enough to flip the two nearest points.  The effect of this is that set A could contain two points that are on the same side of the Y-axis, 
# and one thats on the opposite side, which explains some issues that i was encountering perfectly.  I have updated the code to account for this, which has fixed the observed issues.  