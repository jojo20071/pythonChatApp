import curses
import socket
import threading

def receive_messages(sock, chat_window, chat_history):
    while True:
        msg = sock.recv(1024).decode('utf-8')
        chat_history.append(f"Friend: {msg}")
        chat_window.clear()
        chat_window.addstr("\n".join(chat_history) + "\n")
        chat_window.refresh()

def main(stdscr):
    curses.curs_set(1)
    stdscr.clear()

    height, width = stdscr.getmaxyx()

    chat_window = curses.newwin(height - 3, width, 0, 0)
    input_window = curses.newwin(3, width, height - 3, 0)

    chat_history = []

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 12345))

    threading.Thread(target=receive_messages, args=(sock, chat_window, chat_history), daemon=True).start()

    while True:
        input_window.clear()
        input_window.addstr(1, 1, "Type your message: ")
        input_window.refresh()

        msg = input_window.getstr(1, 18, width - 19).decode('utf-8')

        if msg.lower() == "/exit":
            break

        chat_history.append(f"You: {msg}")
        sock.sendall(msg.encode('utf-8'))
        chat_window.clear()
        chat_window.addstr("\n".join(chat_history) + "\n")
        chat_window.refresh()

curses.wrapper(main)
sock.close()