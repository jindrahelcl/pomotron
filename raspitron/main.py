#!/usr/bin/env python3

import os
import requests
from tts import create_tts_manager
try:
    from player import BeePlayer
except ModuleNotFoundError:
    BeePlayer = None
from math import pi
import threading
import geiger
from terminal import TerminalInterface

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
        self.terminal = TerminalInterface()

    def send_message(self, message: str):
        self.terminal.print_message(f"[Sending: {message}]")
        stop_event = threading.Event()
        geiger_thread = threading.Thread(target=geiger.run, args=(stop_event,))
        geiger_thread.start()
        def stop_geiger(success=True):
            stop_event.set()
            geiger_thread.join()
            if success:
                self.beep()
        data = None
        try:
            response = requests.post(
                f"{self.storytron_url}/api/chat",
                json={"message": message},
                # Separate connect and read timeouts: (connect, read)
                timeout=(5, self.request_timeout)
            )
            if response.status_code == 200:
                data = response.json()
            else:
                error = f"Server error: {response.status_code}"
                self.terminal.print_message(error)
        except requests.exceptions.RequestException as e:
            error = f"Connection error: {e}"
            self.terminal.print_message(error)

        if data:
            bot_response = data.get('agent_response', 'No response')
            agent = data.get('active_agent', 'bot')
            self.terminal.print_message(f"{agent}: {bot_response}")
            self.tts.say(bot_response, agent=agent, cb=stop_geiger)
        else:
            stop_geiger(beep=False)

        # Wait for the tts to say what it wants to say
        self.tts.join()

    def beep(self):
        if not BeePlayer:
            return
        player = BeePlayer(d=5, v=640/3.6, omega=2*pi*220)
        player.open()
        player.play(-0.02, 0.02)
        player.close()

    def on_line_complete(self, line, should_speak):
        """Callback when user completes a line input"""
        if should_speak:
            self.tts.say(line, agent="pomo")
        self.tts.join()
        self.send_message(line)

    def on_sentence_complete(self, sentence):
        """Callback when user completes a sentence"""
        self.tts.say(sentence, agent="pomo")

    def on_quit(self):
        """Callback when user wants to quit"""
        self.running = False

    def run(self):
        print("RaspiTRON - Simple Chat Interface")
        print("Type your message and press Enter. Type 'q' to quit.")
        print("=" * 50)

        self.terminal.print_prompt()

        self.terminal.run_input_loop(
            on_sentence=self.on_sentence_complete,
            on_line=self.on_line_complete,
            on_quit=self.on_quit
        )

        self.tts.shutdown()

def main():
    app = RaspiTRON()
    app.run()

if __name__ == "__main__":
    main()
