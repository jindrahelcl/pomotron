#!/usr/bin/env python3

import sys
import termios
import tty
import select
import time


class TerminalInterface:
    """Handles terminal input/output and provides a rich command-line interface"""

    def __init__(self):
        self.running = True
        self.current_line = ""
        self.cursor_pos = 0
        self.sentence_start = 0
        self.multi_sentence = False
        self.old_settings = None

    def setup_terminal(self):
        """Setup terminal for raw input mode"""
        try:
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
        except Exception as e:
            print(f"Error setting up terminal: {e}")

    def restore_terminal(self):
        """Restore terminal to original settings"""
        if self.old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

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

    def redraw_line(self):
        """Clear line and redraw with cursor at correct position"""
        sys.stdout.write('\r> ' + self.current_line)
        # Move cursor to correct position
        if self.cursor_pos < len(self.current_line):
            # Move cursor back to correct position
            move_back = len(self.current_line) - self.cursor_pos
            sys.stdout.write('\b' * move_back)
        sys.stdout.flush()

    def handle_escape_sequence(self):
        """Handle escape sequences (arrow keys, home, end, etc.)"""
        # Read the escape sequence
        char2 = sys.stdin.read(1)
        if ord(char2) == 91:  # '[' - standard escape sequence
            char3 = sys.stdin.read(1)
            key_code = ord(char3)
            return key_code
        return None

    def handle_backspace(self):
        """Handle backspace key"""
        if self.cursor_pos > 0:
            self.current_line = self.current_line[:self.cursor_pos-1] + self.current_line[self.cursor_pos:]
            self.cursor_pos -= 1
            self.sentence_start = min(self.sentence_start, self.cursor_pos)
            self.redraw_line()

    def handle_arrow_key(self, arrow_key):
        """Handle arrow key navigation"""
        if arrow_key == 67:  # Right arrow
            if self.cursor_pos < len(self.current_line):
                self.cursor_pos += 1
                self.redraw_line()
        elif arrow_key == 68:  # Left arrow
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
                self.redraw_line()
        elif arrow_key == 72:  # Home
            self.cursor_pos = 0
            self.redraw_line()
        elif arrow_key == 70:  # End
            self.cursor_pos = len(self.current_line)
            self.redraw_line()

    def insert_character(self, char):
        """Insert character at cursor position"""
        self.current_line = self.current_line[:self.cursor_pos] + char + self.current_line[self.cursor_pos:]
        self.cursor_pos += 1
        self.redraw_line()

    def is_sentence_end(self, char):
        """Check if character marks end of sentence"""
        return char in '.!?'

    def get_current_sentence(self):
        """Get current sentence from sentence_start to current position"""
        return self.current_line[self.sentence_start:]

    def mark_sentence_end(self):
        """Mark end of current sentence and prepare for next"""
        self.multi_sentence = (self.sentence_start > 0)
        self.sentence_start = len(self.current_line)

    def reset_input(self):
        """Reset input state for new line"""
        self.current_line = ""
        self.cursor_pos = 0
        self.sentence_start = 0
        self.multi_sentence = False

    def should_speak_line(self):
        """Check if the full line should be spoken (multi-sentence or partial sentence)"""
        return self.multi_sentence or self.sentence_start != len(self.current_line)

    def print_prompt(self):
        """Print the input prompt"""
        print("\r\n> ", end="", flush=True)

    def print_message(self, message, end="\r\n"):
        """Print a message with proper line ending"""
        print(f"\r{message}", end=end)

    def run_input_loop(self, on_character=None, on_sentence=None, on_line=None, on_quit=None):
        """
        Main input loop that handles terminal input

        Args:
            on_character: callback(char) - called for each character typed
            on_sentence: callback(sentence) - called when sentence ends
            on_line: callback(line) - called when line is complete (Enter pressed)
            on_quit: callback() - called when user wants to quit
        """
        try:
            self.setup_terminal()

            while self.running:
                if select.select([sys.stdin], [], [], 0.01)[0]:
                    char = sys.stdin.read(1)
                    key_code = ord(char)

                    if key_code == ord('q') and not self.current_line:
                        self.print_message("Goodbye!")
                        if on_quit:
                            on_quit()
                        break

                    elif key_code == 13 or key_code == 10:  # Enter
                        if self.current_line.strip():
                            print()  # New line after input
                            if on_line:
                                on_line(self.current_line.strip(), self.should_speak_line())
                            self.reset_input()
                            self.print_prompt()
                        else:
                            self.print_prompt()

                    elif key_code == 127 or key_code == 8:  # Backspace
                        self.handle_backspace()

                    elif key_code == 27:  # ESC - arrow keys, home, end
                        arrow_key = self.handle_escape_sequence()
                        if arrow_key:
                            self.handle_arrow_key(arrow_key)

                    else:
                        char_str = chr(key_code)
                        self.insert_character(char_str)

                        if on_character:
                            on_character(char_str)

                        # Handle sentence end
                        if self.is_sentence_end(char_str):
                            if on_sentence:
                                on_sentence(self.get_current_sentence())
                            self.mark_sentence_end()

                time.sleep(0.01)

        except KeyboardInterrupt:
            self.print_message("Pro ukončení stiskni q")
        finally:
            self.restore_terminal()

    def stop(self):
        """Stop the input loop"""
        self.running = False
