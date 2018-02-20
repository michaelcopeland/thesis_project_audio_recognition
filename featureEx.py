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
        self.helper = WaveHelper(self.filename)

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
        aud = self.helper.read_whole()

        #plt.plot(aud)
        #plt.title("Waveform of sound file")
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

    @staticmethod
    def chunks(snippet, step):
        # lower, upper, step
        for i in range(0, len(snippet), step):
            yield snippet[i:i+step]

    def generate_spectrogram(self):
        # ms_per_chunk = 16

        sgram = []
        s_per_n = 1024 #self.helper.samples_per_n_mili(ms_per_chunk)
        print('samples: ', s_per_n)

        count = 1
        # for chunk in self.chunks(self.get_audio_data(), s_per_n):
        for chunk in self.chunks(self.get_audio_data(), s_per_n):

            # s_per_n changed to chunk size 1024
            sgram.append(self.get_frequencies(chunk, s_per_n, self.wf.getframerate()))
            print('\rChunk {}'.format(count), end='')
            count += 1
        print()

        #freq_scales = []
        #for elem in sgram:
        #    if elem[0] not in freq_scales:
        #        freq_scales.append(elem[0])
        #print(len(freq_scales))
        #print(sgram[0][0][:10])
        self.to_csv(sgram)

        sgram_y = np.array([], dtype=np.float_, ndmin=1)
        for li in sgram:
            sgram_y = np.hstack((sgram_y, li[1]))
            #else:
             #   sgram_y = np.vstack((sgram_y, li[1]))

        img = plt.matshow(sgram_y.T, origin='lower', extent=[0, 1000, 0, 350])

        img.set_cmap('gnuplot')
        plt.show()

        return sgram, sgram_y

    def to_csv(self, iterable):
        """helper method

        log to csv, iterables may be nested lists, deal with it
        """
        with open('sgram.csv', 'w') as myfile:
            for list in iterable:
                for elem in list:
                    myfile.write(',' + str(elem))
                myfile.write('\n')
        myfile.close()

    def generate_constellation_map(self):
        ms_per_chunk = 16
        sgram, sgram_y = self.generate_spectrogram()
        density = 0.02 # want top 2% of points
        n_windows = 5
        window_length = len(sgram_y[0])

        points_per_chunk = int(window_length * n_windows * density)
        print('points per chunk: ', points_per_chunk)

        count = 0

        # time: ms, freq: mel
        max_idx = []

        for window in self.chunks(sgram_y, n_windows):
            # flatten the multidimensional windows into a one dimensional list
            flat = [item for sulist in window for item in sulist]
            # retrieve top points
            sort = sorted(flat, reverse=True)[:points_per_chunk]

            for item in sort:
                # which is x part of
                x = count + int(flat.index(item)/window_length)
                # how far along the frequency spectrum it is
                y = flat.index(item) % window_length
                max_idx.append((x * ms_per_chunk, sgram[0][0][y]))
            count += n_windows
        print(len(max_idx), "items, first from first 10 are", max_idx[:350:points_per_chunk])
        return max_idx



if __name__ == '__main__':


    fe = featureExtractor(filename=sys.argv[1])
    fe.open_stream()
    fe.print_wav_stats()
    fe.generate_spectrogram()

    #fe.get_fft()

    #audio = fe.get_audio_data()
    #sample_rate = fe.wf.getframerate()
    #frequencies = fe.get_frequencies(audio, len(audio), sample_rate)

    #plt.plot(*frequencies)
    #plt.show()
    #fe.play()

    # TODO: consider integrating pydub
