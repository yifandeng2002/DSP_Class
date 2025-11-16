import numpy as np, soundfile as sf

ref_path = "/Users/yifan/Documents/WebD/DSP_class/demo 06 - filter wave file/author_canonical.wav"       # from the original demo program
test_path = "author_canonical.wav"   # from your Exercise 4 program

ref, fs1 = sf.read(ref_path, dtype="int16")   # int16 preserves raw PCM values
test, fs2 = sf.read(test_path, dtype="int16")

assert fs1 == fs2, "Sample rates differ"
assert ref.shape == test.shape, "Signal shapes differ"

same = np.array_equal(ref, test)
max_abs = int(np.max(np.abs(ref.astype(np.int32) - test.astype(np.int32))))
num_diff = int(np.sum(ref != test))
first_idx = int(np.argmax(ref != test)) if num_diff else None

print("Bit-exact equal:", same)
print("Differing samples:", num_diff)
print("Max |diff| (LSBs):", max_abs)
print("First diff index:", first_idx)