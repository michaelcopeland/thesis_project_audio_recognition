# Based on Will Drevo's DejaVu

import fingerprint
import database as db
import audioHelper as hlp
import sys
import os
import time

def fingerprint_worker(filename, limit=None, song_name=None):
    st = time.time()
    song_name, extension = os.path.splitext(filename)
    print('Fingerprinting ', song_name, ' with extension', extension)

    frame_rate, channels = hlp.retrieve_audio_data(filename, limit)
    result = set()

    for channel_amount, channel in enumerate(channels):
        hashes = fingerprint.fingerprint(channel, frame_rate=frame_rate)

        result |= set(hashes)

    ft = time.time() - st
    print('Elapsed time is: ', ft)
    return song_name, result

song = 'estring.wav'
song_name, list_hash = fingerprint_worker(song, limit=2)

print('song name: ', song_name)
print('Number of generated hashes: ', len(list_hash))

db.connect()

x = db.get_matches(list_hash)
for i in x:
    print(i)