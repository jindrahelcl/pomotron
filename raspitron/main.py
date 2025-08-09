#!/usr/bin/env python3

import os
import sys
import time
import requests
import termios
import tty
import select
from tts import create_tts_manager

class RaspiTRON:
    def __init__(self):
        self.storytron_url = os.environ.get('STORYTRON_URL', 'https://pomotron.cz')
        # HTTP read timeout for StoryTRON requests (seconds)
        # Can be overridden via env var STORYTRON_TIMEOUT
        try:
            self.request_timeout = float(os.environ.get('STORYTRON_TIMEOUT', '30'))
        except ValueError:
            self.request_timeout = 30.0
        self.running = True
        self.tts = create_tts_manager()

    def send_message(self, message: str):
        print("\r")
        print(f"[Sending: {message}]", file=sys.stderr, end="\r\n")
        try:
            response = requests.post(
                f"{self.storytron_url}/api/chat",
                json={"message": message},
                # Separate connect and read timeouts: (connect, read)
                timeout=(5, self.request_timeout)
            )
            if response.status_code == 200:
                data = response.json()
                bot_response = data.get('agent_response', 'No response')
                agent = data.get('active_agent', 'bot')
                print(f"{agent}: {bot_response}", end="\r\n")
                self.tts.say(bot_response)
            else:
                error = f"Server error: {response.status_code}"
                print(f"{error}", end="\r\n")
        except requests.exceptions.RequestException as e:
            error = f"Connection error: {e}"
            print(f"{error}", end="\r\n")

    def get_char(self):
        """Get a single character from stdin without waiting for Enter"""
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            if select.select([sys.stdin], [], [], 0.01)[0]:
                return sys.stdin.read(1)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        return None

    def run(self):
        print("RaspiTRON - Simple Chat Interface")
        print("Type your message and press Enter. Type 'q' to quit.")
        print("=" * 50)

        current_line = ""
        cursor_pos = 0

        def redraw_line():
            # Clear line and redraw with cursor at correct position
            sys.stdout.write('\r> ' + current_line)
            # Move cursor to correct position
            if cursor_pos < len(current_line):
                # Move cursor back to correct position
                move_back = len(current_line) - cursor_pos
                sys.stdout.write('\b' * move_back)
            sys.stdout.flush()

        def handle_escape_sequence():
            # Read the escape sequence
            char2 = sys.stdin.read(1)
            if ord(char2) == 91:  # '[' - standard escape sequence
                char3 = sys.stdin.read(1)
                key_code = ord(char3)
                return key_code
            return None

        try:
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())

            while self.running:
                if select.select([sys.stdin], [], [], 0.01)[0]:
                    char = sys.stdin.read(1)
                    key_code = ord(char)

                    if key_code == ord('q') and not current_line:
                        print("\r\nGoodbye!", end="\r\n")
                        break
                    elif key_code == 13 or key_code == 10:  # Enter
                        if current_line.strip():
                            print()  # New line after input
                            self.send_message(current_line.strip())
                            current_line = ""
                            cursor_pos = 0
                            print("\r\n> ", end="", flush=True)
                        else:
                            print("\r\n> ", end="", flush=True)
                    elif key_code == 127 or key_code == 8:  # Backspace
                        if cursor_pos > 0:
                            current_line = current_line[:cursor_pos-1] + current_line[cursor_pos:]
                            cursor_pos -= 1
                            redraw_line()
                    elif key_code == 27:  # ESC - arrow keys, home, end
                        arrow_key = handle_escape_sequence()
                        if arrow_key == 67:  # Right arrow
                            if cursor_pos < len(current_line):
                                cursor_pos += 1
                                redraw_line()
                        elif arrow_key == 68:  # Left arrow
                            if cursor_pos > 0:
                                cursor_pos -= 1
                                redraw_line()
                        elif arrow_key == 72:  # Home
                            cursor_pos = 0
                            redraw_line()
                        elif arrow_key == 70:  # End
                            cursor_pos = len(current_line)
                            redraw_line()
                    elif 32 <= key_code <= 126:  # Printable characters
                        char = chr(key_code)
                        # Insert character at cursor position
                        current_line = current_line[:cursor_pos] + char + current_line[cursor_pos:]
                        cursor_pos += 1
                        redraw_line()

                        # Speak on sentence end
                        if char in '.!?':
                            self.tts.say(current_line)

                time.sleep(0.01)

        except KeyboardInterrupt:
            print("\r\nPro ukončení stiskni q", end="\r\n")
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            self.tts.shutdown()

def main():
    app = RaspiTRON()
    print("\n> ", end="", flush=True)
    app.run()

if __name__ == "__main__":
    main()
