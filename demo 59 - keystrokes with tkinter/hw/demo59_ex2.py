import pyaudio
import numpy as np
from scipy import signal
from math import sin, cos, pi
import tkinter as Tk

# audio settings
BLOCKLEN = 64
WIDTH = 2
CHANNELS = 1
RATE = 8000
MAXVALUE = 2**15 - 1

Ta = 1.0        # fade out
f0 = 440.0      # starting frequency (middle A)

# mappings
KEY_MAP = {
    'a': 0,   # A
    'w': 1,   # A#
    's': 2,   # B
    'd': 3,   # C
    'r': 4,   # C#
    'f': 5,   # D
    't': 6,   # D#
    'g': 7,   # E
    'h': 8,   # F
    'u': 9,   # F#
    'j': 10,  # G
    'i': 11   # G#
}


class NoteFilter:
    def __init__(self, freq):
        self.r = 0.01**(1.0/(Ta*RATE))
        self.om = 2.0 * pi * freq/RATE
        
        # set up the filter numbers
        self.a = [1, -2*self.r*cos(self.om), self.r**2]
        self.b = [self.r*sin(self.om)]
        self.states = np.zeros(2)
        self.x = np.zeros(BLOCKLEN)

# make 12 filters, one for each note in the octave
notes = []
for k in range(12):
    freq = f0 * (2**(k/12.0))
    notes.append(NoteFilter(freq))

# setup audio output
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=CHANNELS,
    rate=RATE,
    input=False,
    output=True,
    frames_per_buffer=BLOCKLEN
)

CONTINUE = True
KEYPRESSES = []

def my_function(event):
    global CONTINUE, KEYPRESSES
    
    if event.char == 'q':
        print('Good bye')
        CONTINUE = False
    elif event.char in KEY_MAP:
        note_index = KEY_MAP[event.char]
        KEYPRESSES.append(note_index)
        print(f'Playing note {note_index} (key: {event.char})')

# window
root = Tk.Tk()
root.title("Keyboard")
root.bind("<Key>", my_function)

# instructions
info = Tk.Label(root, text="Keyboard Layout:")
info.pack()
layout = Tk.Label(root, text="A W S D R F T G H U J I")
layout.pack()
notes_label = Tk.Label(root, text="A A# B C C# D D# E F F# G G#")
notes_label.pack()
quit_label = Tk.Label(root, text="Press Q to quit.")
quit_label.pack()

print('Press to play notes:')
print('  A W S D R F T G H U J I')
print('  A A# B C C# D D# E F F# G G#')
print('Press Q to quit.')

while CONTINUE:
    root.update()

    while KEYPRESSES:
        note_index = KEYPRESSES.pop(0)
        notes[note_index].x[0] = 10000.0
    total_output = np.zeros(BLOCKLEN)
    
    for note in notes:
        [y, note.states] = signal.lfilter(note.b, note.a, note.x, zi=note.states)
        total_output += y
        note.x[0] = 0.0

    total_output = np.clip(total_output, -MAXVALUE, MAXVALUE)
    y_16bit = total_output.astype('int16')
    y_bytes = y_16bit.tobytes()
    stream.write(y_bytes, BLOCKLEN)

print('Done.')

stream.stop_stream()
stream.close()
p.terminate()
root.destroy()