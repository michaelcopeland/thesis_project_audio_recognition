import fingerprintWorker as fw
import matplotlib.pyplot as plt
import exportData as export
import audioSimilarity as sim

from matplotlib import pyplot as plt


RESULT_DICT = {
    'TP': 0,
    'TN': 0,
    'FP': 0,
    'FN': 0,
    'FA': 0, # false accept
    'FAM_HIT': 0
}
num_tracks, db_tracks = fw.get_wavs_by_fgp(1)
print('Welcome to the experiment script.\nNumber of unique database entries: {}'.format(num_tracks))

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

mp3_test_tracks = [
'01. Hells Bells.mp3',
'02. Shoot To Thrill.mp3',
'03. What Do You Do For Money Honey.mp3',
'05. Let Me Put My Love Into You.mp3',
'06. Back In Black.mp3',
'07. You Shook Me All Night Long.mp3',
'08. Have A Drink On Me.mp3',
'09. Shake A Leg.mp3',
'01. Hard As A Rock.mp3',
'02. Cover You In Oil.mp3',
'04. Givin The Dog A Bone.mp3',
'10. Rock And Roll Aint Noise Pollution.mp3',
]


def reset_result_dict():
    # safety print
    print(RESULT_DICT)
    for key in RESULT_DICT.keys():
        RESULT_DICT[key] = 0


def exp_for_sensitivity(track_list, dir_map, limit=None):
    for tr in track_list:
        directory = dir_map[tr]
        path = directory + '\\' + tr

        sn, list_hash = fw.fingerprint_worker(path, limit=limit)

        matches = fw.db.get_matches(list_hash)

        result_track, matched_fam, res = fw.align_matches_weighted(matches)

        # result track name
        r_t_name = result_track['song name']

        # check if song is in the DB
        db = False
        if tr in db_tracks:
            db = True

        # TP
        if r_t_name == tr and db:
            RESULT_DICT['TP'] += 1
        # TN
        elif r_t_name == 'No results found' and not db:
            RESULT_DICT['TN'] += 1
        # FN
        elif r_t_name == 'No results found' and db:
            RESULT_DICT['FN'] += 1
        # FP
        elif r_t_name != tr and db:
            RESULT_DICT['FP'] += 1
        # FA
        elif r_t_name != tr and not db:
            RESULT_DICT['FA'] += 1

        fam_hit = False
        for k, v in matched_fam.items():
            if tr in v:
                # print('hit! ', song, v)
                fam_hit = True
        if fam_hit:
            RESULT_DICT['FAM_HIT'] += 1

        print('Querying {} --- {} s\nResult={}'.format(tr, limit, result_track))
    return RESULT_DICT


def exp_with_weighted_align(song, limit=None):
    """Runs a query experiment

        Attributes:
            song - tuple (is_fgp, song name)

        Return:
            Dictionary of results
    """
    dir_map = export.build_dir_map(export.mpeg_root)

    song_in = song[1]

    if song_in in dir_map:
        directory = dir_map[song_in]
    else:
        print(song_in, ' missing')
        return

    sn, list_hash = fw.fingerprint_worker(directory + '\\' + song_in, limit=limit)

    matches = fw.db.get_matches(list_hash)

    result_track, matched_fam, res = fw.align_matches_weighted(matches)

    # result track name
    r_t_name = result_track['song name']

    # check if song is in the DB
    db = False
    if song_in in db_tracks:
        db = True

    # TP
    if r_t_name == song_in and db:
        RESULT_DICT['TP'] += 1
    # TN
    elif r_t_name == 'No results found' and not db:
        RESULT_DICT['TN'] += 1
    # FN
    elif r_t_name == 'No results found' and db:
        RESULT_DICT['FN'] += 1
    # FP
    elif r_t_name != song_in and db:
        RESULT_DICT['FP'] += 1
    # FA
    elif r_t_name != song_in and not db:
        RESULT_DICT['FA'] += 1

    fam_hit = False
    for k, v in matched_fam.items():
        if song_in in v:
            # print('hit! ', song, v)
            fam_hit = True
    if fam_hit:
        RESULT_DICT['FAM_HIT'] += 1

    print('Querying {} --- {} s\nResult={}'.format(song_in, limit, result_track))
    return RESULT_DICT


