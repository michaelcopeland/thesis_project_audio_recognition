import wave
import numpy as np
import pyaudio
import soundfile as sf
import time
import sys
import matplotlib.pyplot as plt

from pydub import AudioSegment


class AudioHelper:
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


def retrieve_audio(wave_file, limit=None):
    """Retrieves audio information from sound file using PySoundFile.

    Attributes:
        wave_file - path to the audio file (supports OGG, FLAC, MAT, wave, etc.)
        limit     - how many seconds to play from the audio

    Return:
        num_channels - number of channels of the audio file
        frame rate   - the rate of sample
        data         - numpy array of audio data
    """
    num_channels = 0
    frame_rate = 0
    audio_data = None

    try:
        current_wav = sf.SoundFile(wave_file)
        num_channels = current_wav.channels

        audio_data, frame_rate = sf.read(wave_file, dtype=np.int16)

        if limit:
            frame_count = limit * frame_rate

            if num_channels == 1:
                audio_data = audio_data[:frame_count]
            elif num_channels == 2:
                audio_data = audio_data[:frame_count]

        audio_data = audio_data.T
        audio_data = np.reshape(audio_data, (1, len(audio_data)))

        current_wav.close()
    except:
        pass
        print('Ensure ffmpeg is installed')

    if num_channels == 1:
        return num_channels, frame_rate, audio_data

    elif num_channels == 2:
        return num_channels, frame_rate, list(audio_data)


def retrieve_audio_mpeg(filename, limit=None):
    """Similar to retrieve_audio
    This method returns audio data for mp3 files"""
    frame_rate   = None
    channels     = []
    num_channels = 0

    try:
        audio_data = AudioSegment.from_file(filename)
        num_channels = audio_data.channels
        if limit:
            audio_data = audio_data[:limit * 1000]

        raw = np.fromstring(audio_data._data, np.int16)

        for chn in range(audio_data.channels):
            channels.append(raw[chn::audio_data.channels])

        frame_rate = audio_data.frame_rate
    except:
        print('could not read audio file, or path was wrong')

    return num_channels, frame_rate, channels

# testing main
if __name__ == '__main__':
    file = 'C:\\Users\\Vlad\\Documents\\thesis\\audioExtraction\\wavs\\Sonniss.com - GDC 2017 - Game Audio Bundle\\Creative Audio Pool - INCREDIBLE SOUNDS OF INDIA COLLECTION\\DAYTIME JUNCTION 14.wav'

    nc, f, data = retrieve_audio(file, limit=None)
    #fs, datas = retrieve_audio_data(file, limit=2)
    print(nc, ' ', f)

    print('f_rate=', f)

    #print(len(data), ' ', len(datas))
    print(np.shape(data))
    #print(np.shape(datas))

    print(data)
    #print(datas)



