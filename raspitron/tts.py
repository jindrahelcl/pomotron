#!/usr/bin/env python3

import os
import sys
import threading
import queue
import tempfile
import subprocess
import wave
import asyncio
import string

from gtts import gTTS
from google import genai
from google.genai import types
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer

class TtsEngine:
    """Base TTS engine interface"""
    def __init__(self, lang: str = 'en'):
        self.lang = lang

    def synthesize(self, text: str, filename: str, agent: str, voice: str = None):
        """Synthesize text to audio file"""
        raise NotImplementedError

class GttsEngine(TtsEngine):
    def synthesize(self, text: str, filename: str, agent: str, voice: str = None):
        # gTTS doesn't support custom voices, ignore voice parameter
        tts = gTTS(text=text, lang=self.lang)
        tts.save(filename)

class GeminiTtsEngine(TtsEngine):
    def __init__(self, lang: str = 'cs', api_key: str = None):
        super().__init__(lang)
        api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY environment variable not set")

        self.client = genai.Client(api_key=api_key)

    def synthesize(self, text: str, filename: str, agent: str, voice: str = None):
        try:
            # Use provided voice or default to "Kore"
            voice_name = voice if voice else "Kore"

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

    def synthesize(self, text: str, filename: str, agent: str, voice: str = None):
        encoded_text = text.encode('iso8859-2', errors='ignore')
        with open(filename, 'wb') as outfile:
            # Use provided voice or default to "machac"
            voice_name = voice if voice else "machac"
            voice_cmd = self.get_voice_cmd(voice_name)
            text2wave_proc = subprocess.Popen(
                ['text2wave', '-eval', voice_cmd],
                stdin=subprocess.PIPE,
                stdout=outfile
            )
            text2wave_proc.stdin.write(encoded_text)
            text2wave_proc.stdin.close()
            text2wave_proc.wait()

class OpenAiTtsEngine(TtsEngine):
    """OpenAI TTS engine with real-time streaming"""
    def __init__(self, lang: str = 'cs', api_key: str = None):
        super().__init__(lang)

        api_key = api_key or os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable not set")

        self.client = AsyncOpenAI(api_key=api_key)

    def synthesize(self, text: str, filename: str, agent: str, voice: str = None):
        """Synthesize text to audio file using OpenAI TTS"""
        # Run async synthesis in sync context
        asyncio.run(self._async_synthesize(text, filename, agent, voice))

    async def _async_synthesize(self, text: str, filename: str, agent: str, voice: str = None):
        """Async synthesis method"""
        # Use provided voice or default to "alloy"
        voice_name = voice if voice else "alloy"

        response = await self.client.audio.speech.create(
            model="tts-1",
            voice=voice_name,
            input=text,
            response_format="wav"
        )

        # Save the audio content to file
        with open(filename, 'wb') as f:
            f.write(response.content)

    async def synthesize_and_play_streaming(self, text: str, agent: str, voice: str = None):
        """Synthesize and play audio in real-time streaming mode"""
        # Use provided voice or default to "alloy"
        voice_name = voice if voice else "alloy"

        async with self.client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice=voice_name,
            input=text,
            response_format="pcm",  # PCM works best with LocalAudioPlayer
            stream_format="audio"
        ) as response:
            player = LocalAudioPlayer()
            await player.play(response)

