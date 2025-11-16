import pyaudio
import matplotlib
from matplotlib import pyplot
from matplotlib import animation
import numpy as np
from scipy.signal import butter, lfilter

matplotlib.use('TkAgg')

print('The matplotlib backend is %s' % pyplot.get_backend())

WIDTH = 2
CHANNELS = 1
RATE = 8000
BLOCKLEN = 256

print('Block length: %d' % BLOCKLEN)
print('Duration of block (msec): %.1f' % (1000.0 * BLOCKLEN/RATE))

p = pyaudio.PyAudio()
PA_FORMAT = p.get_format_from_width(WIDTH)
stream = p.open(
    format = PA_FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input = True,
    output = True,
    frames_per_buffer = BLOCKLEN)

# create high-pass Butterworth filter
ORDER = 3
fc = 0.1
[b, a] = butter(ORDER, 2 * fc, btype = 'high')
states = np.zeros(ORDER)

# set up plots
my_fig = pyplot.figure(1)
my_fig.set_size_inches((10, 6))

ax1 = my_fig.add_subplot(2, 2, 1)
ax2 = my_fig.add_subplot(2, 2, 2)
ax3 = my_fig.add_subplot(2, 2, 3)
ax4 = my_fig.add_subplot(2, 2, 4)

t = np.arange(BLOCKLEN) * (1000/RATE)
x = np.zeros(BLOCKLEN)
X = np.fft.rfft(x)
f_X = np.arange(X.size) * RATE/BLOCKLEN

# input signal plot
[g1] = ax1.plot([], [])
ax1.set_xlim(0, 1000 * BLOCKLEN/RATE)
ax1.set_ylim(-10000, 10000)
ax1.set_xlabel('Time (msec)')
ax1.set_title('Input Signal')

# input spectrum plot
[g2] = ax2.plot([], [])
ax2.set_xlim(0, RATE/2)
ax2.set_ylim(0, 1000)
ax2.set_xlabel('Frequency (Hz)')
ax2.set_title('Input Spectrum')

# output signal plot
[g3] = ax3.plot([], [])
ax3.set_xlim(0, 1000 * BLOCKLEN/RATE)
ax3.set_ylim(-10000, 10000)
ax3.set_xlabel('Time (msec)')
ax3.set_title('Output Signal')

# output spectrum plot
[g4] = ax4.plot([], [])
ax4.set_xlim(0, RATE/2)
ax4.set_ylim(0, 1000)
ax4.set_xlabel('Frequency (Hz)')
ax4.set_title('Output Spectrum')

my_fig.tight_layout()

# animation functions
def my_init():
    g1.set_xdata(t)
    g2.set_xdata(f_X)
    g3.set_xdata(t)
    g4.set_xdata(f_X)
    return (g1, g2, g3, g4)

def my_update(i):
    global states
    signal_bytes = stream.read(BLOCKLEN, exception_on_overflow = False)
    x = np.frombuffer(signal_bytes, dtype = 'int16')
    
    # apply high-pass filter
    [y, states] = lfilter(b, a, x, zi = states)
    # compute spectra
    X = np.fft.rfft(x) / BLOCKLEN
    Y = np.fft.rfft(y) / BLOCKLEN

    # update plots
    g1.set_ydata(x)
    g2.set_ydata(np.abs(X))
    g3.set_ydata(y)
    g4.set_ydata(np.abs(Y))
    
    stream.write(y.astype('int16').tobytes(), BLOCKLEN)
    return (g1, g2, g3, g4)

# run animation
my_anima = animation.FuncAnimation(
    my_fig,
    my_update,
    init_func = my_init,
    interval = 10,
    blit = True,
    cache_frame_data = False,
    repeat = False
)
pyplot.show()

stream.stop_stream()
stream.close()
p.terminate()

print('Done.')