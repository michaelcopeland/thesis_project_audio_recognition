"""Displays real time audio wave form from input stream.

Script uses microphone to receive audio input stream.
"""

# TO DO: convert to use wave
# TO DO: convert to input .wav file
# https://people.csail.mit.edu/hubert/pyaudio/docs/

import os
import time
import pyaudio
import struct  # allows conversion of audio data to ints
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
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
fig, (ax, ax_fft) = plt.subplots(2, figsize=(10, 8))

# variables used to plot
x     = np.arange(0, 2*CHUNK, 2)
x_fft = np.linspace(0, RATE, CHUNK)

#line obj with random data
#TO DO: don't generate random input, the y data does not actually matter much since it is received in the loop
line,     = ax.plot(x, np.random.rand(CHUNK), '-', color='k', lw=0.5)
line_fft, = ax_fft.semilogx(x_fft, np.random.rand(CHUNK), '-', color='k', lw=0.5)

# axis formatting
ax.set_title('Time domain waveform')
ax.set_xlabel('samples')
ax.set_ylabel('amplitude')
ax.set_ylim(0, 1024)
ax.set_xlim(0, 2*CHUNK)

ax_fft.set_title('Frequency domain')
ax_fft.set_xlabel('samples')
ax_fft.set_ylabel('frequency')
#ax_fft.set_ylim(0, 1024)
ax_fft.set_xlim(20, RATE / 2)

plt.setp(ax, xticks=[0, CHUNK, 2*CHUNK], yticks=[0, 512, 1024])

plt.show(block=False)

print('audio stream active')

frame_count = 0
start_time  = time.time()

while True:
    data = stream.read(CHUNK)  # returns list of hex
    data_int = struct.unpack(str(2 * CHUNK) + 'B', data)  # sample twice the chunk because nyquist-shannon
    data_int_np = np.array(data_int, dtype='b')[::2] + 512

    line.set_ydata(data_int_np)

    y_fft = fft(data_int_np)
    # sliced from 0 to chunk
    line_fft.set_ydata(np.abs(y_fft[0:CHUNK]) * 2 / (256 * CHUNK))

    # update canvas
    try:
        fig.canvas.draw()
        fig.canvas.flush_events()
        frame_count += 1
    # fix exception
    except:
        if KeyboardInterrupt:
            frame_rate = frame_count / (time.time() - start_time)
            print('Average frames per second: {:.0f} FPS'.format(frame_rate))
            print('Audio stream terminated')
            break