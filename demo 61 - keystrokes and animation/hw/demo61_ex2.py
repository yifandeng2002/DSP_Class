import sys
import threading
import queue
import numpy as np
import pyaudio
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation

FS = 44100
BLOCK = 256
F0 = 440.0   # base frequency
R = 0.996    # pole radius (decay)
WAVE_SAMPLES_TO_SHOW = 2000   # live waveform history
OUT_GAIN = 0.2          # master output gain

# mappings
KEYS = ['a','w','s','e','d','f','t','g','y','h','u','j']
SEMITONES = list(range(12))  # 0..11
KEY_TO_K = {k: i for k, i in zip(KEYS, SEMITONES)}

class ResonatorVoice:
    def __init__(self, fs, freq, r=R):
        self.fs = fs
        self.freq = freq
        self.r = r
        self._update_coeffs()
        self.y1 = 0.0
        self.y2 = 0.0
        self.trigger_flag = False 

    def _update_coeffs(self):
        w0 = 2.0 * np.pi * (self.freq / self.fs)
        self.a1 = 2.0 * self.r * np.cos(w0)
        self.a2 = -(self.r ** 2)  # y[n] = a1*y[n-1] + a2*y[n-2] + x[n]

    def trigger(self, strength=1.0):
        self.trigger_flag = True

    def process_block(self, N):
        out = np.zeros(N, dtype=np.float32)
        y1, y2 = self.y1, self.y2
        a1, a2 = self.a1, self.a2
        # single-sample impulse
        x0 = 1.0 if self.trigger_flag else 0.0
        self.trigger_flag = False

        # first sample with potential impulse
        y = a1 * y1 + a2 * y2 + x0
        out[0] = y
        y2, y1 = y1, y
        for n in range(1, N):
            y = a1 * y1 + a2 * y2
            out[n] = y
            y2, y1 = y1, y

        self.y1, self.y2 = y1, y2
        return out

class PolySynth:
    def __init__(self, fs=FS, f0=F0):
        self.fs = fs
        self.voices = []
        for k in range(12):
            fk = (2.0 ** (k / 12.0)) * f0
            self.voices.append(ResonatorVoice(fs, fk))

    def note_on(self, k):
        if 0 <= k < 12:
            self.voices[k].trigger()

    def render_block(self, N):
        # sum all voices
        mix = np.zeros(N, dtype=np.float32)
        for v in self.voices:
            mix += v.process_block(N)
        mix *= OUT_GAIN
        mix = np.tanh(mix)  # limiting
        return mix

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Keyboard")

        label = tk.Label(self.root, text="Press keys: " + " ".join(KEYS) + "  (chords allowed)")
        label.pack(pady=4)

        self.fig = Figure(figsize=(7, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Output Waveform")
        self.ax.set_xlabel("Samples")
        self.ax.set_ylabel("Amplitude")
        self.ax.set_ylim(-1.1, 1.1)
        self.line, = self.ax.plot([], [], lw=1)
        self.buffer = np.zeros(WAVE_SAMPLES_TO_SHOW, dtype=np.float32)

        canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # audio + synth
        self.synth = PolySynth()
        self.audio_q = queue.Queue(maxsize=64)  # receive audio blocks from callback for plotting

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=FS,
                                  output=True,
                                  frames_per_buffer=BLOCK,
                                  stream_callback=self._audio_callback)

        # bind keys
        self.root.bind("<KeyPress>", self.on_key)
        # animation
        self.ani = animation.FuncAnimation(self.fig, self._update_plot, interval=30, blit=False)

        self.stream.start_stream()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def on_key(self, event):
        ch = event.char.lower()
        if ch in KEY_TO_K:
            self.synth.note_on(KEY_TO_K[ch])

    def _audio_callback(self, in_data, frame_count, time_info, status_flags):
        block = self.synth.render_block(frame_count)
        try:
            self.audio_q.put_nowait(block.copy())
        except queue.Full:
            pass
        return (block.tobytes(), pyaudio.paContinue)

    def _update_plot(self, frame):
        while True:
            try:
                block = self.audio_q.get_nowait()
                L = len(block)
                if L >= len(self.buffer):
                    self.buffer[:] = block[-len(self.buffer):]
                else:
                    self.buffer = np.roll(self.buffer, -L)
                    self.buffer[-L:] = block
            except queue.Empty:
                break
        # update plot
        x = np.arange(len(self.buffer))
        self.line.set_data(x, self.buffer)
        self.ax.set_xlim(0, len(self.buffer)-1)
        return self.line,

    def close(self):
        try:
            if self.stream.is_active():
                self.stream.stop_stream()
            self.stream.close()
        except Exception:
            pass
        try:
            self.p.terminate()
        except Exception:
            pass
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        App().run()
    except KeyboardInterrupt:
        sys.exit(0)
