import os
import time
from sounds import sounds

def run(stop_event):
    """Main entry point for the geiger module"""
    sounds.start_geiger()
    stop_event.wait()
    sounds.stop_geiger()
