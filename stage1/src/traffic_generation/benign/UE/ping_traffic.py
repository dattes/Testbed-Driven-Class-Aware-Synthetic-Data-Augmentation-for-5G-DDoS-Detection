import time
import subprocess


# Run the ping command for specific amount of time
def run_simulation(server_ip, runtime):
    try:
        subprocess.run(["ping", f"{server_ip}"], shell=False, timeout=runtime)
    except subprocess.TimeoutExpired:
        print(f"Terminated since it run for {runtime} seconds.")


# Ping the a DN server for exact amount of time
if __name__ == "__main__":
    
    program_starts = time.time()
    run_time = 14400 # Seconds
    server_ip = "192.168.3.3" # DN server's IP
    now = time.time()

    print(f"Start {run_time} seconds simulation:")

    run_simulation(server_ip ,run_time)
    
    print(f"\n{run_time} seconds ping-simulation finished!")