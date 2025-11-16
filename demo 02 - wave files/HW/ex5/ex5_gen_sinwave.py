import wave, math

sample_rate = 44100 # sample rate
freq = 220.0 #frequency
duration = 1.0    #seconds
amplitude = 0.9   #avoid clipping

num_frames = int(sample_rate * duration)

with wave.open('sin_8bit_220Hz.wav', 'wb') as wf:
    wf.setnchannels(1) #mono
    wf.setsampwidth(1) #8 bit
    wf.setframerate(sample_rate)
    frames = bytearray()
    for n in range(num_frames):
        t = n / sample_rate
        x = amplitude * math.sin(2 * math.pi * freq * t)
        u8 = int(round((x * 127.0) + 128.0))# 0-255
        u8 = max(0, min(255, u8))  # clamp
        frames.append(u8)
    wf.writeframes(frames)