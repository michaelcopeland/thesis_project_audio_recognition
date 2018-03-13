# Based on Will Drevo's DejaVu

from fingerprint import Fingerprint
import database as db
import audioHelper as hlp
import os
import time

import matplotlib.pyplot as plt
import numpy as np

fgp_api = Fingerprint()
song_features = dict()

def fingerprint_worker(filename, limit=None, song_name=None):
    st = time.time()
    song_name, extension = os.path.splitext(filename)
    print('Fingerprinting: ', song_name, '\nFile extension: ', extension)

    frame_rate, channels = hlp.retrieve_audio_data(filename, limit)
    result = set()

    for channel_amount, channel in enumerate(channels):
        hashes = fgp_api.fingerprint(channel, frame_rate=frame_rate)

        result |= set(hashes)

    ft = time.time() - st
    print('Elapsed fingerprinting time: ', ft)
    return song_name, result

def reset_database():
    """drops all tables and recreates the db"""
    db.connect()
    db.drop_all_tables()
    db.setup()

def insert_wav_to_db(song_n):
    db.connect()
    song_name, list_hash = fingerprint_worker(song_n, limit=None)

    print('song name: ', song_name)
    print('Number of generated hashes: ', len(list_hash))

    db.insert_song(song_name, 1)

    for h in list_hash:
        db.insert_fingerprint(h[0], song_name, h[1])

song_1 = 'wavs/estring2.wav'
#song_2 = 'wavs/estring.wav'

song_name_1, lh1 = fingerprint_worker(song_1, limit=None)
peaks = fgp_api.get_unfiltered_data()
#song_features[song_name_1] = peaks

#song_name_2, lh2 = fingerprint_worker(song_2, limit=None)
#peaks = fgp_api.get_unfiltered_data()
#song_features[song_name_1] = peaks

#print(song_features.keys())

peaks_filtered = [x for x in peaks if x[2] > 20]

freq_idx = [x[0] for x in peaks_filtered]
time_idx = [x[1] for x in peaks_filtered]
print(freq_idx)
print(time_idx)
y = freq_idx
x = range(len(time_idx))
plt.bar(x, y, 1/1.5, color='green')
plt.show()


#for f, t, amps in peaks:
#    print('Freq: {}, Time: {}, Amp: {}'.format(f,t,amps))

"""
print('Number of hashes generated=', len(list_hash))
x = db.get_matches(list_hash)
c = 0
for i in x:
    c+=1
    #print(i)
print('matched hashes=', c)
"""