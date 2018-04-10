# Based on Will Drevo's DejaVu

from fingerprint import Fingerprint
import fingerprint as fgp
import database as db
import audioHelper as hlp
import os
import time
import math

fgp_api = Fingerprint()
INVALID_EXT = ['pdf', 'txt', 'jpg', 'wav.alt', 'csv', 'xlsx', 'alt']
VALID_EXT   = ['.wav', 'ogg', 'mp3', 'flac']

def has_valid_extension(path_to_file):
    path, ext = os.path.splitext(path_to_file)
    if ext in VALID_EXT:
        return True
    return False

def retrieve_unfiltered_peaks(filename, limit=None):
    print('Retrieving peaks for ', filename)
    channel_amount, frame_rate, channels = hlp.retrieve_audio(filename, limit)

    for channel_amount, channel in enumerate(channels):
        _ = fgp_api.fingerprint(channel, frame_rate=frame_rate)

    peaks = fgp_api.get_unfiltered_data()
    return peaks

def fingerprint_worker(filename, limit=None, grid_only=False):
    #st = time.time()
    song_name, extension = os.path.splitext(filename)
    #print('Fingerprinting: ', song_name, '\nFile extension: ', extension)

    num_channels, frame_rate, audio_data = hlp.retrieve_audio(filename, limit)
    #print('from fingerprint worker\n frame rate {}, data {}'.format(frame_rate, channels))
    result = set()

    for num_channels, channel in enumerate(audio_data):
        hashes = fgp_api.fingerprint(channel, frame_rate=frame_rate)

        if grid_only:
            grid_points = fgp_api.fingerprint(channel, frame_rate=frame_rate, grid_only=grid_only)
            return grid_points

        result |= set(hashes)

    #ft = time.time() - st
    #print('Elapsed fingerprinting time: ', ft)
    return song_name, result

def reset_database():
    """drops all tables and recreates the db"""
    db.connect()
    db.drop_all_tables()
    db.setup()

def insert_wav_to_db(song_n):
    #db.connect()
    song_name, list_hash = fingerprint_worker(song_n, limit=None)

    print('Song name: ', song_name)
    print('Number of generated hashes: ', len(list_hash))

    db.insert_song(song_name, 1)

    for h in list_hash:
        db.insert_fingerprint(h[0], song_name, h[1])


def align_matches(list_matches, family=False):
    """picks the most likely correct song by doing a frequency count over the results"""
    diff_counter = dict()
    max_t_delta = 0
    largest_count = 0
    song_name = ''

    for _tuple in list_matches:
        # song name and time delta from the list of hashes
        s_n, t_delta = _tuple

        if t_delta not in diff_counter:
            diff_counter[t_delta] = dict()
        if s_n not in diff_counter[t_delta]:
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
    elif song_name == 'track_not_fingerprinted':
        pass
    else:
        # returns 'no_track'
        song_name = name

    # information of returned song
    nseconds = round(float(max_t_delta) /
                     fgp.DEFAULT_FREQ * fgp.DEFAULT_WINDOW_SIZE * fgp.DEFAULT_OVERLAP_RATIO, 5)

    # TODO: perhaps include the file path
    song = {
        'song id': id,
        'song name': song_name,
        'frequency in db': largest_count,
        'time delta': int(max_t_delta),
        'is fingerprinted': int(is_fng),
        'time (sec)': nseconds
    }
    if family:
        return song, diff_counter

    return song


