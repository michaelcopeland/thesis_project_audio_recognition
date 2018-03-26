# Based on Will Drevo's DejaVu

from fingerprint import Fingerprint
import fingerprint as fgp
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

def align_matches(list_hash):
    """picks the most likely correct song by doing a frequency count over the results"""
    diff_counter = dict()
    max_t_delta = 0
    largest_count = 0
    song_name = ''

    for _tuple in list_hash:
        # song name and time delta from the list of hashes
        s_n, t_delta = _tuple

        if t_delta not in diff_counter:
            diff_counter[t_delta] = dict()
        if s_n not in diff_counter:
            diff_counter[t_delta][s_n] = 0
        diff_counter[t_delta][s_n] += 1

        # keep track of result with the largest frequency count
        if diff_counter[t_delta][s_n] > largest_count:
            max_t_delta = t_delta
            largest_count = diff_counter[max_t_delta][s_n]
            song_name = s_n

    # result from database
    query_hit, id, name, is_fng = db.get_song_by_name(song_name)

    if query_hit:
        song_name = name
    else:
        print('Queried for {}\nNo such song in the database'.format(song_name))
        return

    # information of returned song
    nseconds = round(float(max_t_delta) /
                     fgp.DEFAULT_FREQ * fgp.DEFAULT_WINDOW_SIZE * fgp.DEFAULT_OVERLAP_RATIO, 5)

    # TODO: perhaps include the file path
    song = {
        'song id': id,
        'song name': song_name,
        'frequency in db': largest_count,
        'time delta': int(max_t_delta),
        'time (sec)': nseconds
    }

    return song

fingerprint_worker('wavs/c1.wav')
