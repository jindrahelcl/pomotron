import os
import pygame
import time

# Global state
_is_playing = False

def play():
    """Start/resume geiger playback"""
    global _is_playing
    if pygame.mixer.get_init() and not _is_playing:
        pygame.mixer.music.unpause()
        _is_playing = True

def pause():
    """Pause geiger playback"""
    global _is_playing
    if pygame.mixer.get_init() and _is_playing:
        pygame.mixer.music.pause()
        _is_playing = False

def stop():
    """Stop geiger playback"""
    global _is_playing
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        _is_playing = False

def run(stop_event):
    """Main entry point for the geiger module"""
    global _is_playing

    # Get WAV file path from environment variable
    wav_file_path = "geiger.wav"

    if not os.path.exists(wav_file_path):
        raise FileNotFoundError(f"WAV file not found: {wav_file_path}")

    # Initialize pygame mixer
    pygame.mixer.init()

    # Load and play the audio file on loop
    pygame.mixer.music.load(wav_file_path)
    pygame.mixer.music.play(-1)  # -1 means loop forever
    _is_playing = True

    print(f"Playing geiger audio: {wav_file_path}")

    # Keep the thread alive until stop is requested
    stop_event.wait()

    # Cleanup
    pygame.mixer.music.stop()
    _is_playing = False

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
