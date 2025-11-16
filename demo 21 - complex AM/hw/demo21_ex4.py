#!/usr/bin/env python3

# complex AM effect - realtime stuff
# dsp lab exercise 4

import numpy as np
import pyaudio
import matplotlib.pyplot as plt
from scipy import signal

# audio settings
RATE = 8000          # sampling rate 
CHUNK = 512          # buffer size
f1 = 400            # modulation freq

# make the complex filter
# basically we take a lowpass filter and shift it
b_lpf, a_lpf = signal.ellip(7, 0.2, 50, 0.48)  
n = np.arange(8)
s = 1j ** n         # this is same as exp(j*pi/2*n)
b = b_lpf * s       
a = a_lpf * s

# init filter state
zi = signal.lfilter_zi(b, a) * 0

# audio setup
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, 
               channels=1, 
               rate=RATE,
               input=True, 
               output=True, 
               frames_per_buffer=CHUNK)

# make the plots
plt.ion()
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 8))
fig.suptitle('Complex AM - Realtime')

# buffers for plotting
plot_len = 2048
x_plot = np.zeros(plot_len)
y_plot = np.zeros(plot_len)
t_plot = np.arange(plot_len) / RATE

# frequency axis
freq = np.fft.fftfreq(plot_len, 1/RATE)
freq_shifted = np.fft.fftshift(freq)

# plot lines
line1, = ax1.plot(t_plot, x_plot, 'b-', linewidth=0.8)
line2, = ax2.plot(t_plot, y_plot, 'r-', linewidth=0.8)
line3, = ax3.plot(freq_shifted, np.zeros(plot_len), 'b-', linewidth=0.8)
line4, = ax4.plot(freq_shifted, np.zeros(plot_len), 'r-', linewidth=0.8)

# setup axes
ax1.set_title('Input x(t)')
ax1.set_ylim([-0.5, 0.5])
ax1.set_xlabel('Time (s)')
ax1.grid(True, alpha=0.3)

ax2.set_title('Output y(t)')
ax2.set_ylim([-0.5, 0.5])
ax2.set_xlabel('Time (s)')
ax2.grid(True, alpha=0.3)

ax3.set_title('Input Spectrum')
ax3.set_xlim([-2000, 2000])
ax3.set_ylim([0, 50])
ax3.set_xlabel('Frequency (Hz)')
ax3.grid(True, alpha=0.3)

ax4.set_title(f'Output Spectrum (shifted {f1} Hz)')
ax4.set_xlim([-2000, 2000])
ax4.set_ylim([0, 50])
ax4.set_xlabel('Frequency (Hz)')
ax4.grid(True, alpha=0.3)

plt.tight_layout()

# tracking phase for modulation
phase = 0
frame_count = 0

print(f"running complex AM with f1={f1}Hz")
print("talk into the mic, close the window when done")

try:
    while plt.fignum_exists(fig.number):
        # grab audio
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            x = np.frombuffer(data, dtype=np.float32)
        except:
            continue
        
        # do the complex filtering
        r, zi = signal.lfilter(b, a, x, zi=zi)
        
        # complex modulation part
        t = np.arange(CHUNK) / RATE + phase
        g = r * np.exp(1j * 2 * np.pi * f1 * t)
        phase += CHUNK / RATE
        
        # get real part
        y = np.real(g)
        
        # output audio
        stream.write(y.astype(np.float32).tobytes())
        
        # shift buffers
        x_plot = np.roll(x_plot, -CHUNK)
        x_plot[-CHUNK:] = x
        y_plot = np.roll(y_plot, -CHUNK)  
        y_plot[-CHUNK:] = y
        
        # update visuals every other frame
        frame_count = frame_count + 1
        if frame_count % 2 == 0:
            # time plots
            line1.set_ydata(x_plot)
            line2.set_ydata(y_plot)
            
            # freq plots
            X = np.fft.fft(x_plot)
            Y = np.fft.fft(y_plot)
            line3.set_ydata(np.fft.fftshift(np.abs(X)))
            line4.set_ydata(np.fft.fftshift(np.abs(Y)))
            
            # redraw
            fig.canvas.draw()
            fig.canvas.flush_events()
        
except KeyboardInterrupt:
    print("\nctrl-c detected")
except:
    pass
    
# cleanup
print("shutting down...")
stream.stop_stream()  
stream.close()
p.terminate()
plt.close()
print("Done.")