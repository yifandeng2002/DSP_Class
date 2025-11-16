import wave, struct, numpy as np

a1 = -1.9
a2 = 0.998
# y = x - a1*y[n-1] - a2*y[n-2]
a = [1.0, a1, a2]
b = [1.0, 0.0, 0.0]

in_wav  = "author.wav"
out_wav = "author_canonical.wav"

with wave.open(in_wav, "rb") as fin:
    nch  = fin.getnchannels()
    sw   = fin.getsampwidth()
    fs   = fin.getframerate()
    assert nch == 1, "Expected mono input wave."

    with wave.open(out_wav, "wb") as fout:
        fout.setnchannels(1)
        fout.setsampwidth(sw)
        fout.setframerate(fs)

        M = max(len(a), len(b)) - 1 
        w = [0.0] * (M + 1)  # use w[1..M] as delays

        # read/process one frame at a time
        frame = fin.readframes(1)
        while frame:
            x = struct.unpack("<h", frame)[0]
            xf = float(x)

            # w0 = x - sum_{k=1..M} a[k]*w[k]
            acc = xf
            for k in range(1, M + 1):
                acc -= a[k] * w[k]
            w0 = acc

            # y = sum_{k=0..M} b[k]*w[k]; with w[0]:= w0
            y = b[0] * w0
            for k in range(1, M + 1):
                y += b[k] * w[k]

            # shift states: w[M]..w[2] = w[M-1]..w[1]; w[1] = w0
            for k in range(M, 0, -1):
                w[k] = w[k - 1] if k - 1 >= 1 else w0

            # clip & write
            yi = int(np.clip(round(y), -32768, 32767))
            fout.writeframes(struct.pack("<h", yi))

            frame = fin.readframes(1)

print("Wrote:", out_wav)