def run_sensitivity_test():
    limits = [1, 2, 4, 8]

    list_tracks, dir_map = generate_track_list('wav', db_set=40, hold_back_set=10)

    for lim in limits:
        reset_result_dict()
        result = exp_for_sensitivity(list_tracks, dir_map, limit=lim)

        print('Limit: {} s'.format(lim))
        print(result)

def run_exp4_align_weighted():
    limits = [1, 2, 4, 8]
    #limits = [4]
    #num_tracks, track = fw.get_wavs_by_fgp(1)

    result = None
    for l in limits:
        # reset the result dictionary for different limits
        reset_result_dict()
        counter = 0
        for t in db_tracks:
            if counter == 500:
                break
            counter += 1

            t = [1, t]
            result = exp_with_weighted_align(t, l)
        print('Limit: {} s'.format(l))
        print(result)


def generate_track_list(track_type, db_set=0, hold_back_set=0):
    """Generates a list of tracks containing a specified number of
    tracks from the database and specified number of tracks not present
    in the database.

    This is done for the purpose of specificity testing.

    Attributes:
        db_tracks - number of tracks we want from the database
        hold_back - number of tracks we want that are not in the database
        track_type - wav or mp3

    Return:
        res - a list of audio track titles
    """
    # counters for how many songs we've added for each set
    goal_db = 0
    goal_hold_back = 0
    res = []

    # get all available tracks
    if track_type == 'wav':
        dir_map = export.build_dir_map(export.wav_root)
    elif track_type == 'mp3':
        dir_map = export.build_dir_map(export.mpeg_root)
    else:
        print('Only wav or mp3 types accepted')
        return

    # get number of tracks and a list of tracks
    nt, all_tracks_from_db = fw.get_wavs_by_fgp(1)

    # create the list
    for tr in dir_map.keys():
        if tr in all_tracks_from_db and goal_db < db_set:
            res.append(tr)
            goal_db += 1
        if tr not in all_tracks_from_db and goal_hold_back < hold_back_set:
            res.append(tr)
            goal_hold_back += 1
        if goal_db == db_set and goal_hold_back == hold_back_set:
            print('done!')
            break
    return res, dir_map


def exp_aligned_matches():
    song_path = export.db_test + '\\' + 'c1.wav'

    sn, list_hashes = fw.fingerprint_worker(song_path, limit=4)
    print('Querying: {}'.format(sn))

    matches = fw.db.get_matches(list_hashes)

    song, fam_dict, cand = fw.align_matches_weighted(matches)

    print('Most likely res = {}\n'.format(song))
    sim.compute_sim(song['song name'], cand)


def test_list_hash_colision_rate(test_track, limit=None):
    name, list_hash = fw.fingerprint_worker(test_track, limit)
    return list_hash


def run_test_list_colision_rate():
    test_track = 'D:\\thesis-data\\c2.wav'
    _, list_hash_all = fw.fingerprint_worker(test_track)
    print('len=', len(list_hash_all))

    l_num_hash = []
    num_col_hash = []
    for l in range(0, 42):
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
    print('num hash',l_num_hash)
    print('num intersect', num_col_hash)
    return l_num_hash, num_col_hash

def test_all_answers(song_in):
    """Tests whether algorithm correctly returns TP, TN, FP, FN"""

    dir_map = export.build_dir_map(export.wav_root)

    if song_in in dir_map:
        directory = dir_map[song_in]
    else:
        print(song_in, ' missing')
        return

    sn, list_hash = fw.fingerprint_worker(directory + '\\' + song_in, limit=1)

    matches = fw.db.get_matches(list_hash)

    result_track, matched_fam, res = fw.align_matches_weighted(matches)
    for e in res:
        print(e)
    # result track name
    r_t_name = result_track['song name']
    print(r_t_name)

def gen_plot():

    points = [
        (0, 0),
        (10, 20),
        (37, 36),
        (23, 75),
        (35, 70),
        (20, 40),
        (60, 100),
    ]

    x = list(map(lambda x: x[0], points))
    y = list(map(lambda x: x[1], points))

    plt.title('Grid Example')
    plt.xlabel('Time intervals')
    plt.ylabel('Frequency intervals')

    plt.scatter(x, y)
    plt.grid(True)

    plt.show()


if __name__ == '__main__':
    gen_plot()
    #exp_aligned_matches()
    #run_exp4_align_weighted()
    #run_sensitivity_test()

