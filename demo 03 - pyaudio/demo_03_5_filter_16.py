from math import cos, pi 
import pyaudio
import struct

# Fs : Sampling frequency (samples/second)
Fs = 8000

T = 3       # T : Duration of audio to play (seconds)
N = T*Fs    # N : Number of samples to play

# parameters for impulse response h(n) = r^n * cos(ω1n) * u(n)
r = 0.95        # pole radius, must be < 1 for stability
f1 = 440.0      # A4 note
omega1 = 2 * pi * f1 / Fs 


# Numerator coefficients
b0 = 1.0
b1 = -r * cos(omega1)
b2 = 0.0

# Denominator coefficients
a1 = -2 * r * cos(omega1)
a2 = r * r

print(f"Filter coefficients:")
print(f"b0 = {b0:.6f}, b1 = {b1:.6f}, b2 = {b2:.6f}")
print(f"a1 = {a1:.6f}, a2 = {a2:.6f}")
print(f"Designed for frequency: {f1} Hz")
print(f"Pole radius: {r}")

# initialization
x1 = 0.0  # x(n-1)
x2 = 0.0  # x(n-2)
y1 = 0.0  # y(n-1)
y2 = 0.0  # y(n-2)

# set gain to 32767 (2^15 - 1) for a full dynamic range
gain = 32767.0

p = pyaudio.PyAudio()
stream = p.open(format = pyaudio.paInt16,  
                channels = 1, 
                rate = Fs,
                input = False, 
                output = True)

print("playing impulse response.")

# run difference equation
for n in range(0, N):
    # use impulse as input signal
    if n == 0:
        x0 = 1.0
    else:
        x0 = 0.0
    y0 = b0 * x0 + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2

    # update delays
    x2 = x1  # x(n-2) = x(n-1)
    x1 = x0  # x(n-1) = x(n)
    y2 = y1  # y(n-2) = y(n-1)
    y1 = y0  # y(n-1) = y(n)

    # output with clipping
    output_value = gain * y0
    
    # clip to 16-bit signed int
    if output_value > 32767:
        output_value = 32767
    elif output_value < -32768:
        output_value = -32768
        
    output_string = struct.pack('h', int(output_value))
    stream.write(output_string)

print("* Finished *")

stream.stop_stream()
stream.close()
p.terminate()

# print theoretical values
print(f"\nTheoretical values:")
for n in range(10):
    h_n = (r**n) * cos(omega1 * n)
    print(f"h({n}) = {h_n:.6f}")