import numpy as np
import pyaudio
import tkinter as tk
import soundfile as sf
from scipy.fftpack import fft, ifft
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class frequencyScaling:
    def __init__(self, audio_file):
        # parameters
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        # read file
        self.audio_data, _ = sf.read(audio_file)
        self.audio_data = self.audio_data.astype(np.float32)
        self.current_index = 0

        # setup pyaudio
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  output=True,
                                  frames_per_buffer=self.CHUNK)
        self.input_block = np.zeros(self.CHUNK)
        self.output_block = np.zeros(self.CHUNK)
        
        # tkinter GUI
        self.root = tk.Tk()
        self.root.title("Frequency Scaling with Real-Time Spectrum")
        self.root.geometry("900x700")
    
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, pady=10)
        
        # slider
        self.scale_var = tk.DoubleVar(value=1.0)
        self.slider = tk.Scale(control_frame, from_=0.5, to=2.0, 
                               resolution=0.1, 
                               orient=tk.HORIZONTAL, 
                               length=300, 
                               variable=self.scale_var,
                               label="Scaling Factor (α)")
        self.slider.pack(side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="Quit", command=self.quit).pack(side=tk.LEFT, padx=10)
        self.setup_plot()

    def setup_plot(self):
        # create figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6))
        self.fig.tight_layout(pad=3.0)
        
        # axis
        self.freq_axis = np.fft.rfftfreq(self.CHUNK, 1/self.RATE)
        # init plot
        self.line1, = self.ax1.plot(self.freq_axis, np.zeros(len(self.freq_axis)), 'b-', linewidth=1)
        self.ax1.set_xlabel('Frequency(Hz)')
        self.ax1.set_ylabel('Magnitude')
        self.ax1.set_title('Input')
        self.ax1.set_xlim(0, self.RATE/2)
        self.ax1.set_ylim(0, 1)
        self.ax1.grid(True, alpha=0.3)
        
        self.line2, = self.ax2.plot(self.freq_axis, np.zeros(len(self.freq_axis)), 'r-', linewidth=1)
        self.ax2.set_xlabel('Frequency(Hz)')
        self.ax2.set_ylabel('Magnitude')
        self.ax2.set_title('Output')
        self.ax2.set_xlim(0, self.RATE/2)
        self.ax2.set_ylim(0, 1)
        self.ax2.grid(True, alpha=0.3)
    
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def update_plot(self):
        input_fft = np.fft.rfft(self.input_block)
        input_magnitude = np.abs(input_fft)
        output_fft = np.fft.rfft(self.output_block)
        output_magnitude = np.abs(output_fft)
        
        input_max = np.max(input_magnitude) if np.max(input_magnitude) > 0 else 1
        output_max = np.max(output_magnitude) if np.max(output_magnitude) > 0 else 1
        
        # update plot
        self.line1.set_ydata(input_magnitude / input_max)
        self.line2.set_ydata(output_magnitude / output_max)
        alpha = self.scale_var.get()
        self.ax1.set_title(f'Input Spectrum')
        self.ax2.set_title(f'Output Spectrum (α = {alpha:.1f})')
        
        #redraw
        self.canvas.draw_idle()

        self.root.after(50, self.update_plot)

    def process_block(self, block, scaling_factor):
        #FFT
        spectrum = fft(block)
        N = len(spectrum)
        scaled_spectrum = np.zeros_like(spectrum, dtype=np.complex128)
        
        # interpolation-based scaling
        for k in range(N):
            old_index = k / scaling_factor
            if 0 <= old_index < N-1:
                # linear interpolation
                index_floor = int(old_index)
                index_ceil = index_floor + 1
                weight = old_index - index_floor
                scaled_spectrum[k] = (1-weight)*spectrum[index_floor] + weight*spectrum[index_ceil]
        
        # inverse FFT to get time domain signal
        return np.real(ifft(scaled_spectrum))

    def audio_callback(self):
        scaling_factor = self.scale_var.get()
        
        # get the audio block
        block = self.audio_data[self.current_index:self.current_index+self.CHUNK]
        # loop audio
        if len(block) < self.CHUNK:
            self.current_index = 0
            block = self.audio_data[self.current_index:self.current_index+self.CHUNK]
        if len(block) < self.CHUNK:
            block = np.pad(block, (0, self.CHUNK - len(block)), 'constant')
        
        self.input_block = block.copy()
        # process the block
        processed_block = self.process_block(block, scaling_factor)
        self.output_block = processed_block.copy()
        
        # write to stream
        self.stream.write(processed_block.astype(np.float32).tobytes())
        self.current_index += self.CHUNK 
        # next callback
        self.root.after(20, self.audio_callback)

    def quit(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.root.quit()
        plt.close(self.fig)

    def run(self):
        self.audio_callback()
        self.update_plot()
        self.root.mainloop()

if __name__ == "__main__":
    scaler = frequencyScaling("question_2/author.wav")
    scaler.run()