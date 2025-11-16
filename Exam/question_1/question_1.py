import numpy as np
import pyaudio
import tkinter as tk
import soundfile as sf
from scipy.fftpack import fft, ifft

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

        # tkinter GUI
        self.root = tk.Tk()
        self.root.title("frequency scaling")
        # slider
        self.scale_var = tk.DoubleVar(value=1.0)
        self.slider = tk.Scale(self.root, from_=0.5, to=2.0, 
                               resolution=0.1, 
                               orient=tk.HORIZONTAL, 
                               length=300, 
                               variable=self.scale_var,
                               label="Factor")
        self.slider.pack(pady=20)
        tk.Button(self.root, text="quit", command=self.quit).pack(pady=10)

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
        
        # inverse FFT to get time-domain signal
        return np.real(ifft(scaled_spectrum))

    def audio_callback(self):
        scaling_factor = self.scale_var.get()
        
        # get the audio block
        block = self.audio_data[self.current_index:self.current_index+self.CHUNK]
        # loop audio
        if len(block) < self.CHUNK:
            self.current_index = 0
            block = self.audio_data[self.current_index:self.current_index+self.CHUNK]
        processed_block = self.process_block(block, scaling_factor)
        
        # write to stream
        self.stream.write(processed_block.astype(np.float32).tobytes())
        self.current_index += self.CHUNK
        
        #next callback
        self.root.after(20, self.audio_callback)

    def quit(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.root.quit()

    def run(self):
        self.audio_callback()
        self.root.mainloop()

if __name__ == "__main__":
    scaler = frequencyScaling("question_1/author.wav")
    scaler.run()