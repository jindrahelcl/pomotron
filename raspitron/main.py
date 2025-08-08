#!/usr/bin/env python3

import os
import curses
import time
import requests
import threading
import queue
import tempfile
import subprocess
import shutil
from typing import Optional, List
try:
    from gtts import gTTS  # type: ignore
    _GTTS_AVAILABLE = True
except Exception:
    _GTTS_AVAILABLE = False

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
        self.last_keypress_time = 0
        self.playback_delay = 0.3
        self.last_spoken_length = 0

        # TTS config
        self.tts_enabled = os.environ.get('RASPITRON_TTS', '1') != '0'
        self.tts_lang = os.environ.get('RASPITRON_TTS_LANG', 'en')
        self._tts_queue: "queue.Queue" = queue.Queue()
        self._tts_thread: Optional[threading.Thread] = None
        self._audio_player_cmd: Optional[List[str]] = self._detect_audio_player()
        if self.tts_enabled and not _GTTS_AVAILABLE:
            # gTTS is not installed; disable TTS gracefully
            self.tts_enabled = False
            self.log_action("TTS disabled: gTTS not available")
        if self.tts_enabled and self._audio_player_cmd is not None:
            self._start_tts_thread()

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

    def should_trigger_playback(self):
        if not self.current_line.strip():
            return False

        # Only trigger if there's new content to speak
        if len(self.current_line) <= self.last_spoken_length:
            return False

        # Immediate playback on sentence boundaries
        if self.current_line.endswith(('.', '!', '?')):
            return True

        # Debounced playback after typing stops
        time_since_last_key = time.time() - self.last_keypress_time
        if time_since_last_key > self.playback_delay and len(self.current_line.strip()) > 0:
            return True

        return False

    def trigger_playback(self):
        # Only speak the new part
        new_content = self.current_line[self.last_spoken_length:]
        if new_content.strip():
            self.log_action(f"Playback: '{new_content}'")
            self.last_spoken_length = len(self.current_line)

    def _detect_audio_player(self) -> Optional[List[str]]:
        # Prefer lightweight players available on Raspberry Pi / Linux
        if shutil.which('mpg123'):
            return ['mpg123', '-q']
        if shutil.which('ffplay'):
            return ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet']
        if shutil.which('mpv'):
            return ['mpv', '--really-quiet', '--no-video']
        return None

    def _start_tts_thread(self):
        self._tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self._tts_thread.start()

    def _tts_worker(self):
        while self.running:
            try:
                text = self._tts_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            if text is None:
                break
            if not text.strip():
                continue
            if self._audio_player_cmd is None:
                # Disable TTS if no player available
                self.tts_enabled = False
                continue
            try:
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                    tmp_path = tmp_file.name
                # Synthesize
                # Import here in case it was missing at startup but installed later
                if not _GTTS_AVAILABLE:
                    raise RuntimeError("gTTS not available")
                tts = gTTS(text=text, lang=self.tts_lang)
                tts.save(tmp_path)
                # Play
                subprocess.run(self._audio_player_cmd + [tmp_path], check=False)
            except Exception:
                # Swallow TTS errors to avoid breaking UI
                pass
            finally:
                try:
                    if 'tmp_path' in locals() and os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except Exception:
                    pass

    def enqueue_tts(self, text: str):
        if not self.tts_enabled:
            return
        if self._tts_thread is None and self._audio_player_cmd is not None:
            self._start_tts_thread()
        try:
            self._tts_queue.put_nowait(text)
        except Exception:
            pass

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
                # Speak the response
                self.enqueue_tts(bot_response)
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
        self.last_keypress_time = time.time()

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
                self.last_spoken_length = 0
                content_win.addstr("\n")
                self.send_message(message, content_win)
            else:
                content_win.addstr("\n> ")
        elif key_code == 127 or key_code == 8:  # Backspace
            if self.cursor_pos > 0:
                deleted_char = self.current_line[self.cursor_pos-1]
                self.current_line = self.current_line[:self.cursor_pos-1] + self.current_line[self.cursor_pos:]
                self.cursor_pos -= 1
                # Reset spoken length if we backspace past it
                if self.cursor_pos < self.last_spoken_length:
                    self.last_spoken_length = self.cursor_pos
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

            # Check for immediate playback on sentence end
            if self.should_trigger_playback():
                self.trigger_playback()

        elif 128 <= key_code <= 255:  # UTF-8 bytes
            self.utf8_buffer.append(key_code)
            try:
                # Try to decode the buffer as UTF-8
                char = bytes(self.utf8_buffer).decode('utf-8')
                self.current_line = self.current_line[:self.cursor_pos] + char + self.current_line[self.cursor_pos:]
                self.cursor_pos += 1
                self.redraw_line(content_win)
                self.utf8_buffer = []  # Clear buffer on success

                # Check for immediate playback on sentence end
                if self.should_trigger_playback():
                    self.trigger_playback()

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
            else:
                # Check for debounced playback when no keys are pressed
                if self.should_trigger_playback():
                    self.trigger_playback()
            time.sleep(0.01)

        # Graceful shutdown of TTS thread
        try:
            if self._tts_thread is not None:
                self._tts_queue.put_nowait(None)  # sentinel
                self._tts_thread.join(timeout=1.0)
        except Exception:
            pass

def main():
    app = RaspiTRON()
    curses.wrapper(app.run)

if __name__ == "__main__":
    main()
