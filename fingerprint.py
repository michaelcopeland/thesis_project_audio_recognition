# Based on Will Drevo's dejavu
#
# Author: Will Drevo
# URL: https://github.com/VladLimbean/dejavu/tree/master/dejavu

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (generate_binary_structure,
                                      iterate_structure, binary_erosion)
import hashlib
from operator import itemgetter

IDX_FREQ_I = 0
IDX_TIME_J = 1

DEFAULT_FREQ = 44100

######################################################################
# Size of the FFT window, affects frequency granularity
# Experimented with 1024 mostly
# TODO: check effects for different values
DEFAULT_WINDOW_SIZE = 4096

DEFAULT_OVERLAP_RATIO = 0.5

######################################################################
# Degree to which a fingerprint can be paired with its neighbors --
# higher will cause more fingerprints, but potentially better accuracy.
DEFAULT_FAN_VALUE = 15

DEFAULT_MIN_AMP = 10

PEAK_NEIGHBORHOOD_SIZE = 20

######################################################################
# Thresholds on how close or far fingerprints can be in time in order
# to be paired as a fingerprint. If your max is too low, higher values of
# DEFAULT_FAN_VALUE may not perform as expected.
MIN_HASH_TIME_DELTA = 0
MAX_HASH_TIME_DELTA = 200

PEAK_SORT = False

######################################################################
# Number of bits to throw away from the front of the SHA1 hash in the
# fingerprint calculation. The more you throw away, the less storage, but
# potentially higher collisions and misclassifications when identifying songs.
FINGERPRINT_REDUCTION = 20

def fingerprint(channel_samples,
                frame_rate=DEFAULT_FREQ,
                wsize=DEFAULT_WINDOW_SIZE,
                overlap_ratio=DEFAULT_OVERLAP_RATIO,
                fan_val=DEFAULT_FAN_VALUE,
                min_amp=DEFAULT_MIN_AMP):

    # FFT + conversion to spectral domain
    arr2D = mlab.specgram(channel_samples,
                          NFFT=wsize,
                          Fs=frame_rate,
                          window=mlab.window_hanning,
                          noverlap=int(wsize * overlap_ratio))[0]

    # log transform
    arr2D = 10 * np.log10(arr2D)
    arr2D[arr2D == -np.inf] = 0

    # find local maxima
    local_maxima = get_2D_peaks(arr2D, plot=False, min_amp=min_amp)
    local_maxima = np.array(local_maxima)

    # return hashes
    return generate_hashes(local_maxima, fan_value=fan_val)

def get_2D_peaks(arr2D, plot=False, min_amp=DEFAULT_MIN_AMP):
    struct = generate_binary_structure(2, 1)
    neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)

    # find local maxima
    localmax = maximum_filter(arr2D, footprint=neighborhood) == arr2D
    background = (arr2D == 0)
    eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)

    # boolean mask of 2d array with True peaks
    detected_peaks = localmax ^ eroded_background

    # extract peaks
    amps = arr2D[detected_peaks]
    j, i = np.where(detected_peaks)

    # filter peaks
    amps = amps.flatten()
    peaks = zip(i, j, amps) # time, freq, amp
    peaks_filtered = [x for x in peaks if x[2] > min_amp]

    # get idx for freq and time
    freq_idx = [x[1] for x in peaks_filtered]
    time_idx = [x[0] for x in peaks_filtered]

    if plot:
        print('Plotting!')
        fix, ax = plt.subplots()
        ax.imshow(arr2D)
        ax.scatter(time_idx, freq_idx)
        ax.set_xlabel('Time')
        ax.set_ylabel('Frequency')
        ax.set_title('Spectrogram')
        plt.gca().invert_yaxis()
        plt.show()
    # python 2 would cast to a list when using zip, py3 does not
    return list(zip(freq_idx, time_idx))

def generate_hashes(peaks, fan_value=DEFAULT_FAN_VALUE):
    if PEAK_SORT:
        peaks.sort(key=itemgetter(1))

    for i in range(len(peaks)):
        for j in range(1, fan_value):
            if (i+j) < len(peaks):

                freq1 = peaks[i][IDX_FREQ_I]
                freq2 = peaks[i+j][IDX_FREQ_I]

                t1 = peaks[i][IDX_TIME_J]
                t2 = peaks[i+j][IDX_TIME_J]

                tdelta = t2 - t1

                #print('freq1 - {}, freq2 - {}, t1 - {}, t2 - {}, tdelta - {}'.format(freq1, freq2, t1, t2, tdelta))

                # min is 0, max is 200
                if (tdelta >= MIN_HASH_TIME_DELTA) and (tdelta <= MIN_HASH_TIME_DELTA):
                    # string needs encoding for hashing to work
                    string_to_hash = '{}|{}|{}'.format(str(freq1), str(freq2), str(tdelta)).encode('utf-8')

                    h = hashlib.sha1(string_to_hash)
                    x = (h.hexdigest()[0:FINGERPRINT_REDUCTION], t1)

                    yield x

