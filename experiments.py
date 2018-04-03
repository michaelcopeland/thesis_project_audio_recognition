import fingerprintWorker as fw
import json

RESULT_DICT = {
    'TP': 0,
    'TN': 0,
    'FP': 0,
    'FN': 0,
    'FA': 0 # false accept
}


def reset_result_dict():
    for key in RESULT_DICT.keys():
        RESULT_DICT[key] = 0

##### Database query: 10 songs fingerprinted / 10 songs queried #####
# Songs:
# 01.wav
# aic.wav
# birds_outside_002_wide.wav
# busy_dining_room_002.wav
# madrid_food_market_busy_001.wav
# rain_umbrella_001_wide.wav
# 50s_elevator_ride_down_001.wav
# elevator_mechanism_002_wide.wav
# elevator_mechanism_005_wide.wav
# soviet_elevator_door_close_001.wav
def exp(song, limit=None):
    """Runs a query experiment

    Attributes:
        song  - tuple [0, song] or [1, song]; 0,1 = is_fingerprinted
        limit - how much of the song are we listening to

    Return:
        Dictionary of results
    """
    all_files = fw.files_in_dir('C:\\Users\\Vlad\Documents\\thesis\\audioExtraction\\wavs')

    song_in_fgp_statu = song[0]
    song_in        = song[1]

    # directory = ''
    # files_in_dir = []
    result_track = ''

    for tup in all_files:
        directory = tup[0]
        files_in_dir = tup[1]

        for track in files_in_dir:
            # ensure we get the wrong song
            if track == song_in:
                sn, list_hash = fw.fingerprint_worker(directory + '\\' + track, limit=limit)

                matches = fw.db.get_matches(list_hash)

                result_track = fw.align_matches(matches)

                # result track name
                r_t_name = result_track['song name']

                # TP
                if r_t_name == song_in:
                    RESULT_DICT['TP'] += 1
                # TN
                elif r_t_name == 'no_track' and song_in_fgp_statu == 0:
                    RESULT_DICT['TN'] += 1
                # FP
                elif r_t_name != song_in and song_in_fgp_statu == 1:
                    RESULT_DICT['FP'] += 1
                # FN
                elif r_t_name == 'no_track' and song_in_fgp_statu == 1:
                    RESULT_DICT['FN'] += 1
                # FA
                elif r_t_name != song_in and song_in_fgp_statu == 0:
                    RESULT_DICT['FA'] += 1

    print('Querying {} --- {} s\nResult={}'.format(song_in, limit, result_track))
    return RESULT_DICT


tracks_for_exp_1 = ['01.wav',
                    'aic.wav',
                    'birds_outside_002_wide.wav',
                    'busy_dining_room_002.wav',
                    'madrid_food_market_busy_001.wav',
                    'rain_umbrella_001_wide.wav',
                    '50s_elevator_ride_down_001.wav',
                    'elevator_mechanism_002_wide.wav',
                    'elevator_mechanism_005_wide.wav',
                    'soviet_elevator_door_close_001.wav']

# REMEMEBER: send in the song's fingerprint status (0, 1) as a tuple (status, song)

def run_exp1():
    limits = [1, 2, 4, 8]
    # test_track = 'rain_umbrella_001_wide.wav'
    # exp_1(test_track, limit)

    for track in tracks_for_exp_1:
        for l in limits:
            track = [1, track]
            exp(track, l)

# REMEMEBER: send in the song's fingerprint status (0, 1) as a tuple (status, song)
def run_exp2():
    limits = [1, 2, 4, 8]

    #get all fingerprinted songs
    num_tracks, track = fw.get_wavs_by_fgp(1)

    result = None
    for l in limits:

        # reset the result dictionary for different limits
        reset_result_dict()
        for t in track:
            t = [1, t]
            result = exp(t, l)
        print('Limit: {} s'.format(l))
        print(result)


def exp_aligned_matches():
    song_path = 'C:\\Users\\Vlad\Documents\\thesis\\audioExtraction\\wavs\\Sonniss.com - GDC 2017 - Game Audio Bundle\\Chris Skyes - The Black Sea\\AMBIENCE Huge Waves 2m Away From Impact Point 1.wav'

    sn, list_hashes = fw.fingerprint_worker(song_path, limit=2)
    print('Querying: {}'.format(sn))

    matches = fw.db.get_matches(list_hashes)

    song, fam = fw.align_matches(matches, family=True)

    print('Most likely res = {}'.format(song))
    print('Candidates:\n')
    for k, v in fam.items():
        print('Key {} -- Value {}'.format(k, v))


if __name__ == '__main__':
    exp_aligned_matches()
