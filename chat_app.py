import curses

def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()

    height, width = stdscr.getmaxyx()

    chat_window = curses.newwin(height - 3, width, 0, 0)
    input_window = curses.newwin(3, width, height - 3, 0)

    input_window.addstr(1, 1, "Type your message: ")

    chat_window.refresh()
    input_window.refresh()

    stdscr.getch()

curses.wrapper(main)