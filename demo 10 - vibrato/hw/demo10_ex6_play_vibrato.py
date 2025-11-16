import pyaudio
import wave
import struct
import math
from myfunctions import clip16

LFO_TYPE = 'square'
# 'sine', 'triangle', 'square', 'exponential'
wavfile = 'author.wav'
output_wavfile = f'author_vibrato_{LFO_TYPE}.wav'

print('Play the wave file: %s with %s LFO.' % (wavfile, LFO_TYPE))

wf = wave.open(wavfile, 'rb')

# read wave file
RATE        = wf.getframerate()
WIDTH       = wf.getsampwidth()
LEN         = wf.getnframes()
CHANNELS    = wf.getnchannels()

print('The file has %d channel(s).'         % CHANNELS)
print('The file has %d frames/second.'      % RATE)
print('The file has %d frames.'             % LEN)
print('The file has %d bytes per sample.'   % WIDTH)

#vibrato parameters
f0 = 2          # LFO freq
W = 0.015       # sweep width
                
Wd = W * RATE   # W in units of discrete samples

freq_ratio = 1 + W * 2 * math.pi * f0
print('The frequency ratio is %.5f \n' % freq_ratio)

# buffer to store past values
BUFFER_LEN =  1024          # buffer length
buffer = BUFFER_LEN * [0]
kr = 0  # read index
i1 = kr
kw = int(0.5 * BUFFER_LEN)  # write index

print('The buffer is %d samples long.' % BUFFER_LEN)

# Open output wave file
wf_output = wave.open(output_wavfile, 'w')
wf_output.setnchannels(1)
wf_output.setsampwidth(WIDTH)
wf_output.setframerate(RATE)

p = pyaudio.PyAudio()
stream = p.open(format      = pyaudio.paInt16,
                channels    = 1,
                rate        = RATE,
                input       = False,
                output      = True)

print('* Playing and saving to %s...' % output_wavfile)

def lfo_sine(n, f0, RATE):
    """ standard sinusoidal LFO """
    return math.sin(2 * math.pi * f0 * n / RATE)

def lfo_triangle(n, f0, RATE):
    """ triangle wave LFO """
    period = RATE / f0
    phase = (n % period) / period
    if phase < 0.25:
        return 4 * phase
    elif phase < 0.75:
        return 2 - 4 * phase
    else:
        return 4 * phase - 4

def lfo_square(n, f0, RATE):
    """ square wave LFO """
    period = RATE / f0
    phase = (n % period) / period
    return 1.0 if phase < 0.5 else -1.0

def lfo_exponential(n, f0, RATE):
    """ exponential LFO"""
    period = RATE / f0
    phase = (n % period) / period
    return 2 * (math.exp(2 * phase) - 1) / (math.exp(2) - 1) - 1

# select LFO function
lfo_functions = {
    'sine': lfo_sine,
    'triangle': lfo_triangle,
    'square': lfo_square,
    'exponential': lfo_exponential
}

lfo_func = lfo_functions[LFO_TYPE]

for n in range(0, LEN):
    input_bytes = wf.readframes(1)
    x0, = struct.unpack('h', input_bytes)

    # get previous and next buffer
    kr_prev = int(math.floor(kr))
    frac = kr - kr_prev
    kr_next = kr_prev + 1
    if kr_next == BUFFER_LEN:
        kr_next = 0

    # compute output value using interpolation
    y0 = (1-frac) * buffer[kr_prev] + frac * buffer[kr_next]

    # update buffer
    buffer[kw] = x0

    i1 = i1 + 1
    if i1 >= BUFFER_LEN:
        i1 = i1 - BUFFER_LEN

    # calculate kr
    kr = i1 + Wd * lfo_func(n, f0, RATE)
    if kr >= BUFFER_LEN:
        kr = kr - BUFFER_LEN
    elif kr < 0:
        kr = kr + BUFFER_LEN

    kw = kw + 1
    if kw == BUFFER_LEN:
        kw = 0

    output_bytes = struct.pack('h', int(clip16(y0)))
    stream.write(output_bytes)
    wf_output.writeframes(output_bytes)

print('Done.')
print('Output saved to: %s' % output_wavfile)

stream.stop_stream()
stream.close()
p.terminate()
wf.close()
wf_output.close()