import socket
import threading

clients = []

def broadcast(message, sender_sock):
    for client in clients:
        if client != sender_sock:
            client.sendall(message)

def handle_client(client_sock):
    while True:
        try:
            message = client_sock.recv(1024)
            broadcast(message, client_sock)
        except:
            clients.remove(client_sock)
            client_sock.close()
            break

def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(("localhost", 12345))
    server_sock.listen(5)

    while True:
        client_sock, _ = server_sock.accept()
        clients.append(client_sock)
        threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()

if __name__ == "__main__":
    main()