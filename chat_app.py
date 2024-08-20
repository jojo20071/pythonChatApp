import curses
import socket
import threading
import datetime
import os
import time

CHAT_LOG_FILE = "chat_log.txt"
USERNAME = ""
USER_STATUS = {}

def load_chat_history():
    if os.path.exists(CHAT_LOG_FILE):
        with open(CHAT_LOG_FILE, 'r') as file:
            return file.readlines()
    return []

def save_chat_history(chat_history):
    with open(CHAT_LOG_FILE, 'w') as file:
        file.writelines(chat_history)

def log_message(chat_history, msg, sender="You"):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    chat_history.append(f"[{timestamp}] {sender}: {msg}\n")
    save_chat_history(chat_history)

def draw_chat_window(chat_window, chat_history):
    chat_window.clear()
    chat_window.border()
    chat_window.addstr(1, 2, "".join(chat_history[-(chat_window.getmaxyx()[0] - 3):]))
    chat_window.refresh()

def draw_input_window(input_window, prompt="Type your message: "):
    input_window.clear()
    input_window.border()
    input_window.addstr(1, 1, prompt)
    input_window.refresh()

def resize_windows(stdscr, chat_window, input_window):
    height, width = stdscr.getmaxyx()
    chat_window.resize(height - 3, width)
    input_window.resize(3, width)
    input_window.mvwin(height - 3, 0)
    stdscr.clear()
    chat_window.clear()
    input_window.clear()
    stdscr.refresh()

def receive_messages(sock, chat_window, chat_history):
    while True:
        try:
            msg = sock.recv(1024).decode('utf-8')
            if msg.startswith("/status"):
                update_user_status(msg)
            else:
                log_message(chat_history, msg, sender="Friend")
            draw_chat_window(chat_window, chat_history)
        except:
            log_message(chat_history, "Connection lost. Trying to reconnect...")
            sock.close()
            break

def connect_to_server(chat_history):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            sock.connect(("localhost", 12345))
            log_message(chat_history, "Connected to server.")
            return sock
        except:
            log_message(chat_history, "Failed to connect. Retrying in 5 seconds...")
            time.sleep(5)

def authenticate_user(input_window):
    global USERNAME
    input_window.clear()
    draw_input_window(input_window, "Enter username: ")
    USERNAME = input_window.getstr(1, 18, 20).decode('utf-8')

def update_user_status(status_msg):
    parts = status_msg.split()
    username = parts[1]
    status = parts[2]
    USER_STATUS[username] = status

def main(stdscr):
    curses.curs_set(1)
    stdscr.clear()

    height, width = stdscr.getmaxyx()

    chat_window = curses.newwin(height - 3, width, 0, 0)
    input_window = curses.newwin(3, width, height - 3, 0)

    authenticate_user(input_window)

    chat_history = load_chat_history()
    if not chat_history:
        chat_history.append("Welcome to the Python Chat!\n")

    draw_chat_window(chat_window, chat_history)
    draw_input_window(input_window)

    sock = connect_to_server(chat_history)
    threading.Thread(target=receive_messages, args=(sock, chat_window, chat_history), daemon=True).start()

    while True:
        input_window.clear()
        draw_input_window(input_window)
        msg = input_window.getstr(1, 18, width - 19).decode('utf-8')

        if msg.lower() == "/exit":
            break
        elif msg.lower() == "/help":
            log_message(chat_history, "Commands: /exit, /help, /clear, /history, /status, /msg")
        elif msg.lower() == "/clear":
            chat_history.clear()
            log_message(chat_history, "Chat cleared.")
        elif msg.lower() == "/history":
            log_message(chat_history, f"Chat History Loaded: {len(chat_history)} messages")
        elif msg.startswith("/status"):
            sock.sendall(f"/status {USERNAME} {msg.split()[1]}".encode('utf-8'))
            log_message(chat_history, f"Status set to {msg.split()[1]}")
        elif msg.startswith("/msg"):
            recipient, private_msg = msg.split()[1], " ".join(msg.split()[2:])
            sock.sendall(f"/msg {recipient} {private_msg}".encode('utf-8'))
            log_message(chat_history, f"Private message to {recipient}: {private_msg}")
        else:
            log_message(chat_history, msg, sender=USERNAME)
            sock.sendall(msg.encode('utf-8'))

        draw_chat_window(chat_window, chat_history)
        draw_input_window(input_window)

        if stdscr.getch() == curses.KEY_RESIZE:
            resize_windows(stdscr, chat_window, input_window)
            draw_chat_window(chat_window, chat_history)
            draw_input_window(input_window)

    sock.close()

curses.wrapper(main)