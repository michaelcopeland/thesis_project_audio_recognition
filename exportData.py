import numpy as np
import fingerprint as f
import fingerprintWorker as fw

EXPORT_PATH = 'C:\\Users\\Vlad\\Documents\\thesis\\audioExtraction\\npArr'
AUDIO_FILES = fw.files_in_dir('C:\\Users\\Vlad\Documents\\thesis\\audioExtraction\\wavs')

def export(track):
    for tup in AUDIO_FILES:
        directory = tup[0]
        files_in_dir = tup[1]

        for t in files_in_dir:
            if t == track:
                res = fw.fingerprint_worker(directory + '\\' + track, grid_only=True)

                res = np.array(res)
                np.save(EXPORT_PATH + '\\' + track, res)
                print('Exported: {}'.format(track))
                return True


def export_peaks(peaks_to_export):
    pass

# amount, already_fingerprinted = fw.get_wavs_by_fgp(1)
# print('{} tracks already in database'.format(amount))
#
#
# export_counter = 0
# limit = 30
#
# for tr in already_fingerprinted:
#     if export_counter == limit:
#         print('Exported {} tracks'.format(export_counter))
#         break
#     if export(tr):
#         export_counter += 1

#export('birds_outside_002_wide.wav')
x = np.load('npArr/birds_outside_002_wide.wav.npy')
print(x)