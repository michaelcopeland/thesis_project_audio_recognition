import wave
import numpy as np
import pyaudio
import time
import sys

class AudioHelper():
    """This class handles audio data"""

    def __init__(self, filename):
        self.filename = filename

    def get_wav_audio_data(self, filename):
        """Reads audio data of a wave file

        :returns
            data         - audio data
            frame_rate   - rate of audio in Hz
            sample_width - width of sample

        """
        try:
            wave_form = wave.open(filename, 'r')
        except IOError:
            print(filename, ' could not be open')
            return

        frame_rate   = wave_form.getframerate()
        num_frames   = wave_form.getnframes()
        channels     = wave_form.getnchannels()
        sample_width = wave_form.getsampwidth()

        data = wave_form.readframes(num_frames)
        wave_form.close()
        array = self.wave_to_array(channels, sample_width, data)

        return frame_rate, sample_width, array

    def wave_to_array(self, channels, sample_width, data):
        """data must be the string containing the bytes from the wav file."""

        num_samples, remainder = divmod(len(data), sample_width * channels)

        if remainder > 0:
            raise ValueError('The length of data is not a multiple of '
                             'sample_width * channels.')
        if sample_width > 4:
            raise ValueError("sample_width must not be greater than 4.")

        if sample_width == 3:
            a = np.empty((num_samples, channels, 4), dtype=np.uint8)
            raw_bytes = np.fromstring(data, dtype=np.uint8)

            a[:, :, :sample_width] = raw_bytes.reshape(-1, channels, sample_width)
            a[:, :, sample_width:] = (a[:, :, sample_width - 1:sample_width] >> 7) * 255
            result = a.view('<i4').reshape(a.shape[:-1])
        else:
            # 8 bit samples are stored as unsigned ints; others as signed ints.
            dt_char = 'u' if sample_width == 1 else 'i'
            a = np.fromstring(data, dtype='<%s%d' % (dt_char, sample_width))
            result = a.reshape(-1, channels)

        return result

    def play_wav(self):
        """Plays wav file"""

        print('play!')
        self.p = pyaudio.PyAudio()
        wav    = wave.open(self.filename)
        print(wav.getparams())

        # pyaudio config defaults
        self.FORMAT   = self.p.get_format_from_width(wav.getsampwidth())
        self.CHANNELS = wav.getnchannels()
        self.RATE     = wav.getframerate()  # changes the pitch
        self.CHUNK    = 1024

        stream = self.p.open(
            format  =self.FORMAT,
            channels=self.CHANNELS,
            rate    =self.RATE,
            output  =True,
            frames_per_buffer=self.CHUNK
        )

        start_time = time.time()
        data = wav.readframes(self.CHUNK)
        while len(data) > 0:
            stream.write(data)
            data = wav.readframes(self.CHUNK)

        stop_time = time.time()
        print('Elapsed play time: {0:.5f} seconds'.format(stop_time - start_time))
        stream.stop_stream()
        stream.close()
        self.p.terminate()
        print('playback done')

# testing main
if __name__ == '__main__':
    file = sys.argv[1]
    helper = AudioHelper(filename=file)
    rate, ch, arr = helper.get_wav_audio_data(file)
    helper.play_wav()
    print('channels {}'.format(ch), ' samples {} '.format(rate))
    print('\n')

# TODO: check decoder.py make sure you can read any wav file