import pyaudio
import numpy as np

SAMPLE_RATE = 8000
CHUNK_SIZE = 256
DURATION = 3  #seconds

# Karplus-Strong parameters
K = 0.93
N = 60  # delay length

def karplus_strong_realtime():
    # initialize circular buffer with a random noise
    buffer = np.random.randn(N + 2)
    buffer_index = 0
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paFloat32,
        channels=1,
        rate=SAMPLE_RATE,
        output=True,
        frames_per_buffer=CHUNK_SIZE
    )
    
    print("playing...")
    print(f"K={K}, N={N}, Fs={SAMPLE_RATE}Hz")
    
    # generate and play audio
    total_samples = int(SAMPLE_RATE * DURATION)
    
    for i in range(0, total_samples, CHUNK_SIZE):
        output_chunk = np.zeros(CHUNK_SIZE, dtype=np.float32)
        
        for j in range(CHUNK_SIZE):
            # get delayed sample from buffer
            idx1 = (buffer_index - N) % len(buffer)
            idx2 = (buffer_index - N - 1) % len(buffer)

            #y(n) = K/2 * y(n-N) + K/2 * y(n-N-1)
            output_sample = (K / 2) * buffer[idx1] + (K / 2) * buffer[idx2]
            
            # store in buffer
            buffer[buffer_index] = output_sample
            buffer_index = (buffer_index + 1) % len(buffer)     
            # add to output chunk
            output_chunk[j] = output_sample

        output_chunk = output_chunk / np.max(np.abs(output_chunk) + 1e-8)
        stream.write(output_chunk.astype(np.float32).tobytes())
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    print("Done.")

if __name__ == "__main__":
    karplus_strong_realtime()
