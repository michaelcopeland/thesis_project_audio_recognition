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
    print('Fingerprinting: ', song_name, '\nFile extension: ', extension)

    frame_rate, channels = hlp.retrieve_audio_data(filename, limit)
    result = set()
    #result2 = []

    for channel_amount, channel in enumerate(channels):
        hashes = fingerprint.fingerprint(channel, frame_rate=frame_rate)

        result |= set(hashes)
        #result2 = result2.extend(hashes)

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

#reset_database()
song = 'estring.wav'
song_name, list_hash = fingerprint_worker(song, limit=10)
print('Number of hashes generated=', len(list_hash))
x = db.get_matches(list_hash)
c = 0
for i in x:
    c+=1
    print(i)
print('matched hashes=', c)