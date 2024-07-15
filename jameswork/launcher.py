import threading
import subprocess
import time

roboclientCount = 30

def run_script(script_name):
    subprocess.run(["python", script_name])

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_script, args=("server.py",))
    client_thread = threading.Thread(target=run_script, args=("client.py",))
    
    for n in range(1,roboclientCount + 1):
        globals()[f'roboclient{n}_thread'] = threading.Thread(target=run_script, args=("roboclientX.py",))

    server_thread.start()
    time.sleep(0.5)
    client_thread.start()
    for n in range(1,roboclientCount + 1):
        globals()[f'roboclient{n}_thread'].start()
    
    client_thread.join()
    for n in range(1,roboclientCount + 1):
        globals()[f'roboclient{n}_thread'].join()

    print("Scripts have finished executing.")