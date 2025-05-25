import selectors
import socket

sel = selectors.DefaultSelector()
clients = {}

HOST = 'localhost'
PORT = 65433

# Kreiraj i pripremi socket servera
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ)

print(f"[CHAT SERVER] Listening on {HOST}:{PORT}")

try:
    while True:
        events = sel.select(timeout=1)
        for key, _ in events:
            if key.fileobj == lsock:
                conn, addr = lsock.accept()
                conn.setblocking(False)
                sel.register(conn, selectors.EVENT_READ)
                clients[conn] = {"addr": addr, "name": None}
            else:
                conn = key.fileobj
                try:
                    data = conn.recv(1024)
                except ConnectionResetError:
                    data = None

                if data:
                    if clients[conn]["name"] is None:
                        # Prva poruka je korisničko ime
                        clients[conn]["name"] = data.decode().strip()
                        print(f"[LOGIN] {clients[conn]['name']} from {clients[conn]['addr']}")
                    else:
                        msg = f"{clients[conn]['name']}: {data.decode()}"
                        print(msg)
                        # Broadcast poruke svim ostalim klijentima
                        for c in clients:
                            if c != conn:
                                try:
                                    c.sendall(msg.encode())
                                except:
                                    pass
                else:
                    # Klijent se odspojio
                    if conn in clients:
                        print(f"[LOGOUT] {clients[conn]['name']}")
                        sel.unregister(conn)
                        conn.close()
                        del clients[conn]

except KeyboardInterrupt:
    print("\n[SHUTDOWN] Server se zatvara...")

finally:
    for conn in list(clients):
        sel.unregister(conn)
        conn.close()
    sel.unregister(lsock)
    lsock.close()
    sel.close()
    print("[CLEANUP] Server je zatvoren.")
