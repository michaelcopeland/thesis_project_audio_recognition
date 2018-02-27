# Based on Will Drevo's DejaVu

import fingerprint
from audioHelper import AudioHelper
import audioHelper as hlp
import sys
import os

def fingerprint_worker(filename, limit=None, song_name=None):
    song_name, extension = os.path.splitext(filename)
    print('Fingerprinting ', song_name, ' with extension', extension)

    frame_rate, channels = hlp.retrieve_audio_data(filename)

    result = set()

    for channel_amount, channel in enumerate(channels):
        hashes = fingerprint.fingerprint(channel, frame_rate=frame_rate)

        result |= set(hashes)

    return song_name, result

x, y = fingerprint_worker(sys.argv[1])

print('song name: ', x)
print(len(y))
