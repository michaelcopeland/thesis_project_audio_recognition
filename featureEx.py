import sys
import wave
import pyaudio
import numpy as np
import time


class featureExtractor():
    """Retrieves features from audio files"""

    def __init__(self, frequency=0, duration=0, wav_file="No file input"):
        self.frequency = frequency  # for later
        self.duration = duration  # for later
        self.wav_file = wav_file

    def open_stream(self):
        if (len(sys.argv) < 2):
            print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
            sys.exit(-1)

        print('Playing {0}'.format(self.wav_file))
        wav_file = self.wav_file
        self.wf = wave.open(wav_file, 'rb')
        self.p = pyaudio.PyAudio()

        # pyaudio config defaults
        self.FORMAT = self.p.get_format_from_width(self.wf.getsampwidth())
        self.CHANNELS = self.wf.getnchannels()
        self.RATE = self.wf.getframerate() # changes the pitch
        self.CHUNK = 1024

        # pyaudio config custom
        self.set_stream_config(False, 8, 1, 44100)

        self.stream = self.p.open(
            format           =self.FORMAT,
            channels         =self.CHANNELS,
            rate             =self.RATE,
            output           =True,
            frames_per_buffer=self.CHUNK
        )

    def play(self):
        print('play!')
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

    def get_wav_stats(self):
        print('Format from width: {}'
              '\nNumber of channels: {}'
              '\nRate: {}'
              '\nChunk size: {}'.format(self.FORMAT, self.CHANNELS, self.RATE, self.stream._frames_per_buffer))

    def set_stream_config(self, update=False, format=8, channels=1, rate=44100):
        """sets custom values for the audio being played
        Modifies pyaudio constructor parameters

        Attributes:
            update             - whether the parameters will be updated or not
            format             - audio format allowed by pyAudio
                                 (32 bit int / float, 24 bit int, 16 bit int, 8 bit int, 8 bit unsigned int)

            channels           - mono / stereo

            rate               - rate at which the song is playing, basically pitch
                               - increase to raise pitch and shorten time of song
        """
        if update:
            self.FORMAT   = format
            self.CHANNELS = channels
            self.RATE     = rate
        pass


if __name__ == '__main__':
    featureExtractor = featureExtractor(wav_file=sys.argv[1])
    featureExtractor.open_stream()

    featureExtractor.get_wav_stats()
    featureExtractor.play()
