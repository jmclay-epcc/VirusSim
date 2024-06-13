# Explaination of important scripts.  

### To launch the server script, display script, client and bot client scripts in a single terminal, run run_scripts.py.  The clients and the display won't run unless the server is already running - they'll just crash if you launch them by themselves.  However you can also run each script in individual terminals - as long as decoupled_server.py is started before any of the clients, the clients will start up and connect just fine.  

## decoupled_server.py

The tasks that this script executes can be broken down into these steps:-

1. The playable area is defined.  It is here that the boards height and width are defined, as well as the position of any in-game walls.  You will notice that pygame is used for defining the walls even though the script doesn’t create a pygame window.  This is because an earlier version of the script did create a pygame window, and frankly this is just a nice convenient way of doing it. 

2. A websocket server is created, which multiple clients are able to connect to.  Every step after this is contained within a while loop, and will repeat until the script is manually killed.  

3. The servers then waits until a connected client sends a message.  The clients messages consist of a json file with the following format:-  

	player name: player pos X, player pos Y, infection Status, virus name, infection distance, infection strength

	A check is done at this point - if the connecting clients name is “Display1234567890”,  they are considered a display client and are skipped forward to step 7.  If not, they progress through the steps are normal.  

4. The players name and websocket ID are added to a dictionary, along with the names and websocket IDs of all other connected players.  This means that when a websocket connected is severed (e.g. a player disconnects), we can easily look up which player this websocket connection corresponds to, and remove them from the player dictionary defined in step 6.  

5. Checks that the players X and Y positions fall within legal areas (i.e Isn’t outside of the playable area or inside a wall).  If the positions values fall within illegal areas, new corrected values are inserted into the players stats.  There are two different ways that new positions are calculated - if a player is inside a wall, then they are moved to the nearest position outside of the wall.  If they are outside of the playable area, they’re just plopped in a random place inside (This can sometimes result in the player being places in a wall, but they’ll get bumped out into a legal position on the very next frame so its not really an issue).  

6. The players corrected stats are then placed in a larger dictionary that contains the stats of every connected player.  

7. This full dictionary is then sent back to the client.  The script then sleeps for some pre-defined period (currently 1/60 of a second).  

9. The while loop then starts over (see step 3 and onwards).  



## client.py

The tasks that this script executes can be broken down into these steps:-

1. A pygame instance is initiated, and its window size defined.  We also import the infectionLogic.py script at this point.  

2. The initial player stats are pulled from the infectionLogic,py script.  The player is given a starting position between -1000,1000 and -1000,-1000, which might seem odd but is for a good reason.  The client does not know the size of the playable area (to do this we'd have to share the board dimensions over the websocket, which is doable but a bit redundant), so giving them a nice random initial distribution that makes full use of the playable area is hard.  However, the server already has the capability to do this - when a player finds themselves outside of the playable area (this can happen if they set their movement speed very high, or if they somehow send bad position data), they automatically get dropped back into a random place in the full playable area.  So by having each player spawn in an initially bad location, the server will automatically redistributes them into good locations after 1 frame (technically 2 frames if they get respawned into a wall but they'll be put into a good location 99% of the time after that).  

3. The client script is then connected to the server.  Every step beyond this is contains within a while loop and will repeat until the pygame window is closed.  

4. The control UI elements are defined (directional buttons, infection status readout, etc).  A set of If statements check for control inputs (e.g. move up, move left, etc), and updates the players position accordingly.  A check is also done on the players infection status, and the readout is updated if needed.  The pygame window is then flipped to display these UI changes.  

5. The players name and stats are then saved into a dictionary, with the following format:-  
	
	player name: player pos X, player pos Y, infection Status, virus name, infection distance, infection strength

	This dictionary is then send to the server as a json file (see step 3 in decoupled_server.py).  

6. The client then awaits a reply from the server, which will consist of a json file containing the names and stats of every player connected to the server (see step 7 in decoupled_server.py).  The players own stats are then extracted from this list, and uses them to update its own X and Y positions (in case the values it sent to the server in step 5 were illegal and the server sent back corrected legal values).  

