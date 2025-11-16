# Stereo version, different frequencies in l/r
# 
# 16 bit/sample, stereo

from math import cos, pi 
import pyaudio
import struct


# Fs : Sampling frequency (samples/second)
Fs = 8000

T = 1       # T : Duration of audio to play (seconds)
N = T*Fs    # N : Number of samples to play

# L
a1_left = -1.9
a2_left = 0.998

# R
a1_right = -1.5
a2_right = 0.995

# L initialization
y1_left = 0.0
y2_left = 0.0

# R initialization
y1_right = 0.0
y2_right = 0.0

gain = 10000.0

p = pyaudio.PyAudio()
stream = p.open(format = pyaudio.paInt16,  
                channels = 2,  # stereo
                rate = Fs,
                input = False, 
                output = True)

# paInt16 is 16 bits/sample

print("Playing.")

# run difference equation for L and R
for n in range(0, N):

    # use impulse as input signal for L and R
    if n == 0:
        x0 = 1.0
    else:
        x0 = 0.0

    # L
    y0_left = x0 - a1_left * y1_left - a2_left * y2_left
    y2_left = y1_left
    y1_left = y0_left

    # R
    y0_right = x0 - a1_right * y1_right - a2_right * y2_right
    y2_right = y1_right
    y1_right = y0_right

    # convert to 16-bit int
    left_sample = int(gain * y0_left)
    right_sample = int(gain * y0_right)
    
    # cliping
    if left_sample > 32767:
        left_sample = 32767
    elif left_sample < -32768:
        left_sample = -32768
        
    if right_sample > 32767:
        right_sample = 32767
    elif right_sample < -32768:
        right_sample = -32768

    # pack as stereo
    output_string = struct.pack('hh', left_sample, right_sample)
    stream.write(output_string)

print("* Finished *")

stream.stop_stream()
stream.close()
p.terminate()