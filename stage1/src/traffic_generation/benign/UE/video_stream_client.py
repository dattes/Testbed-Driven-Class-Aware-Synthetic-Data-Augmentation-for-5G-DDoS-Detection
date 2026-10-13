import socket, threading


# UDP socket listener (sinkhole)
def start_client(client_ip, client_port):
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
  try:
    s.bind((client_ip, client_port))
    print("Waiting for a connection, client started at port", client_port)
  except socket.error as e:
    print(e)
  
  return s

# Sinkhole recieved UDP stream with feedback for verification
def recieve_stream(s):

  while True:
    try:
      s.recvfrom(2048)
      print("Stream frame recieved by", s.getsockname())
    except:
      pass


# Concurrent video and audio recieving using threads
if __name__ == "__main__":
    # IP of UE's GTP Tunnel IP using distinct ports
    video = start_client('10.60.0.1', 5000)
    audio = start_client('10.60.0.1', 5001)

    t1 = threading.Thread(target=recieve_stream, args=(video,))
    t2 = threading.Thread(target=recieve_stream, args=(audio,))
    
    t1.start()
    t2.start()

    t1.join()
    t2.join()