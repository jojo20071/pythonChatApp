import curses
import socket
import threading
import datetime

def receive_messages(sock, chat_window, chat_history):
    while True:
        msg = sock.recv(1024).decode('utf-8')
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        chat_history.append(f"[{timestamp}] Friend: {msg}")
        chat_window.clear()
        chat_window.border()
        chat_window.addstr(1, 2, "\n".join(chat_history) + "\n")
        chat_window.refresh()

def main(stdscr):
    curses.curs_set(1)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

    stdscr.clear()
    height, width = stdscr.getmaxyx()

    chat_window = curses.newwin(height - 5, width, 0, 0)
    input_window = curses.newwin(3, width, height - 5, 0)
    status_window = curses.newwin(1, width, height - 2, 0)

    chat_window.border()
    input_window.border()

    chat_history = []

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 12345))

    threading.Thread(target=receive_messages, args=(sock, chat_window, chat_history), daemon=True).start()

    username = "You"

    while True:
        status_window.clear()
        status_window.addstr(0, 1, "Press /exit to leave the chat, /help for commands", curses.color_pair(1))
        status_window.refresh()

        input_window.clear()
        input_window.addstr(1, 1, "Type your message: ")
        input_window.refresh()

        msg = input_window.getstr(1, 18, width - 19).decode('utf-8')

        if msg.lower() == "/exit":
            break
        elif msg.lower() == "/help":
            chat_history.append("Commands: /exit, /help")
        else:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            chat_history.append(f"[{timestamp}] {username}: {msg}")
            sock.sendall(msg.encode('utf-8'))
        
        chat_window.clear()
        chat_window.border()
        chat_window.addstr(1, 2, "\n".join(chat_history) + "\n")
        chat_window.refresh()

curses.wrapper(main)
sock.close()