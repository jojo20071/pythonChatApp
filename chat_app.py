import curses
import datetime
import os

CHAT_LOG_FILE = "chat_log.txt"

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

def main(stdscr):
    curses.curs_set(1)
    stdscr.clear()

    height, width = stdscr.getmaxyx()

    chat_window = curses.newwin(height - 3, width, 0, 0)
    input_window = curses.newwin(3, width, height - 3, 0)

    chat_history = load_chat_history()
    if not chat_history:
        chat_history.append("Welcome to the Python Chat!\n")

    draw_chat_window(chat_window, chat_history)
    draw_input_window(input_window)

    while True:
        input_window.clear()
        draw_input_window(input_window)
        msg = input_window.getstr(1, 18, width - 19).decode('utf-8')

        if msg.lower() == "/exit":
            break
        elif msg.lower() == "/help":
            log_message(chat_history, "Commands: /exit, /help, /clear, /history")
        elif msg.lower() == "/clear":
            chat_history.clear()
            log_message(chat_history, "Chat cleared.")
        elif msg.lower() == "/history":
            log_message(chat_history, f"Chat History Loaded: {len(chat_history)} messages")
        else:
            log_message(chat_history, msg)

        draw_chat_window(chat_window, chat_history)
        draw_input_window(input_window)

        if stdscr.getch() == curses.KEY_RESIZE:
            resize_windows(stdscr, chat_window, input_window)
            draw_chat_window(chat_window, chat_history)
            draw_input_window(input_window)

curses.wrapper(main)