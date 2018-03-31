import fingerprintWorker as fw

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
def exp_1(song, limit=None):
    all_files = fw.files_in_dir('C:\\Users\\Vlad\Documents\\thesis\\audioExtraction\\wavs')

    directory = ''
    files_in_dir = []
    result_track = ''

    for tup in all_files:
        directory = tup[0]
        files_in_dir = tup[1]

        for track in files_in_dir:
            if track == song:
                sn, list_hash = fw.fingerprint_worker(directory + '\\' + track, limit=limit)

                matches = fw.db.get_matches(list_hash)

                result_track = fw.align_matches(matches)

    print('Querying {} --- {} s\nResult={}'.format(song, limit, result_track))

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

limit = 8
# test_track = 'rain_umbrella_001_wide.wav'
# exp_1(test_track, limit)

for track in tracks_for_exp_1:
    exp_1(track, limit)
