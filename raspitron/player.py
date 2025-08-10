#!/usr/bin/env python3

import alsaaudio
from math import sin, pi, sqrt

class Player:
    def __init__(self, periodsize=4096, rate=44100):
        self.periodsize = periodsize
        self.rate = rate
        self.buf = bytearray(4*periodsize)
        self.t = 0
        self.dt = 1/rate

    def f(self, t):
        return sin(2*pi*440*t)

    def fl(self, t):
        return self.f(t)

    def fr(self, t):
        return self.f(t)

    def export(self, start, stop, filename):
        i = 0
        t = start
        dt = self.dt
        fl = self.fl
        fr = self.fr
        with open(filename, "wb") as f:
            while (t <= stop):
                val = min(32767, int(32768*fl(t)))
                f.write(bytes([val & 255, val >> 8 & 255]))
                val = min(32767, int(32768*fr(t)))
                f.write(bytes([val & 255, val >> 8 & 255]))
                t = start + i*dt
                i += 1

    def open(self):
        self.dev = alsaaudio.PCM()
        self.dev.setchannels(2)
        self.dev.setrate(self.rate)
        self.dev.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.dev.setperiodsize(self.periodsize)

    def playperiod(self):
        dt = self.dt
        buf = self.buf
        fl = self.fl
        fr = self.fr
        t = self.t
        for i in range(0, 4*self.periodsize, 4):
            val = min(32767, int(32768*fl(t)))
            buf[i] = val & 255
            buf[i+1] = val >> 8 & 255
            val = min(32767, int(32768*fr(t)))
            buf[i+2] = val & 255
            buf[i+3] = val >> 8 & 255
            t += dt  # fixme: this is numerically suboptimal
        self.dev.write(buf)
        self.t = t

    def playpreperiod(self):
        dt = self.dt
        buf = self.buf
        fl = self.fl
        fr = self.fr
        t = self.t
        prev_l = 0
        prev_r = 0
        started_l = False
        started_r = False
        for i in range(0, 4*self.periodsize, 4):
            val = min(32767, int(32768*fl(t)))
            if not started_l:
                if val == 0 or prev_l != 0 and prev_l^val < 0:
                    started_l = True
                prev_l = val
            if started_l:
                buf[i] = val & 255
                buf[i+1] = val >> 8 & 255
            else:
                buf[i] = 0
                buf[i+1] = 0
            val = min(32767, int(32768*fr(t)))
            if not started_r:
                if val == 0 or prev_r != 0 and prev_r^val < 0:
                    started_r = True
                prev_r = val
            if started_r:
                buf[i+2] = val & 255
                buf[i+3] = val >> 8 & 255
            else:
                buf[i] = 0
                buf[i+1] = 0
            t += dt  # fixme: this is numerically suboptimal
        self.dev.write(buf)
        self.t = t

    def playpostperiod(self):
        dt = self.dt
        buf = self.buf
        fl = self.fl
        fr = self.fr
        t = self.t
        prev_l = 0
        prev_r = 0
        stopped_l = False
        stopped_r = False
        for i in range(0, 4*self.periodsize, 4):
            if not stopped_l:
                val = min(32767, int(32768*fl(t)))
                if val == 0 or prev_l != 0 and prev_l^val < 0:
                    stopped_l = True
            if stopped_l:
                buf[i] = 0
                buf[i+1] = 0
            else:
                buf[i] = val & 255
                buf[i+1] = val >> 8 & 255
                prev_l = val
            if not stopped_r:
                val = min(32767, int(32768*fr(t)))
                if val == 0 or prev_r != 0 and prev_r*val < 0:
                    stopped_r = True
            if stopped_r:
                buf[i+2] = 0
                buf[i+3] = 0
            else:
                buf[i+2] = val & 255
                buf[i+3] = val >> 8 & 255
                prev_r = val
            t += dt  # fixme: this is numerically suboptimal
        self.dev.write(buf)
        self.t = t

    def drain(self):
        self.buf[:] = 4*self.periodsize*b"\x00"
        for _ in range(4):
            self.dev.write(self.buf)

    def play(self, start, stop):
        self.t = start
        self.playpreperiod()
        while self.t < stop:
            self.playperiod()
        self.playpostperiod()

    def close(self):
        self.dev.close()

class BeePlayer(Player):
    def __init__(self, c=343, v=22, d=5, omega=2*pi*440, **kwargs):
        super().__init__(**kwargs)
        self.c = c
        self.v = v
        self.d = d
        self.omega = omega
        self.delta = d/c
        self.w = v**2/c**2
        self.alpha = d**2*(c**2-v**2)/c**4

    def f0(self, t):
        return sin(self.omega*t)

    def f(self, t):
        w = self.w
        b = sqrt(t**2*w + self.alpha)
        delta = self.delta
        return delta*((b+t*w) / (t**2*w+delta**2)) * self.f0((t-b)/(1-w))
