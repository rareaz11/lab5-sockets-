import selectors
import socket
import time
import threading

sel = selectors.DefaultSelector()
clients = {}

HOST = 'localhost'
PORT = 65433
LOGFILE = "chat_server.log"

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ)

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOGFILE, "a") as f:
        f.write(line + "\n")

def broadcast(msg, exclude_conn=None):
    for c in clients:
        if c != exclude_conn:
            try:
                c.sendall(msg.encode())
            except:
                pass

def active_users_report():
    while True:
        time.sleep(10)
        count = len(clients)
        log(f"[USERS ONLINE] Trenutno aktivnih korisnika: {count}")

# Pokreni thread koji svakih 10 sekundi ispisuje broj korisnika
threading.Thread(target=active_users_report, daemon=True).start()

log(f"[CHAT SERVER] Listening on {HOST}:{PORT}")

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
                    text = data.decode().strip()
                    if clients[conn]["name"] is None:
                        clients[conn]["name"] = text
                        log(f"[LOGIN] {text} from {clients[conn]['addr']}")
                    else:
                        if text == "/users":
                            # Odgovori klijentu popisom korisnika
                            users = ", ".join(c["name"] for c in clients.values() if c["name"])
                            try:
                                conn.sendall(f"Online korisnici: {users}".encode())
                            except:
                                pass
                        else:
                            msg = f"{clients[conn]['name']}: {text}"
                            log(msg)
                            broadcast(msg, exclude_conn=conn)
                else:
                    if conn in clients:
                        log(f"[LOGOUT] {clients[conn]['name']}")
                        sel.unregister(conn)
                        conn.close()
                        del clients[conn]

except KeyboardInterrupt:
    log("\n[SHUTDOWN] Server se zatvara...")

finally:
    for conn in list(clients):
        sel.unregister(conn)
        conn.close()
    sel.unregister(lsock)
    lsock.close()
    sel.close()
    log("[CLEANUP] Server je zatvoren.")
