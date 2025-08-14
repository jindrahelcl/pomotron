import pygame
import sys

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

        self.sounds = {}
        self._load_sounds()

    def _load_sounds(self):
        sound_files = ['keypress.wav', 'boop.wav', 'beep.wav']
        for filename in sound_files:
            try:
                self.sounds[filename] = pygame.mixer.Sound(filename)
            except (pygame.error, FileNotFoundError) as e:
                print(f"Warning: Could not load {filename}: {e}", file=sys.stderr)
                self.sounds[filename] = None

    def play_keypress(self):
        sound = self.sounds.get('keypress.wav')
        if sound:
            sound.play()

    def play_beep(self):
        sound = self.sounds.get('beep.wav')
        if sound:
            sound.play()

    def play_boop(self):
        sound = self.sounds.get('boop.wav')
        if sound:
            sound.play()

# Global sounds instance
sounds = Sounds()
