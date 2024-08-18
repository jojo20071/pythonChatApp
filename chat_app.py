import curses
import logging
import os
import socket
import threading

def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logging.basicConfig(filename='logs/chat_app.log', level=logging.DEBUG, 
                        format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def authenticate_user(input_window, width):
    input_window.clear()
    input_window.addstr(1, 1, "Enter username: ")
    input_window.refresh()
    username = input_window.getstr(1, 18, width - 19).decode('utf-8')
    logging.info(f"User '{username}' logged in.")
    return username

def receive_messages(sock, chat_window):
    while True:
        try:
            msg = sock.recv(1024).decode('utf-8')
            chat_window.addstr(msg + "\n")
            chat_window.refresh()
        except:
            break

def main(stdscr):
    curses.curs_set(1)
    stdscr.clear()
    setup_logging()

    height, width = stdscr.getmaxyx()

    chat_window = curses.newwin(height - 8, width, 0, 0)
    input_window = curses.newwin(3, width, height - 5, 0)
    status_window = curses.newwin(5, width, height - 8, 0)

    chat_window.scrollok(True)
    chat_window.border()
    input_window.border()
    status_window.border()

    username = authenticate_user(input_window, width)
    user_info = f"Logged in as: {username}"
    status_window.addstr(1, 1, user_info)
    status_window.refresh()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 12345))

    threading.Thread(target=receive_messages, args=(sock, chat_window), daemon=True).start()

    while True:
        input_window.clear()
        input_window.addstr(1, 1, f"{username}: ")
        input_window.refresh()

        msg = input_window.getstr(1, len(username) + 2, width - len(username) - 3).decode('utf-8')

        if msg.lower() == "/exit":
            logging.info(f"User '{username}' exited the chat.")
            break
        elif msg.startswith("/whisper "):
            target, private_msg = msg[9:].split(' ', 1)
            formatted_msg = f"(Private) {username} to {target}: {private_msg}"
        else:
            formatted_msg = f"{username}: {msg}"
        
        sock.sendall(formatted_msg.encode('utf-8'))
        logging.info(formatted_msg)
        
        chat_window.addstr(formatted_msg + "\n")
        chat_window.refresh()

curses.wrapper(main)
sock.close()