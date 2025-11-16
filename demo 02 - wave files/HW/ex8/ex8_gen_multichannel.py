import wave
import struct
import math

# Parameters
sample_rate = 44100
duration = 1.0
num_channels = 4
sample_width = 2
num_samples = int(sample_rate * duration)

freqs = [220, 240, 440, 480]

with wave.open("sin_multichannel.wav", "w") as wf:
    wf.setnchannels(num_channels)
    wf.setsampwidth(sample_width)
    wf.setframerate(sample_rate)

    for n in range(num_samples):
        t = n / sample_rate
        frame = b""
        for ch in range(num_channels):
            value = int(32767.0 * math.sin(2.0 * math.pi * freqs[ch] * t))
            frame += struct.pack('<h', value)
        wf.writeframes(frame)

print("Done with", num_channels, "channels")