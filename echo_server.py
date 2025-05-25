import selectors
import socket

sel = selectors.DefaultSelector()

HOST = 'localhost'
PORT = 65432

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ)
print(f"[SERVER] Listening on {HOST}:{PORT}")

connections = {}

try:
    while True:
        events = sel.select(timeout=1)  # timeout od 1 sekunde
        for key, _ in events:
            if key.fileobj is lsock:
                conn, addr = lsock.accept()
                print(f"[NEW] Connection from {addr}")
                conn.setblocking(False)
                sel.register(conn, selectors.EVENT_READ)
                connections[conn] = addr
            else:
                conn = key.fileobj
                data = conn.recv(1024)
                if data:
                    print(f"[RECV from {connections[conn]}] {data.decode()}")
                    conn.sendall(data)
                else:
                    print(f"[CLOSE] {connections[conn]}")
                    sel.unregister(conn)
                    conn.close()
                    del connections[conn]
except KeyboardInterrupt:
    print("\n[SHUTDOWN] Server is shutting down...")

finally:
    for conn in list(connections):
        sel.unregister(conn)
        conn.close()
    sel.unregister(lsock)
    lsock.close()
    sel.close()
    print("[CLEANUP] Server closed.")
