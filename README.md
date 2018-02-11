# audioExtraction

The featureEx class currently plays a song and prints the digital parameters of the file.

Running the script from cmd: <pre>python featureEx.py file_path</pre>

The spectrumAnalyzer class gets an input stream from the laptop mic and plots the real time wave form.
Also displays FFT of microphone audio stream.

The spectrum analyzer QT uses pyqtgraph instead of matplot lib
Reference: https://github.com/markjay4k/Audio-Spectrum-Analyzer-in-Python/blob/master/audio_spectrumQT.py
