import socket
import threading

clients = {}
lock = threading.Lock()

def broadcast(message, sender_sock=None):
    with lock:
        for client_sock, client_name in clients.items():
            if client_sock != sender_sock:
                client_sock.sendall(message)

def handle_client(client_sock):
    try:
        username = client_sock.recv(1024).decode('utf-8')
        with lock:
            clients[client_sock] = username
        broadcast(f"{username} has joined the chat!".encode('utf-8'), client_sock)
        while True:
            message = client_sock.recv(1024)
            if message.startswith(b"/msg"):
                _, recipient, msg = message.decode('utf-8').split(' ', 2)
                send_private_message(client_sock, recipient, msg)
            else:
                broadcast(message, client_sock)
    except:
        pass
    finally:
        with lock:
            client_name = clients.pop(client_sock, None)
        broadcast(f"{client_name} has left the chat.".encode('utf-8'))
        client_sock.close()

def send_private_message(sender_sock, recipient_name, msg):
    with lock:
        recipient_sock = next((sock for sock, name in clients.items() if name == recipient_name), None)
    if recipient_sock:
        sender_name = clients[sender_sock]
        recipient_sock.sendall(f"[Private] {sender_name}: {msg}".encode('utf-8'))

def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(("localhost", 12345))
    server_sock.listen(5)
    print("Server started on port 12345")

    while True:
        client_sock, _ = server_sock.accept()
        threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()

if __name__ == "__main__":
    main()