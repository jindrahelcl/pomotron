#!/usr/bin/env python3

import sys
import time
import platform
from abc import ABC, abstractmethod

# Platform-specific imports
if platform.system() != 'Windows':
    import termios
    import tty
    import select
else:
    import msvcrt


class BaseTerminalInterface(ABC):
    """Abstract base class for terminal interfaces"""

    def __init__(self):
        self.running = True
        self.current_line = ""
        self.cursor_pos = 0
        self.sentence_start = 0
        self.multi_sentence = False

    @abstractmethod
    def setup_terminal(self):
        """Setup terminal for raw input mode"""
        pass

    @abstractmethod
    def restore_terminal(self):
        """Restore terminal to original settings"""
        pass

    @abstractmethod
    def get_char_if_available(self):
        """Get a character if available, return None if not"""
        pass

    @abstractmethod
    def handle_special_key(self, key_code):
        """Handle special keys (arrows, backspace, etc.), return True if handled"""
        pass

    def redraw_line(self):
        """Clear line and redraw with cursor at correct position"""
        sys.stdout.write('\r> ' + self.current_line)
        # Move cursor to correct position
        if self.cursor_pos < len(self.current_line):
            # Move cursor back to correct position
            move_back = len(self.current_line) - self.cursor_pos
            sys.stdout.write('\b' * move_back)
        sys.stdout.flush()

    def handle_backspace(self):
        """Handle backspace key"""
        if self.cursor_pos > 0:
            self.current_line = self.current_line[:self.cursor_pos-1] + self.current_line[self.cursor_pos:]
            self.cursor_pos -= 1
            self.sentence_start = min(self.sentence_start, self.cursor_pos)
            self.redraw_line()

    def handle_arrow_key(self, direction):
        """Handle arrow key navigation"""
        if direction == 'right':
            if self.cursor_pos < len(self.current_line):
                self.cursor_pos += 1
                self.redraw_line()
        elif direction == 'left':
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
                self.redraw_line()
        elif direction == 'home':
            self.cursor_pos = 0
            self.redraw_line()
        elif direction == 'end':
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
                char = self.get_char_if_available()
                if char is not None:
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

                    elif not self.handle_special_key(key_code):
                        # Regular character
                        if 32 <= key_code <= 126:  # Printable ASCII
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


class UnixTerminalInterface(BaseTerminalInterface):
    """Unix/Linux terminal interface implementation"""

    def __init__(self):
        super().__init__()
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

    def get_char_if_available(self):
        """Get a character if available, return None if not"""
        if select.select([sys.stdin], [], [], 0.01)[0]:
            return sys.stdin.read(1)
        return None

    def handle_special_key(self, key_code):
        """Handle special keys (arrows, backspace, etc.), return True if handled"""
        if key_code == 127 or key_code == 8:  # Backspace
            self.handle_backspace()
            return True
        elif key_code == 27:  # ESC - arrow keys, home, end
            arrow_key = self._handle_escape_sequence()
            if arrow_key:
                self._handle_unix_arrow_key(arrow_key)
            return True
        return False

    def _handle_escape_sequence(self):
        """Handle escape sequences (arrow keys, home, end, etc.)"""
        # Read the escape sequence
        char2 = sys.stdin.read(1)
        if ord(char2) == 91:  # '[' - standard escape sequence
            char3 = sys.stdin.read(1)
            key_code = ord(char3)
            return key_code
        return None

    def _handle_unix_arrow_key(self, arrow_key):
        """Handle Unix arrow key codes"""
        if arrow_key == 67:  # Right arrow
            self.handle_arrow_key('right')
        elif arrow_key == 68:  # Left arrow
            self.handle_arrow_key('left')
        elif arrow_key == 72:  # Home
            self.handle_arrow_key('home')
        elif arrow_key == 70:  # End
            self.handle_arrow_key('end')


class WindowsTerminalInterface(BaseTerminalInterface):
    """Windows terminal interface implementation"""

    def __init__(self):
        super().__init__()

    def setup_terminal(self):
        """Setup terminal for raw input mode"""
        # Windows terminal is already in the right mode for msvcrt
        pass

    def restore_terminal(self):
        """Restore terminal to original settings"""
        # No restoration needed on Windows
        pass

    def get_char_if_available(self):
        """Get a character if available, return None if not"""
        if msvcrt.kbhit():
            return msvcrt.getch().decode('utf-8', errors='ignore')
        return None

    def handle_special_key(self, key_code):
        """Handle special keys (arrows, backspace, etc.), return True if handled"""
        if key_code == 8:  # Backspace
            self.handle_backspace()
            return True
        elif key_code == 224:  # Special key prefix on Windows
            # Read the second byte for arrow keys
            if msvcrt.kbhit():
                second_key = ord(msvcrt.getch())
                self._handle_windows_arrow_key(second_key)
            return True
        return False

    def _handle_windows_arrow_key(self, second_key):
        """Handle Windows arrow key codes"""
        if second_key == 77:  # Right arrow
            self.handle_arrow_key('right')
        elif second_key == 75:  # Left arrow
            self.handle_arrow_key('left')
        elif second_key == 71:  # Home
            self.handle_arrow_key('home')
        elif second_key == 79:  # End
            self.handle_arrow_key('end')


def create_terminal_interface():
    """Factory function to create the appropriate terminal interface"""
    if platform.system() == 'Windows':
        return WindowsTerminalInterface()
    else:
        return UnixTerminalInterface()


# Backward compatibility
TerminalInterface = create_terminal_interface
