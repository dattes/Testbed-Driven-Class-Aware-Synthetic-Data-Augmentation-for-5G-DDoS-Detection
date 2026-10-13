import socket
from _thread import *


# TCP socket listener
def start_server(server_ip, server_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((server_ip, server_port))
    except socket.error as e:
        print(e)

    s.listen(1)
    print("Waiting for a connection, Server started")

    return s

# Sending back what is recieved by the client
def threaded_client(conn):
    conn.send(str.encode("Connected"))
    reply = ""
    
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode("utf-8")

            if not data:
                print("Disconnected")
                break

            print("Recived: ", reply)
            print("Sending: ", reply)
            conn.sendall(str.encode(reply))
        except: 
            break
    
    print("Lost connection")
    conn.close()


# Run in DN (gaming simulation)
if __name__ == "__main__":
    s = start_server("192.168.3.3", 5555)

    while True:
        conn, addr = s.accept()
        print("Connected to:", addr)
        start_new_thread(threaded_client, (conn,))
