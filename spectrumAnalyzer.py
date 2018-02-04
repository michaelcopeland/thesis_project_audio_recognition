"""Displays real time audio wave form from input stream.

Script uses microphone to receive audio input stream.
"""

# TO DO: convert to use wave
# TO DO: convert to input .wav file
# https://people.csail.mit.edu/hubert/pyaudio/docs/

import time
import pyaudio
import struct  # allows conversion of audio data to ints
import numpy as np
import matplotlib.pyplot as plt
plt.interactive(True) # ensures matplotlib opens a new window

# format constants
CHUNK    = 1024 * 2
FORMAT   = pyaudio.paInt16
CHANNELS = 1 # MONO
RATE     = 44100 # Hz

# instance of pyaudio
p = pyaudio.PyAudio()

# audio input stream object
stream = p.open(
    format            = FORMAT,
    channels          = CHANNELS,
    rate              = RATE,
    input             = True, # mic
    output            = True,
    frames_per_buffer = CHUNK
)
# figure and axes fig size - height width in inches
fig, ax = plt.subplots(1, figsize=(10, 8))

# variable used to plot
x = np.arange(0, 2*CHUNK, 2)

#line obj with random data
#TO DO: don't generate random input
line, = ax.plot(x, np.random.rand(CHUNK), '-', color='k', lw=0.5)

# axis formatting
ax.set_title('Waveform')
ax.set_xlabel('samples')
ax.set_ylabel('amplitude')
ax.set_ylim(0, 512)
ax.set_xlim(0, CHUNK)
plt.setp(ax, xticks=[0, CHUNK/2, CHUNK], yticks=[0, 256, 512])

plt.show(block=False)

print('audio stream active')

frame_count = 0
start_time = time.time()

while True:
    data = stream.read(CHUNK)  # returns list of hex
    data_int = struct.unpack(str(2 * CHUNK) + 'B', data)  # sample twice the chunk because nyquist-shannon
    data_int_np = np.array(data_int, dtype='b')[::2] + 256

    line.set_ydata(data_int_np)

    # update canvas
    try:
        fig.canvas.draw()
        fig.canvas.flush_events()
        frame_count += 1
    # fix exception
    except KeyboardInterrupt:
        frame_rate = frame_count / (time.time() - start_time)
        print('Average frames per second: {:.0f} FPS'.format(frame_rate))
        print('Audio stream terminated')
        break