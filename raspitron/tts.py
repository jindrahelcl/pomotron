#!/usr/bin/env python3

import os
import sys
import threading
import queue
import tempfile
import subprocess
import shutil
from typing import Optional, List

try:
    from gtts import gTTS
    _GTTS_AVAILABLE = True
except Exception:
    _GTTS_AVAILABLE = False

class TtsEngine:
    """Base TTS engine interface"""
    def __init__(self, lang: str = 'en'):
        self.lang = lang

    def synthesize(self, text: str, filename: str, agent: str):
        """Synthesize text to audio file"""
        raise NotImplementedError

class GttsEngine(TtsEngine):
    """Google Text-to-Speech engine"""
    def synthesize(self, text: str, filename: str, agent: str):
        if not _GTTS_AVAILABLE:
            raise RuntimeError("gTTS not available")
        tts = gTTS(text=text, lang=self.lang)
        tts.save(filename)

class FestivalEngine(TtsEngine):
    """Festival TTS engine for Czech"""
    def __init__(self, voice: str = "machac"):
        super().__init__('cs')
        self.voice_cmd = self.get_voice_cmd(voice)

    def get_voice_cmd(self, voice: str):
        return {
            "krb": "(voice_czech_krb)",
            "dita": "(voice_czech_dita)",
            "machac": "(voice_czech_machac)",
            "ph": "(voice_czech_ph)",
        }.get(voice, "(voice_czech_krb)")

    def agent_to_voice(self, agent: str):
        return {
            "confessor": "krb",
            "tradicni": "dita",
            "pomo": "dita",
        }.get(agent, "machac")

    def synthesize(self, text: str, filename: str, agent: str):
        encoded_text = text.encode('iso8859-2', errors='ignore')
        with open(filename, 'wb') as outfile:
            voice = self.agent_to_voice(agent)
            voice_cmd = self.get_voice_cmd(voice)
            text2wave_proc = subprocess.Popen(
                ['text2wave', '-eval', voice_cmd],
                stdin=subprocess.PIPE,
                stdout=outfile
            )
            text2wave_proc.stdin.write(encoded_text)
            text2wave_proc.stdin.close()
            text2wave_proc.wait()

class TtsManager:
    """Manages TTS functionality with background processing"""

    def __init__(self, lang: str = 'en', engine_type: str = 'gtts'):
        self.running = True
        self.enabled = os.environ.get('RASPITRON_TTS', '1') != '0'
        self.lang = lang

        # Initialize engine
        if engine_type == 'festival':
            self.engine = FestivalEngine()
        else:
            self.engine = GttsEngine(lang)

        # Setup audio player
        self._audio_player_cmd = self._detect_audio_player()

        # Setup background processing
        self._tts_queue = queue.Queue()
        self._tts_thread = None

        # Initialize if everything is available
        if self.enabled:
            if not self._audio_player_cmd:
                self.enabled = False
                print("[TTS disabled: no audio player found]", file=sys.stderr)
            elif engine_type == 'gtts' and not _GTTS_AVAILABLE:
                self.enabled = False
                print("[TTS disabled: gTTS not available]", file=sys.stderr)
            else:
                self._start_worker_thread()

    def _detect_audio_player(self) -> Optional[List[str]]:
        """Detect available audio player"""
        if shutil.which('ffplay'):
            return ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet']
        if shutil.which('mpv'):
            return ['mpv', '--really-quiet', '--no-video']
        if shutil.which('mpg123'):
            return ['mpg123', '-q']
        return None

    def _start_worker_thread(self):
        """Start background TTS worker thread"""
        self._tts_thread = threading.Thread(target=self._worker, daemon=True)
        self._tts_thread.start()

    def _worker(self):
        """Background worker that processes TTS queue"""
        while self.running:
            try:
                text, agent = self._tts_queue.get(timeout=0.1)
                if text is None:  # Shutdown signal
                    break
                if not text.strip():
                    continue

                # Create temporary file
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                    tmp_path = tmp_file.name

                # Synthesize speech
                self.engine.synthesize(text, tmp_path, agent)

                # Play audio
                subprocess.run(
                    self._audio_player_cmd + [tmp_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                # Clean up
                os.remove(tmp_path)

            except queue.Empty:
                continue
            except Exception as e:
                # Log errors but don't crash
                print(f"[TTS error: {e}]", file=sys.stderr)

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text before TTS synthesis"""
        # Convert to lowercase
        processed_text = text.lower()
        # Remove star symbols
        processed_text = processed_text.replace('*', '')
        return processed_text

    def say(self, text: str, agent: str):
        """Queue text for speech synthesis"""
        if not self.enabled:
            return
        try:
            # Preprocess text before queuing
            processed_text = self._preprocess_text(text)
            self._tts_queue.put_nowait((processed_text, agent))
        except queue.Full:
            # Queue is full, skip this message
            pass

    def shutdown(self):
        """Gracefully shutdown TTS manager"""
        self.running = False
        if self._tts_thread and self._tts_thread.is_alive():
            try:
                self._tts_queue.put_nowait((None, None))  # Shutdown signal
                self._tts_thread.join(timeout=1.0)
            except:
                pass

def create_tts_manager() -> TtsManager:
    """Factory function to create TTS manager with environment configuration"""
    lang = os.environ.get('RASPITRON_TTS_LANG', 'cs')
    engine = os.environ.get('RASPITRON_TTS_ENGINE', 'gtts')
    return TtsManager(lang=lang, engine_type=engine)