def align_matches_weighted(list_matches):
    candidates = dict()

    for tup in list_matches:
        track_name, time_delta = tup

        if time_delta not in candidates:
            candidates[time_delta] = dict()
        if track_name not in candidates[time_delta]:
            candidates[time_delta][track_name] = 1
        else:
            candidates[time_delta][track_name] += 1

    weighted_candidates = []
    # each candidate is a tuple of (weight, (k,v))
    # default weight = 1
    # formula    = ((e ^ -(|time_delta|)) / number of candidates of that key)
    # formula alt= ((e ^ -(time_delta ^ 2)) / number of candidates of that key) - use this for stronger filtering
    for k, v in candidates.items():
        cands_per_key = len(v.values())
        cand_weight = float(math.e ** (-abs(k))) * 1000
        cand_weight = cand_weight / cands_per_key
        cand_tup = (cand_weight, k, v)

        weighted_candidates.append(cand_tup)

    weighted_candidates = sorted(weighted_candidates, key=lambda weight: weight[0])
    res = [x for x in weighted_candidates if x[0] > 0.0]

    if len(res) == 0:
        return {'song id': 0,
        'song name': 'no_track',
        'is fingerprinted': 0}, candidates

    prime_candidate = res[-1]
    max_count = 0
    query_track = ''

    for k, v in prime_candidate[2].items():
        if v > max_count:
            max_count = v
            query_track = k

    query_hit, id, name, is_fng = db.get_song_by_name(query_track)

    if query_hit:
        ret_name = name
    elif name == 'track_not_fingerprinted':
        ret_name = 'track_not_fingerprinted'
    else:
        # returns 'no_track' in case no query hit
        ret_name = name

    track = {
        'song id': id,
        'song name': ret_name,
        'is fingerprinted': int(is_fng),
    }
    return track, res


def files_in_dir(dir_path):
    """Returns all stored wavs"""
    files = []

    for (dirpath, dirname, filenames) in os.walk(dir_path):
        files.append([dirpath, filenames])
    return files


#### bulk add ####
def fingerprint_songs(reset_db=False, song_limit=None):
    f = files_in_dir('C:\\Users\\Vlad\Documents\\thesis\\audioExtraction\\wavs')

    if reset_db:
        reset_database()

    # get fingerprinted files
    number_fgp, already_fingerprinted = get_wavs_by_fgp(1)
    #print(already_fingerprinted)
    #print('Number of fingerprints=', number_fgp)

    song_counter = 0

    # go through each directory
    for tup in f:
        current_dir = tup[0]
        file_in_cd = tup[1]

        # go through each file in the directory
        for file in file_in_cd:
            # don't re-fingerprint files
            if file in already_fingerprinted:
                print('Skipping: {}'.format(file))
                continue

            if song_counter == song_limit:
                print('Added {} tracks to database.'.format(song_counter))
                db.connection.close()
                return

            path = current_dir + '\\' + file

            # avoid invalid extensions
            ext = file.split(".")[-1].lower()
            if ext in INVALID_EXT:
                continue

            # insert song returns true if it managed, false otherwise
            res = db.insert_song(file, 1)
            if res:
                song_counter += 1

                # generate and insert hashes
                _, list_hashes = fingerprint_worker(path)
                for h in list_hashes:
                    db.insert_fingerprint(h[0], file, h[1])
            else:
                print('Fingerprinting skipped')
                continue

    print('Number of wavs: ', song_counter)


def get_wavs_by_fgp(is_fgp=0):
    res = list(db.get_songs_by_fgp_status(is_fgp))

    clean_list = []
    for elem in res:
        temp = str(elem)[2:-3]
        clean_list.append(temp)
    print(clean_list)

    number_of_tracks = len(clean_list)
    return number_of_tracks, clean_list


def clean_not_fgp():
    # remove fingerprints + songs marked as not fingerprinted
    #not_fingerprinted = get_wavs_by_fgp(0)
    last_fingerprinted = ['DAYTIME, JUNCTION WITH BUSY TRAFFIC, CARS, MOTORBIKES, TRUCKS, HORNING, PEOPLE ON THE STREET, BIG CITY LIFE, BOMBAY, MUMBAI_INCREDIBLE_INDIA_VOL_II_14.WAV']
    db.delete_fgp_by_song(last_fingerprinted)
    db.delete_songs(last_fingerprinted)


if __name__ == '__main__':

    test1 = 'C:\\Users\\Vlad\\Documents\\thesis\\audioExtraction\\wavs\\Sonniss.com - GDC 2017 - Game Audio Bundle\\Chris Skyes - The Black Sea\\SFX Medium Wave Splash on Rocks 12.wav'
    sn, list_hash = fingerprint_worker('wavs/estring.wav',
                                       limit=2)

    matches = db.get_matches(list_hash)

    x, r = align_matches_weighted(matches)
    print(x)
    print(r)
    for _ in r:
        print(_)