# Based on Will Drevo's DejaVu

from fingerprint import Fingerprint
import database as db
import audioHelper as hlp
import os
import time

fgp_api = Fingerprint()

def retrieve_unfiltered_peaks(filename, limit=None):
    print('Retrieving peaks for ', filename)
    frame_rate, channels = hlp.retrieve_audio_data(filename, limit)

    for channel_amount, channel in enumerate(channels):
        _ = fgp_api.fingerprint(channel, frame_rate=frame_rate)

    peaks = fgp_api.get_unfiltered_data()
    return peaks

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

# TODO: add match alignment

fingerprint_worker('wavs/c1.wav')
