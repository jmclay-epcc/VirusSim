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
        globals()[f'autoClient{counter}_thread'] = threading.Thread(target=spawner, args=("autoClient.py",))
        globals()[f'autoClient{counter}_thread'].start()
        counter += 1
    if t == "Kill last bot" and counter > 0:
        globals()[f'autoClient{counter}'].kill()
        counter -= 1
    else: 
        await on_button_click(t)

async def on_button_click(button_text):
    async with websockets.connect(uri) as websocket:
        dummyPlayerInfo[name] = [button_text,0,0,0,0,0,True]
        await websocket.send(json.dumps(dummyPlayerInfo))
        print('"', button_text, '"', "command sent")
        await asyncio.sleep(0.25) # Commands that need to effect every player need to be held on for a while so that every player get updated.  For 20 players, 1/4 a second SHOULD be enough.  
        dummyPlayerInfo[name] = [0,0,0,0,0,0,True]
        await websocket.send(json.dumps(dummyPlayerInfo))
        await websocket.close()

# Create the main window
root = tk.Tk()
root.title("Control client test")

# Create buttons and place them in the window
button_texts = ["Cure all", "Spawn bot", "Kill last bot", "Infect player - long range, weak", "Infect player - short range, strong", "Infect player - bad", "Infect player - good"]
for text in button_texts:
    button = tk.Button(root, text=text, command=lambda t=text: asyncio.run(main(t)))
    button.pack(pady=10)

# Start the GUI event loop
root.mainloop()

