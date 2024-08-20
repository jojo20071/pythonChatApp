import socket
import threading
import os

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
            elif message.startswith(b"/file"):
                _, recipient, filename = message.decode('utf-8').split(' ', 2)
                send_file(client_sock, recipient, filename)
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

def send_file(sender_sock, recipient_name, filename):
    with lock:
        recipient_sock = next((sock for sock, name in clients.items() if name == recipient_name), None)
    if recipient_sock:
        sender_name = clients[sender_sock]
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                file_data = f.read()
            recipient_sock.sendall(f"/file {sender_name} {filename}".encode('utf-8'))
            recipient_sock.sendall(file_data)

def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   