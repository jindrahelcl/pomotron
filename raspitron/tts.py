#!/usr/bin/env python3

import os
import sys
import threading
import queue
import tempfile
import subprocess
import wave

from gtts import gTTS
from google import genai
from google.genai import types

class TtsEngine:
    """Base TTS engine interface"""
    def __init__(self, lang: str = 'en'):
        self.lang = lang

    def synthesize(self, text: str, filename: str, agent: str):
        """Synthesize text to audio file"""
        raise NotImplementedError

class GttsEngine(TtsEngine):
    def synthesize(self, text: str, filename: str, agent: str):
        tts = gTTS(text=text, lang=self.lang)
        tts.save(filename)

class GeminiTtsEngine(TtsEngine):
    def __init__(self, lang: str = 'cs', api_key: str = None):
        super().__init__(lang)
        api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY environment variable not set")

        self.client = genai.Client(api_key=api_key)

        self.voice_mapping = {
            "shot_out_eye": "Fenrir",
            "confessor": "Charon",
            "tradicni": "Orus",
            "pomo": "Puck",
        }

    def get_voice_for_agent(self, agent: str) -> str:
        return self.voice_mapping.get(agent, "Kore")

    def synthesize(self, text: str, filename: str, agent: str):
        try:
            voice_name = self.get_voice_for_agent(agent)

            response = self.client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name,
                            )
                        )
                    ),
                )
            )

            audio_data = response.candidates[0].content.parts[0].inline_data.data
            self._save_wave_file(filename, audio_data)

        except Exception as e:
            print(f"Gemini TTS error: {e}, falling back to gTTS", file=sys.stderr)
            tts = gTTS(text=text, lang='cs')
            tts.save(filename)

    def _save_wave_file(self, filename: str, pcm_data: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2):
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm_data)

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
            "mbrola": '(progn (set! mbrola_progname "/usr/bin/mbrola")(set! czech-mbrola_database "/usr/share/mbrola/cz2/cz2")(require \'czech-mbrola)(voice_czech_mbrola_cz2))',
        }.get(voice, "(voice_czech_krb)")

    def agent_to_voice(self, agent: str):
        return {
            "shot_out_eye": "mbrola",
            "confessor": "krb",
            "tradicni": "ph",
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
    def __init__(self, lang: str = 'cs', engine_type: str = 'gtts'):
        self.running = True
        self.enabled = os.environ.get('RASPITRON_TTS', '1') != '0'
        self.lang = lang

        if engine_type == 'festival':
            self.engine = FestivalEngine()
        elif engine_type == 'gemini':
            self.engine = GeminiTtsEngine(lang)
        else:
            self.engine = GttsEngine(lang)

        self._audio_player_cmd = ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet']
        self._tts_queue = queue.Queue()
        self._tts_thread = None

        if self.enabled:
            self._start_worker_thread()

    def join(self):
        self._tts_queue.join()

    def _start_worker_thread(self):
        self._tts_thread = threading.Thread(target=self._worker, daemon=True)
        self._tts_thread.start()

    def _worker(self):
        while self.running:
            try:
                text, agent, cb = self._tts_queue.get(timeout=0.1)
                if text is None:
                    break
                if not text.strip():
                    continue

                if isinstance(self.engine, GeminiTtsEngine):
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                        tmp_path = tmp_file.name
                else:
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                        tmp_path = tmp_file.name

                self.engine.synthesize(text, tmp_path, agent)

                if cb:
                    cb()

                subprocess.run(
                    self._audio_player_cmd + [tmp_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                os.remove(tmp_path)

                self._tts_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"[TTS error: {e}]", file=sys.stderr)

    def _preprocess_text(self, text: str) -> str:
        processed_text = text.lower()
        processed_text = processed_text.replace('*', '')
        return processed_text

    def say(self, text: str, agent: str, cb=None):
        if not self.enabled:
            return
        try:
            processed_text = self._preprocess_text(text)
            self._tts_queue.put_nowait((processed_text, agent, cb))
        except queue.Full:
            pass

    def shutdown(self):
        self.running = False
        if self._tts_thread and self._tts_thread.is_alive():
            try:
                self._tts_queue.put_nowait((None, None, None))
                self._tts_thread.join(timeout=1.0)
            except:
                pass

def create_tts_manager() -> TtsManager:
    lang = os.environ.get('RASPITRON_TTS_LANG', 'cs')
    engine = os.environ.get('RASPITRON_TTS_ENGINE', 'gtts')
    return TtsManager(lang=lang, engine_type=engine)
