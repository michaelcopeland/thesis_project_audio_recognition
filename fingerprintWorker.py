# Based on Will Drevo's DejaVu

from fingerprint import Fingerprint
import fingerprint as fgp
import database as db
import audioHelper as hlp
import os
import time

fgp_api = Fingerprint()
invalid_ext = ['pdf', 'txt', 'jpg', 'wav.alt', 'csv', 'xlsx', 'alt']

def retrieve_unfiltered_peaks(filename, limit=None):
    print('Retrieving peaks for ', filename)
    channel_amount, frame_rate, channels = hlp.retrieve_audio(filename, limit)

    for channel_amount, channel in enumerate(channels):
        _ = fgp_api.fingerprint(channel, frame_rate=frame_rate)

    peaks = fgp_api.get_unfiltered_data()
    return peaks

def fingerprint_worker(filename, limit=None):
    st = time.time()
    song_name, extension = os.path.splitext(filename)
    print('Fingerprinting: ', song_name, '\nFile extension: ', extension)

    num_channels, frame_rate, audio_data = hlp.retrieve_audio(filename, limit)
    #print('from fingerprint worker\n frame rate {}, data {}'.format(frame_rate, channels))
    result = set()

    for num_channels, channel in enumerate(audio_data):
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

    print('Song name: ', song_name)
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

def files_in_dir(dir_path):
    """Returns all stored wavs"""
    files = []

    for (dirpath, dirname, filenames) in os.walk(dir_path):
        files.append([dirpath, filenames])
    return files

#### experiment 1 ####
# add all wavs to db

f = files_in_dir('C:\\Users\\Vlad\Documents\\thesis\\audioExtraction\\wavs')
reset_database()

track_counter = 0

# go through each directory
for tup in f:
    current_dir = tup[0]
    file_in_cd = tup[1]

    # go through each file in the directory
    for file in file_in_cd:
        path = current_dir + '\\' + file

        # avoid invalid extensions
        ext = file.split(".")[-1].lower()
        if ext in invalid_ext:
            continue
        db.insert_song(file, 1)
        _, list_hashes = fingerprint_worker(path)
        for h in list_hashes:
            db.insert_fingerprint(h[0], file, h[1])

print('Number of wavs: ', track_counter)

    #directory, f_name = tup
    #print('{}\n{}'.format())

# song_name, list_hash = fingerprint_worker('wavs/river1.wav', limit=4)

