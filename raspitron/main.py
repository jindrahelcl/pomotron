#!/usr/bin/env python3

from dotenv import load_dotenv
import os
import sys
import requests
import time
from prompt import Session
from sounds import sounds
from tts import create_tts_manager
try:
    from player import BeePlayer
except ModuleNotFoundError:
    BeePlayer = None
from math import pi
import threading
if os.environ.get('DISABLE_GEIGER', '0') != "1":
    import geiger
else:
    import types
    geiger = types.ModuleType("geiger")
    def run(stop_event):
        stop_event.wait()
    geiger.run = run

load_dotenv()

class RaspiTRON:
    def __init__(self):
        self.storytron_url = os.environ.get('STORYTRON_URL', 'https://pomotron.cz')
        # HTTP read timeout for StoryTRON requests (seconds)
        # Can be overridden via env var STORYTRON_TIMEOUT
        try:
            self.request_timeout = float(os.environ.get('STORYTRON_TIMEOUT', '30'))
        except ValueError:
            self.request_timeout = 30.0

        # Pomo agent TTS configuration
        self.pomo_tts_engine = os.environ.get('POMO_TTS_ENGINE', 'festival')
        self.pomo_tts_voice = os.environ.get('POMO_TTS_VOICE', "ph")
        self.disable_sentence_echo = (os.environ.get("DISABLE_SENTENCE_ECHO", "1") == "1")

    def send_message(self, message: str):
        print("\r")
        print(f"[Sending: {message}]", file=sys.stderr, end="\r\n")
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
                print(f"{error}", end="\r\n")
        except requests.exceptions.RequestException as e:
            error = f"Connection error: {e}"
            print(f"{error}", end="\r\n")

        if data:
            bot_response = data.get('agent_response', 'No response')
            agent = data.get('active_agent', 'bot')
            tts_engine = data.get('tts_engine', 'gtts')
            tts_voice = data.get('tts_voice', None)
            print(f"{agent}: {bot_response}", end="\r\n")
            sounds.play_boop()
            self.tts.say(bot_response, agent=agent, cb=stop_geiger, engine_type=tts_engine, voice=tts_voice)
        else:
            stop_geiger(success=False)

        # Wait for the tts to say what it wants to say
        self.tts.join()

    def beep(self):
        if not BeePlayer:
            return
        player = BeePlayer(d=5, v=640/3.6, omega=2*pi*220)
        player.open()
        player.play(-0.02, 0.02)
        player.close()

    def run(self):
        self.tts = create_tts_manager()
        self.session = Session()
        sounds.play_beep_startup()
        try:
            while True:
                line = self.session.prompt().strip()
                if not line:
                    continue

                self.tts.say(line, agent="pomo", engine_type=self.pomo_tts_engine, voice=self.pomo_tts_voice)
                sounds.play_beep()
                self.tts.join()
                self.send_message(line)
        except EOFError:
            sounds.play_reload()
            time.sleep(0.5)
        finally:
            self.tts.shutdown()

def main():
    app = RaspiTRON()
    app.run()

if __name__ == "__main__":
    main()
