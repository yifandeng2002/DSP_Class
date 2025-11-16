import pyaudio
import struct
import wave
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation

a = [1.0, -1.8, 1.5, -0.6, 0.1]
b = [0.02, 0.0, -0.04, 0.0, 0.02]

GAIN = 0.5

BLOCKLEN = 512
DISPLAY_SAMPLES = 2048  # number of samples to display on plot

input_wavefile = 'author.wav'

wf = wave.open(input_wavefile, 'rb')
RATE = wf.getframerate()
WIDTH = wf.getsampwidth()
LEN = wf.getnframes()
CHANNELS = wf.getnchannels()

print('sampling rate: %d samples per second' % RATE)
print('sample width: %d bytes' % WIDTH)
print('signal length: %d samples' % LEN)
print('signal channel counts: %d channels' % CHANNELS)

p = pyaudio.PyAudio()
stream = p.open(
    format=p.get_format_from_width(WIDTH),
    channels=CHANNELS,
    rate=RATE,
    input=False,
    output=True)

# canonical form filter
M = max(len(a), len(b)) - 1
w = [0.0] * (M + 1)  # delay states

# buffers for plotting
input_buffer = [0] * DISPLAY_SAMPLES
output_buffer = [0] * DISPLAY_SAMPLES

# output blocks
output_block = BLOCKLEN * [0]
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
x_axis = list(range(DISPLAY_SAMPLES))
line1, = ax1.plot(x_axis, input_buffer, 'b-', linewidth=0.5)
line2, = ax2.plot(x_axis, output_buffer, 'r-', linewidth=0.5)

#subplots
ax1.set_ylim(-32768, 32768)
ax1.set_xlim(0, DISPLAY_SAMPLES)
ax1.set_ylabel('Amplitude')
ax1.set_title('Input signal')
ax1.grid(True)

ax2.set_ylim(-32768, 32768)
ax2.set_xlim(0, DISPLAY_SAMPLES)
ax2.set_xlabel('Sample index')
ax2.set_ylabel('Amplitude')
ax2.set_title('Output signal')
ax2.grid(True)

plt.tight_layout()

block_counter = [0]

def animate(frame):
    """animation function"""
    if block_counter[0] >= int(math.floor(LEN / BLOCKLEN)):
        wf.rewind()
        block_counter[0] = 0
        print('Rr')
    input_bytes = wf.readframes(BLOCKLEN)
    
    if len(input_bytes) < BLOCKLEN * WIDTH:
        wf.rewind()
        block_counter[0] = 0
        input_bytes = wf.readframes(BLOCKLEN)
    
    input_tuple = struct.unpack('h' * BLOCKLEN, input_bytes)
    
    # process each sample in the block
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
        y = y * GAIN

        for k in range(M, 0, -1):
            w[k] = w[k - 1] if k - 1 >= 1 else w0
        if y > 32767:
            y = 32767
        elif y < -32768:
            y = -32768
        output_block[n] = int(y)

    input_buffer[:-BLOCKLEN] = input_buffer[BLOCKLEN:]
    input_buffer[-BLOCKLEN:] = input_tuple
    
    output_buffer[:-BLOCKLEN] = output_buffer[BLOCKLEN:]
    output_buffer[-BLOCKLEN:] = output_block

    line1.set_ydata(input_buffer)
    line2.set_ydata(output_buffer)

    output_bytes = struct.pack('h' * BLOCKLEN, *output_block)
    stream.write(output_bytes)
    
    block_counter[0] += 1
    
    return line1, line2

# create animation
print('playback with animation.')
print('close the window to stop.')

ani = animation.FuncAnimation(
    fig,
    animate,
    interval=int(1000 * BLOCKLEN / RATE),  # Update interval in ms
    blit=True,
    cache_frame_data=False)

try:
    plt.show()
except KeyboardInterrupt:
    print('\nStopped by user')

print('Done.')

stream.stop_stream()
stream.close()
p.terminate()
wf.close()