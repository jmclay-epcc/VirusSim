import math
import random

playerName = "Robo-Client 2000"
evoDist = 30
evoStatus = 1
hand = random.randint(1,3)
handTypes = ["Rock","Paper","Scissors"]
dontInteract = ""

def infectionLogicDef(playerList):
    
    playerStats = playerList[playerName]
    playerPos = (playerStats[0],playerStats[1])
    evoStatus = playerStats[2]
    
    global hand
    global dontInteract
    
    for nthPlayer, nthStats in playerList.items(): # Loop through the list of players
        if nthPlayer != playerName: # We're only interested in the players that AREN'T current player, eg the "nth player". 
            nthPosX = nthStats[0] # Pulls out nth players stats...
            nthPosY = nthStats[1]
            nthEvoStatus = nthStats[2]
            nthHand = nthStats[3]
            dist = math.hypot((playerPos[0]-nthPosX),(playerPos[1]-nthPosY)) # Calculates the distance between current player and nth player.  
            if dist < evoDist and nthEvoStatus == evoStatus and nthPlayer != dontInteract and evoStatus != 5: # If its less than some predefined infection distance, and nth player is infected, then bingo the magic can happen.  
                print("----------",playerName,"----------")
                if (hand == 1 and nthHand == 3) or (hand == 2 and nthHand == 1) or (hand == 3 and nthHand == 2):
                    evoStatus += 1
                    print("You threw a ",handTypes[hand-1],", and your opponent threw",handTypes[nthHand-1],".  You win!")
                    if evoStatus == 5:
                        print("You have reached level 5 - peak evolution!")
                    else:
                        print("You have evolved to level ",evoStatus)
                    dontInteract = nthPlayer
                elif (hand == 1 and nthHand == 2) or (hand == 2 and nthHand == 3) or (hand == 3 and nthHand == 1):
                    evoStatus -= 1
                    print("You threw a ",handTypes[hand-1],", and your opponent threw",handTypes[nthHand-1],".  You lose!")
                    if evoStatus == 0:
                        evoStatus = 1
                        print("You can't fall any lower!")
                    else:
                        print("You have de-evolved to level ",evoStatus,".  Sad!")
                    dontInteract = nthPlayer
                elif hand == nthHand:
                    print("You both threw ",handTypes[hand-1],".  Its a draw!")
                    dontInteract = nthPlayer
            elif dist < evoDist and nthEvoStatus == evoStatus  and nthPlayer != dontInteract and evoStatus == 5:
                print("----------",playerName,"----------")
                print("You're both perfect and cannot evolve any further!")
                dontInteract = nthPlayer
            if dist > evoDist and nthPlayer == dontInteract:
                dontInteract = ""
                hand = random.randint(1,3)
                            
    return evoStatus, hand