import socket
import threading

HOST = 'localhost'
PORT = 65433

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

name = input("Unesite korisničko ime: ")
sock.sendall(name.encode())

def receive_messages():
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\nVeza sa serverom je prekinuta.")
                break
            print("\n" + data.decode())
        except:
            break

# Pokreni thread koji stalno prima poruke od servera
threading.Thread(target=receive_messages, daemon=True).start()

print("Chat započet. Koristite Ctrl+C za izlaz.")

try:
    while True:
        msg = input("> ")
        if msg.strip():
            sock.sendall(msg.encode())
except KeyboardInterrupt:
    print("\nIzlaz iz chata...")
finally:
    sock.close()
