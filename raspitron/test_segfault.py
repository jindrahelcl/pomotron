#!/usr/bin/env python3
"""
Segfault isolation test for RaspiTRON
Run this to identify where the segfault occurs during audio playback
"""

import sys
import time
import threading

def test_step(step_num, description, test_func):
    """Run a test step and report results"""
    print(f"{step_num}. {description}...", end=" ", flush=True)
    try:
        test_func()
        print("OK")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pygame_init():
    import pygame
    pygame.mixer.init()

def test_sounds_import():
    from sounds import sounds

def test_tts_import():
    from tts import create_tts_manager

def test_first_sound():
    from sounds import sounds
    sounds.play_beep()
    time.sleep(0.5)

def test_tts_creation():
    global tts_manager
    from tts import create_tts_manager
    tts_manager = create_tts_manager()

def test_simple_tts():
    tts_manager.say("test message", "system", engine_type='gtts')
    tts_manager.join()

def test_second_sound():
    from sounds import sounds
    sounds.play_boop()
    time.sleep(0.5)

def test_tts_with_callback():
    """Test TTS with callback - this simulates the main app flow"""
    callback_called = threading.Event()

    def test_callback():
        callback_called.set()
        print("\n   Callback executed")

    print("\n   Starting TTS with callback...")
    tts_manager.say("testing callback", "system", cb=test_callback, engine_type='gtts')
    tts_manager.join()

    # Wait for callback
    if callback_called.wait(timeout=5):
        print("   Callback completed")
    else:
        raise Exception("Callback timeout")

def test_third_sound():
    """This is where the segfault typically happens"""
    from sounds import sounds
    sounds.play_beep()
    time.sleep(0.5)

def main():
    print("=== RaspiTRON Segfault Isolation Test ===")
    print("This test isolates the audio playback segfault issue")
    print()

    global tts_manager
    tts_manager = None

    tests = [
        ("Testing pygame initialization", test_pygame_init),
        ("Testing sounds module import", test_sounds_import),
        ("Testing TTS module import", test_tts_import),
        ("Testing first sound playback", test_first_sound),
        ("Testing TTS manager creation", test_tts_creation),
        ("Testing simple TTS playback", test_simple_tts),
        ("Testing second sound (potential conflict)", test_second_sound),
        ("Testing TTS with callback (main app flow)", test_tts_with_callback),
        ("Testing third sound (typical segfault point)", test_third_sound),
    ]

    for i, (description, test_func) in enumerate(tests, 1):
        if not test_step(i, description, test_func):
            print(f"\nTest failed at step {i}: {description}")
            print("This is likely where the segfault occurs in the main app.")
            sys.exit(1)

        # Small delay between tests
        time.sleep(0.2)

    print("\n=== All tests passed! ===")
    print("If you get a segfault, it's likely in the audio subsystem interaction")
    print("between pygame sounds and subprocess audio playback.")

    # Cleanup
    if tts_manager:
        tts_manager.shutdown()

if __name__ == "__main__":
    main()
