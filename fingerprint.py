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
# Experimented with 1024, 2048 and mostly 4096
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

PEAK_SORT = True

######################################################################
# Number of bits to throw away from the front of the SHA1 hash in the
# fingerprint calculation. The more you throw away, the less storage, but
# potentially higher collisions and misclassifications when identifying songs.
FINGERPRINT_REDUCTION = 20

# TODO: generate a grid example later on
######################################################################
# Time and Frequency intervals and tolerances for the grid-hash
# The interval values refer to the grid step on the time and frequency axes
# The tolerance values refer to the area within the grid where a peak must be
# in order for it be hashed.
# If the peak is outside this grid area it will be discarded

TIME_INTERVAL = 50
FREQ_INTERVAL = 50

TIME_TOLERANCE = 20
FREQ_TOLERANCE = 20


class Fingerprint:

    def __init__(self):
        self.amps = None
        self.freq = None
        self.time = None

    def set_data(self, freq, time, amps):
        self.freq = freq
        self.time = time
        self.amps = amps

    def get_unfiltered_data(self):
        peaks = zip(self.freq, self.time, self.amps)
        return list(peaks)

    def fingerprint(self, channel_samples,
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
        local_maxima = self.get_2D_peaks(arr2D, plot=True, min_amp=min_amp)
        local_maxima = np.array(local_maxima)

        # return hashes
        return self.generate_hashes(local_maxima, fan_value=fan_val)

    def get_2D_peaks(self, arr2D, plot=False, store_data=False, min_amp=DEFAULT_MIN_AMP):
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
        j, i = np.where(detected_peaks)  # time, frequency

        # filter peaks
        amps = amps.flatten()

        # stores information in a dictionary // used by audio similarity
        if store_data:
            self.set_data(i, j, amps)

        peaks = zip(i, j, amps)  # freq, time, amp

        # only consider peaks above a specific amplitude
        # TODO: remove this before minhash approach
        peaks_filtered = [x for x in peaks if x[2] > min_amp]

        # get idx for freq and time
        freq_idx = [x[0] for x in peaks_filtered]
        time_idx = [x[1] for x in peaks_filtered]
        # frequency = [x[2] for x in peaks_filtered]
        print('FINGERPRINTER DETAILS ***********')
        print('Number of peaks: ', len(freq_idx))
        print('Number of time idx: ', len(time_idx))
        print('Length of segment: ',
              round(len(arr2D[1]) / DEFAULT_FREQ * DEFAULT_WINDOW_SIZE * DEFAULT_OVERLAP_RATIO, 5), 'seconds')

        if plot:
            print('Plotting spectrogram!')
            fig, ax = plt.subplots()
            ax.imshow(arr2D, cmap='gnuplot')
            ax.scatter(freq_idx, time_idx)
            ax.set_xlabel('Time')
            ax.set_ylabel('Frequency')
            ax.set_title('Spectrogram')
            ax.set_aspect('auto', adjustable='box')
            plt.gca().invert_yaxis()
            plt.show()
            plt.close()

            print('Plotting peaks!')
            plt.scatter(freq_idx, time_idx)
            plt.grid(True)
            plt.show()
        # python 2 would cast to a list when using zip, py3 does not
        return list(zip(freq_idx, time_idx))

    def _localize_coord(self, f, t):
        """
        Find the point within the grid toward which a coordinate will hash.

        Attributes:
            f, t - tuple of frequency and time
        Return:
             - tuple of frequency and time
             - 'invalid' if tuple is not within target zone
        """
        _relative_f_idx = f % FREQ_INTERVAL
        _relative_t_idx = t % TIME_INTERVAL

        # find position on the grid
        if f < FREQ_INTERVAL:
            lb_f = 0
        else:
            lb_f = f - _relative_f_idx
        ub_f = lb_f + FREQ_INTERVAL

        if t < TIME_INTERVAL:
            lb_t = 0
        else:
            lb_t = t - _relative_t_idx
        ub_t = lb_t + TIME_INTERVAL

        # ensure time coordinates are within grid tolerance
        valid_lt = t <= lb_t + TIME_TOLERANCE
        valid_ut = t >= ub_t - TIME_TOLERANCE
        # ensure frequency coordinates are within grid tolerance
        valid_lf = f <= lb_f + FREQ_TOLERANCE
        valid_uf = f >= ub_f - FREQ_TOLERANCE

        # what coordinate do we return
        if (valid_lt or valid_ut) and (valid_lf or valid_uf):
            # time coordinate
            if valid_lt and valid_ut:
                t_res = ub_t
            elif valid_lt:
                t_res = lb_t
            else:
                t_res = ub_t

            # frequency coordinate
            if valid_lt and valid_uf:
                f_res = ub_f
            elif valid_lf:
                f_res = lb_f
            else:
                f_res = ub_f

            return f_res, t_res
        return 'invalid', 'invalid'

    def grid_filter_peaks(self, peaks, plot=False):
        """
        Filters the peaks.

        Attributes:
            peaks - a zip of frequency and time points
        Return:
             a filtered list of frequency and time points
        """
        freq_coords = []
        time_coords = []

        for i in range(len(peaks)):
            f, t = self._localize_coord(peaks[i][IDX_FREQ_I], peaks[i][IDX_TIME_J])
            if type(f) and type(t) is not str:
                freq_coords.append(f)
                time_coords.append(t)
        print('Length of peak lists={} -freq {} -time'.format(len(freq_coords), len(time_coords)))

        if plot:
            print('Plotting grid!')
            print('\nTime interval= {}\nTime tolerance= {}\nFreq interval= {}\nFreq tolerance= {}'.format(
                TIME_INTERVAL,
                TIME_TOLERANCE,
                FREQ_INTERVAL,
                FREQ_TOLERANCE))

            plt.rc('grid', linestyle='-', color='black')
            plt.scatter(freq_coords, time_coords)
            plt.grid(True)
            plt.show()
        # print('freq coords: {}\ntime coords: {}'.format(freq_coords, time_coords))

            # TODO: if invalid, delete from zip

    def generate_hashes(self, peaks, fan_value=DEFAULT_FAN_VALUE):
        #self.grid_filter_peaks(peaks)
        if PEAK_SORT:
            # sorting peaks by frequency
            sorted(peaks, key=itemgetter(0))

        for i in range(len(peaks)):
            for j in range(1, fan_value):
                if (i + j) < len(peaks):

                    freq1 = peaks[i][IDX_FREQ_I]
                    freq2 = peaks[i + j][IDX_FREQ_I]

                    t1 = peaks[i][IDX_TIME_J]
                    t2 = peaks[i + j][IDX_TIME_J]

                    tdelta = t2 - t1

                    # print('freq1: {}, freq2: {}, t1: {}, t2: {}, tdelta: {}'.format(freq1, freq2, t1, t2, tdelta))

                    # min is 0, max is 200
                    if (tdelta >= MIN_HASH_TIME_DELTA) and (tdelta <= MAX_HASH_TIME_DELTA):
                        # string needs encoding for hashing to work
                        string_to_hash = '{}{}{}'.format(str(freq1), str(freq2), str(tdelta)).encode('utf-8')

                        h = hashlib.sha1(string_to_hash)
                        x = (h.hexdigest()[0:FINGERPRINT_REDUCTION], t1)

                        yield x
