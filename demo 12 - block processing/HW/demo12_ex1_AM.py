import pyaudio
import struct
import math

# fourth order bandpass filter
a = [1.0, -1.8, 1.5, -0.6, 0.1]
b = [0.02, 0.0, -0.04, 0.0, 0.02]

BLOCKLEN = 1024
input_wavefile = 'author.wav'

import wave
wf = wave.open(input_wavefile, 'rb')
RATE = wf.getframerate()
WIDTH = wf.getsampwidth()
LEN = wf.getnframes()
CHANNELS = wf.getnchannels()

print('sampling rate: %d samples per second' % RATE)
print('each sample: %d bytes' % WIDTH)
print('signal length: %d samples' % LEN)
print('channel counts: %d channels' % CHANNELS)
print('block length: %d samples (%.2f ms)' % (BLOCKLEN, 1000.0 * BLOCKLEN / RATE))

# open audio stream
p = pyaudio.PyAudio()
stream = p.open(
    format=p.get_format_from_width(WIDTH),
    channels=CHANNELS,
    rate=RATE,
    input=False,
    output=True)

# create output block
output_block = BLOCKLEN * [0]

# number of blocks in file
num_blocks = int(math.floor(LEN / BLOCKLEN))

M = max(len(a), len(b)) - 1
w = [0.0] * (M + 1)  # delay states

print('Playing...')

for i in range(0, num_blocks):

    # get block of samples from wave file
    input_bytes = wf.readframes(BLOCKLEN)  #number of frames to read

    # binary to tuple of numbers
    input_tuple = struct.unpack('h' * BLOCKLEN, input_bytes)

    for n in range(0, BLOCKLEN):
        x = float(input_tuple[n])
        
        # canonical form filter
        acc = x
        for k in range(1, M + 1):
            acc -= a[k] * w[k]
        w0 = acc
        y = b[0] * w0
        for k in range(1, M + 1):
            y += b[k] * w[k]
        for k in range(M, 0, -1):
            w[k] = w[k - 1] if k - 1 >= 1 else w0
        
        # clip and store output sample
        y_clipped = max(-32768, min(32767, round(y)))
        output_block[n] = int(y_clipped)

    output_bytes = struct.pack('h' * BLOCKLEN, *output_block)
    stream.write(output_bytes)

print('Done.')

stream.stop_stream()
stream.close()
p.terminate()
wf.close()