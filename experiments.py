import fingerprintWorker as fw
import matplotlib.pyplot as plt
import exportData as export

RESULT_DICT = {
    'TP': 0,
    'TN': 0,
    'FP': 0,
    'FN': 0,
    'FA': 0, # false accept
    'FAM_HIT': 0
}

test_tracks = ['01.wav',
               'aic.wav',
               'birds_outside_002_wide.wav',
               'busy_dining_room_002.wav',
               'madrid_food_market_busy_001.wav',
               'rain_umbrella_001_wide.wav',
               '50s_elevator_ride_down_001.wav',
               'elevator_mechanism_002_wide.wav',
               'elevator_mechanism_005_wide.wav',
               'soviet_elevator_door_close_001.wav']


def reset_result_dict():
    for key in RESULT_DICT.keys():
        RESULT_DICT[key] = 0


def exp(song, limit=None):
    """Runs a query experiment

    Attributes:
        song - tuple (is_fgp, song name)

    Return:
        Dictionary of results
    """
    dir_map = export.build_dir_map(export.root)

    song_in_fgp_status = song[0]
    song_in            = song[1]

    directory = dir_map[song_in]

    sn, list_hash = fw.fingerprint_worker(directory + '\\' + song_in, limit=limit)

    matches = fw.db.get_matches(list_hash)

    result_track, matched_fam = fw.align_matches(matches, family=True)

    # result track name
    r_t_name = result_track['song name']

    # TP
    if r_t_name == song_in:
        RESULT_DICT['TP'] += 1
    # TN
    elif r_t_name == 'no_track' and song_in_fgp_status == 0:
        RESULT_DICT['TN'] += 1
    # FP
    elif r_t_name != song_in and song_in_fgp_status == 1:
        RESULT_DICT['FP'] += 1
    # FN
    elif r_t_name == 'no_track' and song_in_fgp_status == 1:
        RESULT_DICT['FN'] += 1
    # FA
    elif r_t_name != song_in and song_in_fgp_status == 0:
        RESULT_DICT['FA'] += 1

    fam_hit = False
    for k, v in matched_fam.items():
        if song_in in v:
            #print('hit! ', song, v)
            fam_hit = True
    if fam_hit:
        RESULT_DICT['FAM_HIT'] += 1
    else:
        print('!!!!!!!!!!!!!\nSong in: {}\nValues: {}'.format(song_in, matched_fam.values()))

    print('Querying {} --- {} s\nResult={}'.format(song_in, limit, result_track))
    return RESULT_DICT


def exp_with_weighted_align(song, limit=None):
    dir_map = export.build_dir_map(export.root)

    song_in_fgp_status = song[0]
    song_in = song[1]
    directory = dir_map[song_in]

    sn, list_hash = fw.fingerprint_worker(directory + '\\' + song_in, limit=limit)

    matches = fw.db.get_matches(list_hash)

    result_track, matched_fam = fw.align_matches_weighted(matches)

    # result track name
    r_t_name = result_track['song name']

    # TP
    if r_t_name == song_in:
        RESULT_DICT['TP'] += 1
    # TN
    elif r_t_name == 'no_track' and song_in_fgp_status == 0:
        RESULT_DICT['TN'] += 1
    # FP
    elif r_t_name != song_in and song_in_fgp_status == 1:
        RESULT_DICT['FP'] += 1
    # FN
    elif r_t_name == 'no_track' and song_in_fgp_status == 1:
        RESULT_DICT['FN'] += 1
    # FA
    elif r_t_name != song_in and song_in_fgp_status == 0:
        RESULT_DICT['FA'] += 1

    fam_hit = False
    for k, v in matched_fam.items():
        if song_in in v:
            # print('hit! ', song, v)
            fam_hit = True
    if fam_hit:
        RESULT_DICT['FAM_HIT'] += 1
    else:
        print('!!!!!!!!!!!!!\nSong in: {}\nValues: {}'.format(song_in, matched_fam.values()))

    print('Querying {} --- {} s\nResult={}'.format(song_in, limit, result_track))
    return RESULT_DICT


# REMEMEBER: send in the song's fingerprint status (0, 1) as a tuple (status, song)
def run_exp1():
    limits = [1, 2, 4, 8]
    # test_track = 'rain_umbrella_001_wide.wav'
    # exp_1(test_track, limit)

    for track in test_tracks:
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

def run_exp3():
    """the point is to find if the correct song is the family of returned songs"""
    limits = [1, 2, 4, 8]

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


def run_exp4_align_weighted():
    limits = [1, 2, 4, 8]

    num_tracks, track = fw.get_wavs_by_fgp(1)

    result = None
    for l in limits:

        # reset the result dictionary for different limits
        reset_result_dict()
        for t in track:
            t = [1, t]
            result = exp_with_weighted_align(t, l)
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


def test_list_hash_colision_rate(test_track, limit=None):
    name, list_hash = fw.fingerprint_worker(test_track, limit)
    return list_hash


def run_test_list_colision_rate():
    test_track = 'C:\\Users\\Vlad\\Documents\\thesis\\audioExtraction\\wavs\\Sonniss.com - GDC 2017 - Game Audio Bundle\\Articulated Sounds - Quiet Streets\\QUIET STREET Back alley, people chatting, ST.wav'
    _, list_hash_all = fw.fingerprint_worker(test_track)

    l_num_hash = []
    num_col_hash = []
    for l in range(0, 132):
        print('limit= ', l)
        limited_list = test_list_hash_colision_rate(test_track, limit=l)

        num_hash = len(limited_list)
        intersect = len(limited_list.intersection(list_hash_all))
        l_num_hash.append(num_hash)
        num_col_hash.append(intersect)

        print('Num hash: {}'.format(num_hash))
        print('intersection=', intersect)

        plt.plot(l_num_hash, num_col_hash)
        plt.show()


if __name__ == '__main__':
    run_exp4_align_weighted()