import pygame
import sys
import glob
import os

class Sounds:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Reserve channels for each sound type
        pygame.mixer.set_num_channels(8)  # Ensure we have enough channels
        self.channels = {
            'keypress': pygame.mixer.Channel(0),
            'boop': pygame.mixer.Channel(1),
            'beep': pygame.mixer.Channel(2),
            'beep-startup': pygame.mixer.Channel(3),
            'geiger': pygame.mixer.Channel(4),
            'music': pygame.mixer.Channel(5)
        }

        self.sounds = {}
        self._geiger_paused = False
        self._music_file = None
        self._load_sounds()

    def _load_sounds(self):
        sound_files = ['keypress.wav', 'boop.wav', 'beep.wav', 'beep-startup.wav', 'geiger.wav']

        # Add first MP3 file from ~/Music if available
        music_files = glob.glob(os.path.expanduser('~/Music/*.mp3'))
        if music_files:
            self._music_file = music_files[0]
            sound_files.append(self._music_file)
        else:
            print("Warning: No MP3 files found in ~/Music", file=sys.stderr)
            self._music_file = None

        for filename in sound_files:
            try:
                self.sounds[filename] = pygame.mixer.Sound(filename)
            except (pygame.error, FileNotFoundError) as e:
                print(f"Warning: Could not load {filename}: {e}", file=sys.stderr)
                self.sounds[filename] = None

    def play_keypress(self):
        sound = self.sounds.get('keypress.wav')
        if sound:
            self.channels['keypress'].play(sound)

    def play_beep(self):
        sound = self.sounds.get('beep.wav')
        if sound:
            self.channels['beep'].play(sound)

    def play_boop(self):
        sound = self.sounds.get('boop.wav')
        if sound:
            self.channels['boop'].play(sound)

    def play_beep_startup(self):
        sound = self.sounds.get('beep-startup.wav')
        if sound:
            self.channels['beep-startup'].play(sound)

    def play_music(self):
        if self._music_file:
            sound = self.sounds.get(self._music_file)
            if sound:
                self.channels['music'].play(sound)

    def play_reload(self):
        """Reload and play the music file (useful if the music directory has changed)"""
        self._load_sounds()
        self.play_music()

    def start_geiger(self):
        """Start geiger counter sound (resumes if paused, starts fresh if stopped)"""
        if self._geiger_paused:
            # Resume from where we left off
            self.channels['geiger'].unpause()
            self._geiger_paused = False
        else:
            # Start fresh
            sound = self.sounds.get('geiger.wav')
            if sound:
                self.channels['geiger'].play(sound, loops=-1)  # Loop forever

    def pause_geiger(self):
        self.channels['geiger'].pause()
        self._geiger_paused = True

    def resume_geiger(self):
        self.channels['geiger'].unpause()
        self._geiger_paused = False

    def stop_geiger(self):
        self.channels['geiger'].pause()
        self._geiger_paused = True

    def is_geiger_playing(self):
        return self.channels['geiger'].get_busy()

# Global sounds instance
sounds = Sounds()