7. infectionLogicDef, which is held within infectionLogic.py, is invoked, with the player list that we received from the server in step 6 as the input (as well as a counter, which is just a number that ticks up by one every frame and resets to 0 if the player becomes infected or if it exceeds a certain value defined in infectionLogic.py).  This returns updated values for infection status, virus name, infection strength, and the counter.  

8. The while loop then starts over (see step 4 and onwards).  


## infectionLogic.py

This is a significant script because Its the one that the masterclass attendees will actually interact with directly.  As such, the contents are less of a hard-and-fast definition, and more of a suggested outline.  The attendees can really put whatever they want in here given that it follows certain criteria and returns the right values.  

The tasks that this script executes can be broken down into these steps:-

1. The players initial values are defined.  These consist of their player name, infection status, infection name, infection distance and infection strength.  If the infection status is False, then the rest of the infection stats don’t really matter as they get updated if the player is eventually infected.  An infection check time and counter are also defined - the infection check time is how often (in seconds) the player should check to see if I is at risk of being infected by another player, and the counter is a number that ticks up by one every frame, and then resets to zero after the infection check time passes.  There is a potential issue here that a large number of players would result in a longer time between each player invoking infectionLogic.py, which in turn would screw with how often each player checks for infection.  If this turns out to actually be an issue im sure it can be solved, but based off of my testing it seems alright?

2. An if statement runs if the player is currently uninfected, and if their counter is currently above a specified value.  If the player meets these two criteria then their counter is reset to 0; if they are uninfected but their counter is below 0 then their counter is incremented up by 1.  

3. (Still in this if loop, conditional on the player being uninfected and their counter being above the specified value) A for loop is started which runs through other player on the full player list (see step 7 of client.py).  Each infected player on the list provides a position, an infection name, an infection strength, and an infection distance.  If the current player finds that it is within the infection distance of an infected player, it uses the infected players infection distance and strength to calculate a percentage odds of being infected, based off of a sigmoid curve formula (this part is absolutely overly complicated.  You could easily just have the odds of infection be determined linearly by the distance and have the strength be an additional thing).  

4. A random number between 1 and 100 is then generated.  If it’s less than the calculated odds of infection, then the player becomes infected.  The players infection status is changed to True, and they take on the stats of the player that infected them (virus name, strength, distance).  The for loop is then broken.  If the number is higher then the player is not infected, and the for loop breaks within anything being changed.  

5. With the for loop now finished, the players new infection status, virus name, infection distance, infection strength and counter value are returned to client.py (see step 7 of client.py).  


## display.py

This is essentially a modified version of client.py, which sends the a set of dummy player stats, under a specific player name that the server recognises and excludes from the player list.  It then receives the full player dictionary from the server, and displays this in its pygame window.  It also runs some basic scripting that generates unique colours for infected players based off of their infections name.  

This is a somewhat crude execution, but this does not matter - Luca’s webpage will replace this script entirely.  This is really just a proof on concept to show how a websocket client can be used to create a UI, rather than having the UI baked right into the server script itself, or by doing some other complicated method.  


## The less important scripts

The numbered infectionLogics, and roboclients, and run_scripts.py all relate to testing.  You can use these to launch multiple clients that jitter arounds on a random walk.  There is a branch of this repo that has 20 bots but i am NOT updating that all by hand.  We can get the damn thing on some VMs and test it properly.  

server (depreciated).py is the old version of the server script.  It is essentially just decoupled_server.py and display.py smushed together.  This probably won't work anymore due to it using strings instead of json files to talk over the websockets.   

expo.py is a very simple tool that lets you visualise the infection curves of an infected player.  You can toggle the infections distance and strength, and see how that changes the likelyhood if this player infecting another at any given distance.  It started off as a debug tool to help me wrap my head around what the hell a sigmoid curve was but I think its quite a fun visualisation.  
