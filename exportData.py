import numpy as np
import fingerprint as f
import fingerprintWorker as fw

export_path = 'C:\\Users\\Vlad\\Documents\\thesis\\audioExtraction\\npArr'

def set_grid_attributes(t_int, f_int, t_tol, f_tol):
    """Set custom grid"""
    f.TIME_INTERVAL = t_int
    f.FREQ_INTERVAL = f_int

    f.TIME_TOLERANCE = t_tol
    f.FREQ_TOLERANCE = f_tol

def export(track):
    all_files = fw.files_in_dir('C:\\Users\\Vlad\Documents\\thesis\\audioExtraction\\wavs')
    res = None

    for tup in all_files:
        directory = tup[0]
        files_in_dir = tup[1]

        for t in files_in_dir:
            if t == track:
                res = fw.fingerprint_worker(directory + '\\' + track, grid_only=True)

                res = np.array(res)
                np.save(export_path + '\\' + track, res)
                #print(np.shape(res))

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

#export('birds_outside_002_wide.wav')
x = np.load('npArr/birds_outside_002_wide.wav.npy')
print(x)