class TtsManager:
    def __init__(self, lang: str = 'cs'):
        self.running = True
        self.enabled = os.environ.get('RASPITRON_TTS', '1') != '0'
        self.lang = lang
        self.engines = {}

        # Pre-initialize all possible engines if TTS is enabled
        if self.enabled:
            self._initialize_engines()
        else:
            print("TTS Engine disabled", file=sys.stderr)

        #self._audio_player_cmd = [r"c:\\Program Files\\VideoLAN\\VLC\\vlc.exe", "--play-and-exit", "--intf", "dummy"]
        self._audio_player_cmd = ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet']
        self._tts_queue = queue.Queue()
        self._tts_thread = None

        if self.enabled:
            self._start_worker_thread()

    def _initialize_engines(self):
        """Initialize all possible TTS engines"""
        try:
            self.engines['gtts'] = GttsEngine(self.lang)
        except Exception as e:
            print(f"Failed to initialize gTTS engine: {e}", file=sys.stderr)

        try:
            self.engines['festival'] = FestivalEngine()
        except Exception as e:
            print(f"Failed to initialize Festival engine: {e}", file=sys.stderr)

        try:
            self.engines['gemini'] = GeminiTtsEngine(self.lang)
        except Exception as e:
            print(f"Failed to initialize Gemini engine: {e}", file=sys.stderr)

        try:
            self.engines['openai'] = OpenAiTtsEngine(self.lang)
        except Exception as e:
            print(f"Failed to initialize OpenAI engine: {e}", file=sys.stderr)

        #self._audio_player_cmd = [r"c:\\Program Files\\VideoLAN\\VLC\\vlc.exe", "--play-and-exit", "--intf", "dummy"]
        self._audio_player_cmd = ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet']
        self._tts_queue = queue.Queue()
        self._tts_thread = None

        if self.enabled:
            self._start_worker_thread()

    def join(self):
        if self._tts_thread and self._tts_thread.is_alive():
            self._tts_queue.join()

    def _start_worker_thread(self):
        self._tts_thread = threading.Thread(target=self._worker, daemon=True)
        self._tts_thread.start()

    def _worker(self):
        while self.running:
            try:
                queue_item = self._tts_queue.get(timeout=0.1)

                # Handle format: (text, agent, cb, use_streaming, engine_type, voice)
                if len(queue_item) == 6:
                    text, agent, cb, use_streaming, engine_type, voice = queue_item
                elif len(queue_item) == 5:
                    # Backward compatibility
                    text, agent, cb, use_streaming, engine_type = queue_item
                    voice = None
                else:
                    # Fallback for old format
                    text, agent, cb = queue_item[:3]
                    use_streaming = False
                    engine_type = 'gtts'
                    voice = None

                if text is None:
                    break
                if not text.strip():
                    continue

                # Get the specified engine
                engine = self.engines.get(engine_type)
                if not engine:
                    print(f"Unknown TTS engine: {engine_type}, using gtts", file=sys.stderr)
                    engine = self.engines.get('gtts')

                # Use streaming mode for OpenAI if requested
                if use_streaming and isinstance(engine, OpenAiTtsEngine):
                    # Run streaming synthesis
                    asyncio.run(engine.synthesize_and_play_streaming(text, agent, voice))

                    if cb:
                        cb()
                else:
                    # Regular synthesis for all other cases
                    self._regular_synthesis(text, agent, cb, engine, voice)

                self._tts_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"[TTS error: {e}]", file=sys.stderr)

    def _regular_synthesis(self, text: str, agent: str, cb, engine, voice=None):
        """Regular file-based synthesis and playback"""
        if isinstance(engine, GeminiTtsEngine):
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = tmp_file.name
        else:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = tmp_file.name

        engine.synthesize(text, tmp_path, agent, voice)

        if cb:
            cb()

        subprocess.run(
            self._audio_player_cmd + [tmp_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        os.remove(tmp_path)

    def _preprocess_text(self, text: str) -> str:
        processed_text = text.lower()
        processed_text = processed_text.replace('*', '')
        return processed_text

    def say(self, text: str, agent: str, cb=None, use_streaming=False, engine_type='gtts', voice=None):
        if not self.enabled:
            # If TTS is disabled, just call the callback immediately
            if cb:
                cb()
            return

        try:
            processed_text = self._preprocess_text(text)
            # gtts throws at inputs like "."
            if not any(char in string.ascii_letters+string.digits for char in processed_text):
                return

            # Put request in queue with engine type and voice
            self._tts_queue.put_nowait((processed_text, agent, cb, use_streaming, engine_type, voice))
        except queue.Full:
            pass

    def shutdown(self):
        self.running = False
        if self._tts_thread and self._tts_thread.is_alive():
            try:
                self._tts_queue.put_nowait((None, None, None, False, None, None))
                self._tts_thread.join(timeout=1.0)
            except:
                pass

def create_tts_manager() -> TtsManager:
    lang = os.environ.get('RASPITRON_TTS_LANG', 'cs')
    return TtsManager(lang=lang)
