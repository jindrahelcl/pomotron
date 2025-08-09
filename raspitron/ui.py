import curses

class RaspiTRONUI:
    def __init__(self):
        self.main_win = None
        self.log_win = None
        self.log_content = None

    def setup_windows(self, stdscr):
        height, width = stdscr.getmaxyx()

        # Create main window (left half)
        self.main_win = curses.newwin(height, width // 2, 0, 0)

        # Create log window (right half)
        self.log_win = curses.newwin(height, width - width // 2, 0, width // 2)

        # Add borders
        self.main_win.box()
        self.log_win.box()

        # Add titles
        self.main_win.addstr(0, 2, " RaspiTRON ")
        self.log_win.addstr(0, 2, " Action Log ")

        self.main_win.refresh()
        self.log_win.refresh()

        main_content = self.main_win.derwin(height-2, width//2-2, 1, 1)
        self.log_content = self.log_win.derwin(height-2, width-width//2-2, 1, 1)

        return main_content, self.log_content

    def log_action(self, action: str):
        if self.log_content:
            try:
                max_y, max_x = self.log_content.getmaxyx()
                cur_y, cur_x = self.log_content.getyx()
                if cur_y >= max_y - 1:
                    self.log_content.scroll()
                    self.log_content.move(max_y - 1, 0)
                message = f" {action}\n"
                if len(message) > max_x - 1:
                    message = message[:max_x - 4] + "...\n"
                self.log_content.addstr(message)
                self.log_content.refresh()
            except curses.error:
                pass

    def redraw_line(self, content_win, current_line, cursor_pos, last_spoken_length):
        try:
            y, x = content_win.getyx()
            max_y, max_x = content_win.getmaxyx()
            if y >= max_y:
                y = max_y - 1
            try:
                content_win.move(y, 2)
            except curses.error:
                pass
            content_win.clrtoeol()
            display_line = current_line
            if len(display_line) > max_x - 3:
                display_line = display_line[:max_x - 6] + "..."
            content_win.addstr(display_line)
            cursor_x = min(2 + cursor_pos, max_x - 1)
            try:
                content_win.move(y, cursor_x)
            except curses.error:
                pass
        except curses.error:
            pass
