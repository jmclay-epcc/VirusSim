import asyncio
import websockets
import json
import tkinter as tk
import subprocess
import threading

counter = 0

dummyPlayerInfo = {}
name = "1995199820022006"

uri = "ws://localhost:8765"

def spawner(script):
    globals()[f'autoClient{counter}'] = subprocess.Popen(["python", script])

async def main(t):
    global counter
    
    if t == "Spawn bot":
        counter += 1
        globals()[f'autoClient{counter}_thread'] = threading.Thread(target=spawner, args=("autoClient.py",))
        globals()[f'autoClient{counter}_thread'].start()
    elif t == "Spawn 10 bots":
        for i in range(10):
            counter += 1
            globals()[f'autoClient{counter}_thread'] = threading.Thread(target=spawner, args=("autoClient.py",))
            await asyncio.sleep(0.1)
            globals()[f'autoClient{counter}_thread'].start()
            await asyncio.sleep(0.1)
    elif t == "Spawn 100 bots!":
        for i in range(100):
            counter += 1
            globals()[f'autoClient{counter}_thread'] = threading.Thread(target=spawner, args=("autoClient.py",))
            await asyncio.sleep(0.2)
            globals()[f'autoClient{counter}_thread'].start()
            await asyncio.sleep(0.2)
    elif t == "Kill last bot" and counter > 0:
        globals()[f'autoClient{counter}'].kill()
        await asyncio.sleep(0.1)
        counter -= 1
    elif t == "Kill all bots" and counter > 0:
        for i in range(counter):
            globals()[f'autoClient{i+1}'].kill()
        counter = 0
    else: 
        await on_button_click(t)

async def on_button_click(button_text):
    async with websockets.connect(uri) as websocket:
        infStrength = infStrengthScale.get()
        infDist = infDistScale.get()
        dummyPlayerInfo[name] = [button_text,infDist,infStrength,0,0,0,True]
        await websocket.send(json.dumps(dummyPlayerInfo))
        print('"', button_text, '"', "command sent")
        await asyncio.sleep(0.25) # Commands that need to effect every player need to be held on for a while so that every player get updated.  For 20 players, 1/4 a second SHOULD be enough.  
        dummyPlayerInfo[name] = [0,0,0,0,0,0,True]
        await websocket.send(json.dumps(dummyPlayerInfo))
        await websocket.close()

# Create the main window
root = tk.Tk()
root.title("GM Console")
root.minsize(600, 440)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

warning = tk.Label(button_frame, text = "Note: Don't close the the console without killing any active bots, otherwise they'll become unkillable and you'll need to restart the server.  And wait until the bots have actually spawned before you press the 'spawn bots' buttons again, otherwise you will also end up with unkillable bots.", wraplength=400, justify="center")
warning.pack(pady=5)

# Create buttons and place them in the window
button_texts = ["Cure all", "Spawn bot", "Spawn 10 bots", "Kill last bot", "Kill all bots"]
for text in button_texts:
    button = tk.Button(button_frame, text=text, command=lambda t=text: asyncio.run(main(t)))
    button.pack(padx=5, pady=10, side = tk.LEFT)
    
label = tk.Label(root, text = "Virus Range & Strength", wraplength=300, justify="left")
label.pack()
label = tk.Label(root, text = "200 and 100 are the default maximum values.  You can go higher for more extreme behaviour.", wraplength=300, justify="left")
label.pack()

infDistScale = tk.Scale(root,orient="horizontal",length=500,width=20,sliderlength=10,from_=0,to=500,tickinterval=100)
infDistScale.pack()
    
infStrengthScale = tk.Scale(root,orient="horizontal",length=500,width=20,sliderlength=10,from_=0,to=200,tickinterval=50)
infStrengthScale.pack()

button = tk.Button(root, text= "Infect random player", command=lambda t=text: asyncio.run(main("Infect player")))
button.pack(pady=10)

button = tk.Button(root, text= "Spawn 100 bots! (Takes a while)", command=lambda t=text: asyncio.run(main("Spawn 100 bots!")))
button.pack(pady=10)

# Start the GUI event loop
root.mainloop()

