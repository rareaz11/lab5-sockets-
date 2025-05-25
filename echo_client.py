import socket 
HOST = 'localhost' 
PORT = 65432 
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
sock.connect((HOST, PORT)) 
msg = input("Unesite poruku: ") 
sock.sendall(msg.encode()) 
data = sock.recv(1024) 
print(f"Odgovor servera: {data.decode()}") 
sock.close()
