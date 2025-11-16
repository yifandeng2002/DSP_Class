# filter_16_clipped.py
# 
# Implement the second-order recursive difference equation
# y(n) = x(n) - a1 y(n-1) - a2 y(n-2)
# 
# 16 bit/sample
# clipped

from math import cos, pi 
import pyaudio
import struct


# Fs : Sampling frequency (samples/second)
Fs = 8000
# Also try other values of 'Fs'. What happens? Why?

T = 1       # T : Duration of audio to play (seconds)
N = T*Fs    # N : Number of samples to play

# Difference equation coefficients
a1 = -1.9
a2 = 0.998

# Initialization
y1 = 0.0
y2 = 0.0
gain = 50000.0  # test clipping
# Also try other values of 'gain'. What is the effect?

# Define 16-bit signed integer limits
max_val_16bit = 32767
min_val_16bit = -32768

# Create an audio object and open an audio stream for output
p = pyaudio.PyAudio()
stream = p.open(format = pyaudio.paInt16,  
                channels = 1, 
                rate = Fs,
                input = False, 
                output = True)

# paInt16 is 16 bits/sample

# Run difference equation
for n in range(0, N):

    # Use impulse as input signal
    if n == 0:
        x0 = 1.0
    else:
        x0 = 0.0

    # Difference equation
    y0 = x0 - a1 * y1 - a2 * y2

    # Delays
    y2 = y1
    y1 = y0

    # Output with gain
    output_value = gain * y0
    
    # clip the signal
    if output_value > max_val_16bit:
        clipped_value = max_val_16bit
    elif output_value < min_val_16bit:
        clipped_value = min_val_16bit
    else:
        clipped_value = int(output_value)
    
    # pack and write the clipped value
    output_string = struct.pack('h', clipped_value)
    stream.write(output_string)

print("* Finished *")

stream.stop_stream()
stream.close()
p.terminate()