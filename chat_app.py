import curses

def main(stdscr):
    curses.curs_set(1)
    stdscr.clear()

    height, width = stdscr.getmaxyx()

    chat_window = curses.newwin(height - 3, width, 0, 0)
    input_window = curses.newwin(3, width, height - 3, 0)

    chat_history = []

    while True:
        input_window.clear()
        input_window.addstr(1, 1, "Type your message: ")
        input_window.refresh()

        msg = input_window.getstr(1, 18, width - 19).decode('utf-8')

        if msg.lower() == "/exit":
            break

        chat_history.append(f"You: {msg}")
        chat_window.clear()
        chat_window.addstr("\n".join(chat_history) + "\n")
        chat_window.refresh()

curses.wrapper(main)