"""An alternative to audioHelper using SciPy.IO"""

from scipy.io import wavfile

def read_wave_file(filename):
    """Returns sample frequency and data from wave file.

    Attributes:
        filename - file path or filename, depending on the working directory

        Accepted formats:
    =====================  ===========  ===========  =============
         WAV format            Min          Max       NumPy dtype
    =====================  ===========  ===========  =============
    32-bit floating-point  -1.0         +1.0         float32
    32-bit PCM             -2147483648  +2147483647  int32
    16-bit PCM             -32768       +32767       int16
    8-bit PCM              0            255          uint8
    =====================  ===========  ===========  =============
    """
    freq, data = wavfile.read(filename=filename)
    return freq, data

