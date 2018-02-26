import wave
import numpy as np
import pyaudio
from pydub import AudioSegment
from pydub.utils import audioop
import time
import sys
import matplotlib.pyplot as plt

class AudioHelper():
    """This class handles audio data of a 24-bit encoding"""

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

        aud_data = wave_form.readframes(num_frames)
        wave_form.close()
        array = self.wave_to_array(channels, sample_width, aud_data)

        return frame_rate, sample_width, array

    def wave_to_array(self, channels, sample_width, aud_data):
        """data must be the string containing the bytes from the wav file."""

        num_samples, remainder = divmod(len(aud_data), sample_width * channels)

        if remainder > 0:
            raise ValueError('The length of data is not a multiple of '
                             'sample_width * channels.')
        if sample_width > 4:
            raise ValueError("sample_width must not be greater than 4.")

        if sample_width == 3:
            a = np.empty((num_samples, channels, 4), dtype=np.uint8)
            raw_bytes = np.fromstring(aud_data, dtype=np.uint8)

            a[:, :, :sample_width] = raw_bytes.reshape(-1, channels, sample_width)
            a[:, :, sample_width:] = (a[:, :, sample_width - 1:sample_width] >> 7) * 255
            result = a.view('<i4').reshape(a.shape[:-1])
        else:
            # 8 bit samples are stored as unsigned ints; others as signed ints.
            dt_char = 'u' if sample_width == 1 else 'i'
            a = np.fromstring(aud_data, dtype='<%s%d' % (dt_char, sample_width))
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

def retrieve_audio_data(filename, limit=None):
    """Retrieves audio information from an audio file.
    In case of a 24-bit file it uses AudioHelper(with wave)

    Returns:
        frame_rate - rate at which audio is being sampled in Hz
        channels   - the audio data of the song whether it is mono or stereo
    """
    try:
        audio_data = AudioSegment.from_file(filename)

        if limit:
            # the limit refers to a segment of audio, by default we want to retrieve the entire audio data
            audio_data = audio_data[:limit * 1000]

        # raw data is pydub's representation of the raw audio bytestring
        data = np.fromstring(audio_data.raw_data, dtype=np.int16)

        channels = []

        # accounting for mono / stereo
        for chn in range(audio_data.channels):
            channels.append(data[chn::audio_data.channels])

        frame_rate = audio_data.frame_rate
        if AudioSegment.converter == 'other':
            raise Exception('hack')

    # this does not work as intended
    # TODO: just convert all files to 16 or 32. Later
    except Exception:#audioop.error:
        print('Audio is 24-bit\nUsing wave')
        helper = AudioHelper(filename)
        frame_rate, sample_width, audio_data = helper.get_wav_audio_data(filename)
        audio_data = np.array(audio_data)

        if limit:
            audio_data = audio_data[:limit * 1000]

        audio_data = audio_data.T
        audio_data = audio_data.astype(np.int16)
        print('shape', audio_data.shape)

        channels = []
        for chn in audio_data:
            channels.append(chn)

    return frame_rate, channels


# testing main
if __name__ == '__main__':
    # TODO: 24-bit could be an issue with pydub. Check for solutions with wave
    file = sys.argv[1]
    #helper = AudioHelper(file)
    #fs, _, data = helper.get_wav_audio_data(file)

    fs, data = retrieve_audio_data(file)
    plt.plot(*data)
    plt.show()

    print('frame rate {}'.format(fs), 'data {}'.format(data[int(len(data)/4):len(data)]))
    print('\n')

