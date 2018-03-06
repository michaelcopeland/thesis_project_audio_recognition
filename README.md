# Landmark based audio fingerprinter

In order to fingerprint a .wav song:

<pre> python pyFingerprint.py yourfile.wav </pre>

It works for 32, 16, and 8 bit wav. Still working on the 24-bit.

Requirements:
matplotlib
numpy
pyaudio
pydub
wave
scipy
hashlib

######OTHER STUFF########

The featureEx class can extract the spectral domain from a wave file. It computes a spectrogram and can split it into a number of chunks.

Currently working on a hash function similar to the one used by the Landmark algorithm.

Running the script from cmd: <pre>python featureEx.py file_path</pre>
This will read the file, display inforamtion regarding its encoding. It will break it up into chunks and return top frequency points.

The spectrumAnalyzer class gets an input stream from the laptop mic and plots the real time wave form.
Also displays FFT of microphone audio stream.

The spectrum analyzer QT uses pyqtgraph instead of matplot lib
Reference: https://github.com/markjay4k/Audio-Spectrum-Analyzer-in-Python/blob/master/audio_spectrumQT.pyR
Breaking up file into chunks: https://github.com/notexactlyawe/abracadabra/blob/master/fingerprint.ipynb
