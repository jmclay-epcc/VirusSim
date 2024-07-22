import threading
import subprocess
import time

autoClientCount = 20
     
def run_script(script_name):
    subprocess.run(["python", script_name])

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_script, args=("server.py",))
    #client_thread = threading.Thread(target=run_script, args=("client/client.py",))
    
    for n in range(1,autoClientCount + 1):
        globals()[f'autoClient{n}_thread'] = threading.Thread(target=run_script, args=("autoClient.py",))

    server_thread.start()
    time.sleep(5)
    #client_thread.start()
    for n in range(1,autoClientCount + 1):
        globals()[f'autoClient{n}_thread'].start()
    
    #client_thread.join()
    for n in range(1,autoClientCount + 1):
        globals()[f'autoClient{n}_thread'].join()

    print("Scripts have finished executing.")