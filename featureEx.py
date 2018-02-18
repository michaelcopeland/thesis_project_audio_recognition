import sys
import wave
import pyaudio
import numpy as np
from scipy.fftpack import fft
import matplotlib.pyplot as plt
import time
from wavehelper import WaveHelper

class featureExtractor():
    """Retrieves features from audio files"""

    def __init__(self, filename='No file input'):
        self.filename = filename

    def open_stream(self):
        if (len(sys.argv) < 2):
            print('No file input')
            sys.exit(-1)

        print('Opened {0}'.format(self.filename))

        self.wf = wave.open(self.filename)

    def play(self):
        print('play!')
        self.p = pyaudio.PyAudio()

        # pyaudio config defaults
        self.FORMAT = self.p.get_format_from_width(self.wf.getsampwidth())
        self.CHANNELS = self.wf.getnchannels()
        self.RATE = self.wf.getframerate()  # changes the pitch
        self.CHUNK = 1024

        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            output=True,
            frames_per_buffer=self.CHUNK
        )

        start_time = time.time()
        # the wave chunks are a series of hex length 2048
        data = self.wf.readframes(self.CHUNK)
        while len(data) > 0:
            # plays the file
            self.stream.write(data)
            data = self.wf.readframes(self.CHUNK)

        stop_time = time.time()
        print('Elapsed play time: {0:.5f} seconds'.format(stop_time - start_time))
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        print('playback done')

    def print_wav_stats(self):
        print(self.wf.getparams())

    def get_audio_data(self):
        """retrieves audio data for the entire wav file"""
        audio = WaveHelper(self.filename)
        aud = audio.read_whole()

        #plt.plot(aud)
        plt.title("Waveform of sound file")
        #plt.show()
        return aud

    def get_fft(self):
        aud = self.get_audio_data()
        transform = fft(aud)

        # frequency coefficients
        frequency_series = 2 / len(transform) * np.abs(transform[:len(transform)//2])
        xf = np.linspace(0, self.wf.getframerate()/2, len(transform)/2)

        mel = self.to_mel(xf)
        newmel, newy = self.to_int_version(mel, frequency_series)
        plt.plot(newmel, newy)
        plt.title("Frequency spectrum")
        plt.ylabel("Power")
        plt.xlabel("Frequency (Hz)")
        plt.show()

        print("length of audio: {}, length of fft: {}".format(len(aud), len(transform)))

    def get_frequencies(self, aud, len_aud, smpl_rate):
        """returns the power frequency spectrum. the frequency spectrum is converted to the mel scale"""
        transform = fft(aud)
        l_trans = len(transform)

        yf = 2 / len_aud * np.abs(transform[:l_trans//2])
        xf = np.linspace(0, smpl_rate / 2, int(l_trans/2))

        mel = self.to_mel(xf)
        return self.to_int_version(mel, yf)

    def to_mel(self, iterable):
        """converts to mel scale"""
        return 2595 * np.log10(1 + (iterable/700))

    def to_int_version(self, xlist, ylist):
        """Given a list of x values and a list of y values it will produce new lists
        where the x values have all been rounded to the nearest integers and the
        corresponding y values averaged.
        [715.2364, 715.3462, 715.5693, 716.2054], [12, 10, 13, 16] would produce
        [715, 716], [11, 14.5]"""
        prev = 0
        d = []
        new_X = []
        new_y = []
        for idx, x in enumerate(xlist):
            if round(x) != prev:
                if d != []:
                    new_X.append(prev)
                    new_y.append(np.mean(d))
                prev = int(round(x))
                d = []
            d.append(ylist[idx])
        new_X.append(prev)
        new_y.append(np.mean(d))
        return new_X, new_y


if __name__ == '__main__':
    fe = featureExtractor(filename=sys.argv[1])
    fe.open_stream()
    fe.print_wav_stats()
    #fe.get_fft()

    audio = fe.get_audio_data()
    sample_rate = fe.wf.getframerate()
    frequencies = fe.get_frequencies(audio, len(audio), sample_rate)

    plt.plot(*frequencies)
    plt.show()
    #fe.play()
