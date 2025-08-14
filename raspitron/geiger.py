from sounds import sounds

def run(stop_event):
    sounds.start_geiger()
    stop_event.wait()
    sounds.stop_geiger()
