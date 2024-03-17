import pyaudio
import wave
import audioop
from pynput.keyboard import Key, Controller
import time

def timems():
    return round(time.time() * 1000)

keyboard = Controller()

CHUNK = 16 # basically latency
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
WAVE_OUTPUT_FILENAME = "output.wav"

LIMIT = 19000 

p = pyaudio.PyAudio()

BPM = 142 # Fan Club & Fan Club 2
error = 200 # time in ms ± this (for "wonderful" and "i suppose")
delay1 = 1.5 # in beats
delay2 = 0.5
delay3 = 1 # how long to hold for

beat_len = 60000 / BPM

last = False
claps = []
max_claps = 5

ignore_until = -(delay3 * beat_len) - 1

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

try:
    while True:
        data = stream.read(CHUNK)
        rms = audioop.rms(data, 2)
        t = timems()
        if ignore_until > t or (len(claps) and t - claps[-1] < 50):
            continue
        print(rms)
        if rms >= LIMIT and not last:
            keyboard.press(" ")
            last = True
            claps += [t]
            if len(claps) > max_claps:
                claps = claps[-max_claps:]
            if len(claps) < 3:
                continue
            if abs(claps[-2] - claps[-3] - delay1 * beat_len) < error and abs(claps[-1] - claps[-2] - delay2 * beat_len) < error:
                ignore_until = t + delay3 * beat_len
        elif rms < LIMIT and last:
            keyboard.release(" ")
            last = False
except KeyboardInterrupt:
    pass

stream.stop_stream()
stream.close()
p.terminate()