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
IDX_FREQ_J = 1

DEFAULT_FREQ = 44100

######################################################################
# Size of the FFT window, affects frequency granularity
# Experimented with 1024 mostly
# TODO: check effects for different values
DEFAULT_WINDOW_SIZE = 4096

DEFAULT_OVERLAP_RATION = 0.5

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

