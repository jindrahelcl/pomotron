import numpy as np
import random
import math
import alsaaudio
import time

from scipy.signal import butter, lfilter

# ---------- Parameters ----------
base_cps = 2.5              # average counts/sec
variation_depth = 0.5       # +/-50% variation
change_interval = 5.0       # seconds between new target rates
sample_rate = 44100
buffer_size = 1024          # ALSA frames per write
click_max_amp = 1.0
click_duration_ms = 6.0
deadtime_ms = 0.3
background_hiss_level = 0.003
# -------------------------------

class SlowRateModulator:
    def __init__(self, base_cps, variation_depth=0.5, change_interval=1.0, smoothing_factor=0.1):
        self.base_cps = base_cps
        self.variation_depth = variation_depth
        self.change_interval = change_interval
        self.smoothing_factor = smoothing_factor
        self.current_mult = 1.0
        self.target_mult = 1.0
        self.time_to_next_change = 0

    def sample_rate_multiplier_log_cauchy(self):
        loc = 0.0  # median on log scale corresponds to multiplier=1
        scale = 0.6  # tweak for tail heaviness
        epsilon = 1e-6
        u = random.uniform(-0.5 + epsilon, 0.5 - epsilon)
        y = loc + scale * math.tan(math.pi * u)
        val = math.exp(y)
        return max(0.1, min(20.0, val))

    def advance(self, dt):
        self.time_to_next_change -= dt
        if self.time_to_next_change <= 0:
            self.target_mult = self.sample_rate_multiplier_log_cauchy()
            self.time_to_next_change = self.change_interval

        blend = self.smoothing_factor * dt
        self.current_mult += (self.target_mult - self.current_mult) * blend
        return self.base_cps * self.current_mult

def make_click(click_len_samples, sample_rate):
    noise = np.random.normal(0.0, 1.0, click_len_samples)
    t = np.arange(click_len_samples) / sample_rate
    tau = (click_len_samples / sample_rate) * 0.6
    env = (1.0 - np.exp(-20 * t)) * np.exp(-t / max(1e-6, tau))
    click = noise * env

    lowcut = 800.0
    highcut = 6000.0
    nyq = 0.5 * sample_rate
    b, a = butter(2, [lowcut / nyq, highcut / nyq], btype='band')
    click = lfilter(b, a, click)

    click /= (np.max(np.abs(click)) + 1e-12)
    return click

def generate_poisson_event_times(modulator, deadtime_s=0.0003):
    t = 0.0
    last_event_time = -1e9
    while True:
        inst_rate = modulator.advance(0)
        wait = random.expovariate(inst_rate)
        t += wait
        modulator.advance(wait)
        if t - last_event_time >= deadtime_s:
            last_event_time = t
            yield t

def sample_click_amplitude(mean=0.8, std=0.3, min_val=0.5, max_val=1.0):
    amp = random.gauss(mean, std)
    return max(min_val, min(max_val, amp))

def run(stop_event):
    # Setup audio
    pcm = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK)
    pcm.setchannels(1)
    pcm.setrate(sample_rate)
    pcm.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    pcm.setperiodsize(buffer_size)

    click_len_samples = max(1, int((click_duration_ms / 1000.0) * sample_rate))
    deadtime_s = deadtime_ms / 1000.0
    click_template = make_click(click_len_samples, sample_rate)

    modulator = SlowRateModulator(base_cps, variation_depth, change_interval)
    event_gen = generate_poisson_event_times(modulator, deadtime_s)

    current_time = 0.0
    pending_clicks = []

    while not stop_event.is_set():
        # Fill buffer with background hiss
        buf = np.random.normal(0.0, background_hiss_level, buffer_size)

        # Add clicks whose times fall into this buffer
        buffer_start = current_time
        buffer_end = current_time + buffer_size / sample_rate

        # Schedule new clicks until the next click is beyond buffer_end
        while True:
            next_click_time = next(event_gen)
            if next_click_time < buffer_start:
                continue
            if next_click_time >= buffer_end:
                # Put it back for the next iteration
                pending_clicks.append(next_click_time)
                break
            else:
                pending_clicks.append(next_click_time)

        # Mix clicks into buffer
        for click_time in list(pending_clicks):
            offset_samples = int((click_time - buffer_start) * sample_rate)
            if 0 <= offset_samples < buffer_size:
                amp = click_max_amp * sample_click_amplitude()
                # Generate fresh click waveform per event
                click = make_click(click_len_samples, sample_rate) * amp
                end_idx = min(buffer_size, offset_samples + click.size)
                buf[offset_samples:end_idx] += click[:end_idx - offset_samples]

            if click_time < buffer_end:
                pending_clicks.remove(click_time)

        # Clip and convert to 16-bit PCM
        buf = np.clip(buf, -1.0, 1.0)
        pcm.write((buf * 32767).astype(np.int16).tobytes())

        current_time += buffer_size / sample_rate

