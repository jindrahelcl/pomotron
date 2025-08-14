import os
import pygame
import time
import threading

class GeigerPlayer:
    def __init__(self):
        self.sounds = {}
        self.channels = {}
        self.current_mode = None
        self.is_playing = False
        self.switch_event = threading.Event()
        self.switch_to_mode = None
        self.stop_event = None

        # File mappings - only known to this class
        self.mode_files = {
            'request': 'geiger-low.wav',
            'tts': 'geiger.wav'
        }

    def load_sound(self, wav_file_path):
        """Load a sound file if not already loaded"""
        if wav_file_path not in self.sounds:
            if not os.path.exists(wav_file_path):
                raise FileNotFoundError(f"WAV file not found: {wav_file_path}")
            self.sounds[wav_file_path] = pygame.mixer.Sound(wav_file_path)
        return self.sounds[wav_file_path]

    def switch_to_mode(self, mode):
        """Switch to a different mode (request/tts)"""
        if mode in self.mode_files:
            self.switch_to_mode = mode
            self.switch_event.set()
        else:
            print(f"Warning: Unknown mode '{mode}'. Available modes: {list(self.mode_files.keys())}")

    def play(self):
        """Start/resume geiger playback"""
        if pygame.mixer.get_init() and not self.is_playing and self.current_mode:
            current_file = self.mode_files[self.current_mode]
            if current_file in self.channels and self.channels[current_file]:
                self.channels[current_file].unpause()
            self.is_playing = True

    def pause(self):
        """Pause geiger playback"""
        if pygame.mixer.get_init() and self.is_playing and self.current_mode:
            current_file = self.mode_files[self.current_mode]
            if current_file in self.channels and self.channels[current_file]:
                self.channels[current_file].pause()
            self.is_playing = False

    def stop(self):
        """Stop geiger playback"""
        if pygame.mixer.get_init() and self.current_mode:
            current_file = self.mode_files[self.current_mode]
            if current_file in self.channels and self.channels[current_file]:
                self.channels[current_file].stop()
            self.is_playing = False

    def run(self, stop_event, initial_mode="request"):
        """Main entry point for the geiger module"""
        self.stop_event = stop_event

        # Initialize pygame mixer
        pygame.mixer.init()

        # Load all sound files
        try:
            for mode, filename in self.mode_files.items():
                self.load_sound(filename)
        except FileNotFoundError as e:
            print(f"Error loading sound files: {e}")
            return

        # Start playing initial mode
        if initial_mode not in self.mode_files:
            print(f"Warning: Unknown initial mode '{initial_mode}', using 'request'")
            initial_mode = "request"

        self.current_mode = initial_mode
        current_file = self.mode_files[self.current_mode]
        sound = self.sounds[current_file]
        self.channels[current_file] = sound.play(-1)  # -1 means loop forever
        self.is_playing = True

        print(f"Playing geiger audio in mode '{self.current_mode}': {current_file}")

        # Keep the thread alive until stop is requested
        while not stop_event.is_set():
            # Check for mode switch requests
            if self.switch_event.wait(timeout=0.1):
                self.switch_event.clear()
                if self.switch_to_mode and self.switch_to_mode != self.current_mode:
                    self._switch_mode()

        # Cleanup
        self._cleanup()

    def _switch_mode(self):
        """Internal method to handle mode switching"""
        # Pause current file
        current_file = self.mode_files[self.current_mode]
        if current_file in self.channels and self.channels[current_file]:
            self.channels[current_file].pause()

        # Switch to new mode
        old_mode = self.current_mode
        self.current_mode = self.switch_to_mode
        new_file = self.mode_files[self.current_mode]

        # Start new file if not already playing, or resume if paused
        if new_file not in self.channels or not self.channels[new_file]:
            sound = self.sounds[new_file]
            self.channels[new_file] = sound.play(-1)
        else:
            self.channels[new_file].unpause()

        print(f"Switched from mode '{old_mode}' to '{self.current_mode}'")
        self.switch_to_mode = None

    def _cleanup(self):
        """Clean up resources"""
        for channel in self.channels.values():
            if channel:
                channel.stop()
        pygame.mixer.quit()
        self.is_playing = False

# Global instance for backward compatibility
_geiger_player = GeigerPlayer()

# Backward compatibility functions
def switch_to_mode(mode):
    _geiger_player.switch_to_mode(mode)

def play():
    _geiger_player.play()

def pause():
    _geiger_player.pause()

def stop():
    _geiger_player.stop()

def run(stop_event, initial_mode="request"):
    _geiger_player.run(stop_event, initial_mode)

if __name__ == "__main__":
    import threading

    print("Testing geiger playback...")
    stop_event = threading.Event()

    try:
        # Start playback in a separate thread
        geiger_thread = threading.Thread(target=run, args=(stop_event,))
        geiger_thread.start()

        print("Playing geiger sound. Press Ctrl+C to stop.")

        # Wait for user interrupt
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping geiger...")
        stop_event.set()
        geiger_thread.join()
        print("Stopped.")
