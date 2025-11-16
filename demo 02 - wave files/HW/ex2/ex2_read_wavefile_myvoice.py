import wave

file_name = "myvoice16.wav"

wf = wave.open(file_name, 'rb')

num_channels = wf.getnchannels()
fs = wf.getframerate()
num_frames = wf.getnframes()
sample_width = wf.getsampwidth()

print("File:", file_name)
print("Number of channels:", num_channels)
print("Sampling rate:", fs)
print("Number of frames:", num_frames)
print("Sample width:", sample_width)

wf.close()