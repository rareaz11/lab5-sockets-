import socket 
 
HOST = 'localhost' 
PORT = 65433 
 
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
sock.connect((HOST, PORT)) 
 
name = input("Unesite korisničko ime: ") 
sock.sendall(name.encode()) 
 
print("Chat započet. Koristite Ctrl+C za izlaz.") 
 
while True: 
    msg = input("> ") 
    sock.sendall(msg.encode())
