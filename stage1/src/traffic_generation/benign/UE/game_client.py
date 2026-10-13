import socket, time, random

# Jitter with spike to add realism
def jitter(base, std_dev, spike, spike_prob):
    delay = -1

    while (delay<0):
        # Gaussian jitter
        delay = random.gauss(base, std_dev)

        # Spike
        if random.random() <= spike_prob:
            delay = spike
    
    return delay


# TCP socket listener
def start_client(server_ip, server_port):
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = (server_ip, server_port)

    c.connect(addr)
    id = c.recv(2048).decode()
    print(id)

    return c

# Response
def send(c, data):
    try:
        c.send(str.encode(data))
        return c.recv(2048).decode()
    except socket.error as e:
        print(e)


# Send and reply with jitter and spike using TCP Sockets on client side
if __name__ == "__main__":
    # Setup time of simulation
    program_starts = time.time()
    run_time = 14400 # Seconds
    now = time.time()

    # Start client and connect to game-Server
    c = start_client("192.168.3.3", 5555)

    # Run for specific amount of time
    while((now - program_starts) <= run_time):
        now = time.time()
        time.sleep((jitter(30,10,120,0.05)/1000)) # spike: 120ms, spike propability: 5%, delay: 30ms, delay std dev: 10ms
        print(send(c, "Hello World!"))

    print(f"\n{run_time} seconds gaming simulation finished!")
