# Based on Will Drevo's DejaVu

import fingerprint
from audioHelper import AudioHelper
import audioHelper as hlp
import sys
import os
import time

def fingerprint_worker(filename, limit=None, song_name=None):
    st = time.time()
    song_name, extension = os.path.splitext(filename)
    print('Fingerprinting ', song_name, ' with extension', extension)

    frame_rate, channels = hlp.retrieve_audio_data(filename)
    result = set()

    for channel_amount, channel in enumerate(channels):
        hashes = fingerprint.fingerprint(channel, frame_rate=frame_rate)

        result |= set(hashes)

    ft = time.time() - st
    print('Elapsed time is: ', ft)
    return song_name, result

x, y = fingerprint_worker(sys.argv[1])

print('song name: ', x)
print('Number of generated hashes: ',len(y))
for i in y:
    print('\rHash value - time index: {}'.format(i), end='')

