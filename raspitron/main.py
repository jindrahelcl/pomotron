#!/usr/bin/env python3

import os
import curses
import time
import requests

class RaspiTRON:
    def __init__(self):
        self.storytron_url = os.environ.get('STORYTRON_URL', 'https://reggnox.cz/pomotron')
        self.running = True
        self.current_line = ""
        self.cursor_pos = 0
        self.utf8_buffer = []
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
            self.log_content.addstr(f" {action}\n")
            self.log_content.refresh()

    def send_message(self, message: str, content_win):
        try:
            url = f"{self.storytron_url}/api/chat"
            self.log_action(f"Sending to: {url}")
            response = requests.post(
                url,
                json={"message": message},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                bot_response = data.get('agent_response', 'No response received')
                content_win.addstr(f"{bot_response}\n> ")
                self.log_action(f"Response from {data.get('active_agent', 'unknown')}: '{bot_response}'")
            else:
                error_msg = f"Server error: {response.status_code}"
                content_win.addstr(f"{error_msg}\n> ")
                self.log_action(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {str(e)}"
            content_win.addstr(f"{error_msg}\n> ")
            self.log_action(error_msg)

    def redraw_line(self, content_win):
        y, x = content_win.getyx()
        content_win.move(y, 2)  # Move to after "> "
        content_win.clrtoeol()  # Clear rest of line
        content_win.addstr(self.current_line)
        content_win.move(y, 2 + self.cursor_pos)  # Position cursor correctly

    def handle_keypress(self, key_code: int, content_win):
        if key_code == ord('q'):
            self.running = False
            self.log_action("User quit application")
            return

        if key_code == ord('\n') or key_code == 10:  # Enter
            if self.current_line.strip():  # Only send non-empty messages
                self.log_action(f"Message sent: '{self.current_line}'")
                message = self.current_line
                self.current_line = ""
                self.cursor_pos = 0
                content_win.addstr("\n")
                self.send_message(message, content_win)
            else:
                content_win.addstr("\n> ")
        elif key_code == 127 or key_code == 8:  # Backspace
            if self.cursor_pos > 0:
                deleted_char = self.current_line[self.cursor_pos-1]
                self.current_line = self.current_line[:self.cursor_pos-1] + self.current_line[self.cursor_pos:]
                self.cursor_pos -= 1
                self.redraw_line(content_win)
        elif key_code == curses.KEY_LEFT:
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
                y, x = content_win.getyx()
                content_win.move(y, x - 1)
        elif key_code == curses.KEY_RIGHT:
            if self.cursor_pos < len(self.current_line):
                self.cursor_pos += 1
                y, x = content_win.getyx()
                content_win.move(y, x + 1)
        elif key_code == curses.KEY_HOME:
            self.cursor_pos = 0
            y, x = content_win.getyx()
            content_win.move(y, 2)  # Move to after "> "
        elif key_code == curses.KEY_END:
            self.cursor_pos = len(self.current_line)
            y, x = content_win.getyx()
            content_win.move(y, 2 + len(self.current_line))
        elif 32 <= key_code <= 126:  # ASCII printable characters
            char = chr(key_code)
            self.current_line = self.current_line[:self.cursor_pos] + char + self.current_line[self.cursor_pos:]
            self.cursor_pos += 1
            self.redraw_line(content_win)
        elif 128 <= key_code <= 255:  # UTF-8 bytes
            self.utf8_buffer.append(key_code)
            try:
                # Try to decode the buffer as UTF-8
                char = bytes(self.utf8_buffer).decode('utf-8')
                self.current_line = self.current_line[:self.cursor_pos] + char + self.current_line[self.cursor_pos:]
                self.cursor_pos += 1
                self.redraw_line(content_win)
                self.utf8_buffer = []  # Clear buffer on success
            except UnicodeDecodeError:
                # Need more bytes, keep collecting
                if len(self.utf8_buffer) > 4:  # UTF-8 max is 4 bytes
                    self.utf8_buffer = []  # Reset if too long
        else:
            content_win.addstr(f" [KEY:{key_code}]")
            self.log_action(f"Special key pressed: {key_code}")

        content_win.refresh()

    def run(self, stdscr):
        stdscr.nodelay(True)
        stdscr.clear()

        # Setup split windows
        main_content, log_content = self.setup_windows(stdscr)
        main_content.nodelay(True)

        # Initial messages
        main_content.addstr("RaspiTRON started.\n")
        main_content.addstr("Type something, press Enter to submit, 'q' to quit.\n")
        main_content.addstr("> ")
        main_content.refresh()

        # Position log window cursor properly
        self.log_action("RaspiTRON initialized")
        self.log_action("Split window layout created")

        while self.running:
            key = main_content.getch()
            if key != -1:
                self.handle_keypress(key, main_content)
            time.sleep(0.01)

def main():
    app = RaspiTRON()
    curses.wrapper(app.run)

if __name__ == "__main__":
    main()
