import pyaudio
import wave
import numpy as np
import struct
import math

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000   # sr
DURATION = 5 # duration
FREQ = 400.0  # modulation frequency 400
OUTPUT_FILE = "ex4_output.wav"

p = pyaudio.PyAudio()

# i/o stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

print("Recording for 5 seconds...")

frames = []
n = 0

for i in range(0, int(RATE / CHUNK * DURATION)):
    data = stream.read(CHUNK)
    x = np.frombuffer(data, dtype=np.int16)  #input signal
    
    t = (np.arange(len(x)) + n) / RATE
    n += len(x)
    
    # amplitude modulation
    carrier = np.cos(2 * np.pi * FREQ * t)
    y = x * carrier
    # clip and convert to 16-bit PCM
    y = np.int16(y)
    frames.append(y.tobytes())
    
    # playback
    stream.write(y.tobytes())

print("Done.")

# close
stream.stop_stream()
stream.close()
p.terminate()

# save file
wf = wave.open(OUTPUT_FILE, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

print(f"Output to {OUTPUT_FILE}")