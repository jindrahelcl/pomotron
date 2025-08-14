#!/usr/bin/env python3
"""
Minimal test to reproduce the pygame + subprocess audio conflict
This simulates the exact sequence that causes segfaults in RaspiTRON
"""

import sys
import time
import subprocess
import tempfile
import os

def main():
    print("=== Pygame + Subprocess Audio Conflict Test ===")

    try:
        print("1. Initializing pygame...")
        import pygame
        pygame.mixer.init()

        print("2. Loading a pygame sound...")
        from sounds import sounds

        print("3. Playing pygame sound...")
        sounds.play_beep()
        time.sleep(1)

        print("4. Creating temporary audio file for subprocess...")
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name

        # Create a simple wav file using gTTS
        print("5. Generating audio with gTTS...")
        from gtts import gTTS
        tts = gTTS(text="test audio", lang='en')
        tts.save(tmp_path)

        print("6. Playing audio via subprocess (ffplay)...")
        subprocess.run(
            ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', tmp_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        print("7. Playing pygame sound again (SEGFAULT POINT)...")
        sounds.play_boop()
        time.sleep(1)

        print("8. Cleanup...")
        os.remove(tmp_path)

        print("SUCCESS: No segfault detected!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

        # Cleanup
        try:
            if 'tmp_path' in locals():
                os.remove(tmp_path)
        except:
            pass

if __name__ == "__main__":
    main()
