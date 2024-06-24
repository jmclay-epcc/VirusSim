import threading
import subprocess
import time

def run_script(script_name):
    subprocess.run(["python", script_name])

if __name__ == "__main__":
    script1_thread = threading.Thread(target=run_script, args=("server.py",))
    script2_thread = threading.Thread(target=run_script, args=("client.py",))
    script3_thread = threading.Thread(target=run_script, args=("roboclient1.py",))
    script5_thread = threading.Thread(target=run_script, args=("roboclient3.py",))
    script4_thread = threading.Thread(target=run_script, args=("roboclient2.py",))
    script6_thread = threading.Thread(target=run_script, args=("display.py",))

    script1_thread.start()
    time.sleep(0.5)
    script2_thread.start()
    script3_thread.start()
    script4_thread.start()
    script5_thread.start()
    script6_thread.start()

    script1_thread.join()
    script2_thread.join()
    script3_thread.join()
    script4_thread.join()
    script5_thread.join()
    script6_thread.join()

    print("Scripts have finished executing.")