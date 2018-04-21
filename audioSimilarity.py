"""Stores audio information and allows to compute various similarity searches"""

from datasketch import MinHash
import fingerprintWorker as fw

from scipy.signal import correlate2d, correlate
from scipy.stats import pearsonr, linregress
import exportData as export
import numpy as np
import matplotlib.pyplot as plt

class AudioSimilarity():
    def __init__(self):
        self.storedAudio = dict()

    def add_audio_data(self, wav_name, data):
        self.storedAudio[wav_name] = data

    def get_audio_data(self, wav_name):
        return self.storedAudio[wav_name]

    def get_xcorr(self, data1, data2):
        print(len(data1))
        #data1 = data1[25:100]

        norm = np.sum(data1 * data1)
        #data1 = [10, 20, 30, 40]
        #data2 = [20, 30, 40, 10]
        corr = correlate(data1, data2, mode='full') / norm

        res = np.argmax(corr)
        print('time lag of corr', res)

        plt.plot(corr)

        plt.grid(True)
        plt.axhline(0, color='black', lw=2)
        plt.title('1d correlation')
        plt.show()

    def get_xcorr_2d(self, ft1, ft2):
        corr = correlate2d(ft1, ft2, mode='full')

        plt.plot(*corr)
        plt.title('2d correlation')
        plt.show()

    def get_pearson_correlation(self, wav_file1, wav_file2):
        l1 = len(wav_file1)
        l2 = len(wav_file2)

        # ensure the files are the same length
        if l1 > l2:
            wav_file1 = wav_file1[:l2]
        else:
            wav_file2 = wav_file2[:l1]

        res = pearsonr(wav_file1, wav_file2)
        print('Pearson correlation: ', res)

    def get_correlated_coefficients(self, data1, data2):
        l1 = len(data1)
        l2 = len(data2)

        if l1 > l2:
            data1 = data1[:l2]
        else:
            data2 = data2[:l1]

        res = np.corrcoef(data1, data2)
        print('Correlated coefficients:\n', res)

    def get_linear_regression(self, f1, f2):
        f, ax = plt.subplots(2, sharex=True)

        ax[0].plot(f2)
        ax[1].plot(f1)

        plt.show()

        plt.close(f)

        l1 = len(f1)
        l2 = len(f2)

        if l1 > l2:
            f1 = f1[:l2]
        else:
            f2 = f2[:l1]

        slope, intercept, r_value, p_value, std_err = linregress(f1, f2)

        print('Linear regression:\n\nslope={}\nintercept={}\nr_val={}\np_val={}\nerr={}'.format(
            slope, intercept, r_value, p_value, std_err))

    def plot_waves(self, wav1, wav2):
        l1 = len(wav1)
        l2 = len(wav2)

        if l1 > l2:
            wav1 = wav1[:l2]
        else:
            wav2 = wav2[:l1]
        # print(np.shape(wav1))
        # print(np.shape(wav2))
        plt.plot(wav1, wav2, '--b', wav1, '--r', wav2, alpha=0.75)
        plt.show()


def minHash(set1, set2):
    m1, m2 = MinHash(), MinHash()

    for d in set1:
        m1.update(d.encode('utf8'))
    for d in set2:
        m2.update(d.encode('utf8'))

    sim = m1.jaccard(m2)
    #print("Estimated Jaccard: ", sim)

    #s1 = set(set1)
    #s2 = set(set2)
    #actual_jaccard = float(len(s1.intersection(s2))) / float(len(s1.union(s2)))
    #print("Actual Jaccard: ", actual_jaccard)

    return sim

def compute_sim(primary, candidates):
    """Calculates Jaccard similarity of different audio tracks
    It takes a primary track and minhashes it against other candidates

    Attributes:
        primary     - .grid file representing an audio track
        candidates  - a list of matching files

    Return:
        res         - a list of songs with above 75% similarity
    """
    all_grids = export.build_dir_map(export.EXPORT_PATH)
    prim_set = export.load_grid(primary)

    # grids_to_load = set()
    # for cand in candidates:
    #     tup = cand[2].keys()
    #
    #     for sub_cand in tup:
    #         grids_to_load.add(sub_cand)

    # for grd in grids_to_load:
    #     current = export.load_grid(grd)
    #     s = minHash(prim_set, current)
    #     if s > 0.75:
    #         print(primary, grd, s)
    for grd in all_grids.keys():
        current = export.load_grid(grd)
        s = minHash(prim_set, current)
        if s > 0.75:
            print(grd, primary, s)



def get_similarity(list_dir, grid_setup):
    """Receives a list of folders each containing audio files.
    Returns the similarity values per grid size for each folder.

    Attributes:
        list_dir   - a list of directories in which to look for songs
        grid_setup - a list of grid setup values ie (50, 50, 20, 20)
    """
    for stp in grid_setup:
        tint = stp[0]
        fint = stp[1]
        ttol = stp[2]
        ftol = stp[3]
        fw.fgp_api.set_grid_attributes(tint, fint, ttol, ftol)

        for dir in list_dir:
            paths = export._get_dir_structure('wavs')

            for tup in paths:
                directory_name = tup[0]
                files          = tup[1]

                if directory_name == dir:
                    primary_file = files[-1]
                    primary_set = fw.fingerprint_worker(dir + '\\' + primary_file, grid_only=True)

                    for _f in files:
                        if _f != primary_file:
                            secondary_set = fw.fingerprint_worker(dir + '\\' + _f, grid_only=True)

                            print('{} <> {}'.format(primary_file, _f))
                            minHash(primary_set, secondary_set)


if __name__=='__main__':
    compute_sim('08. Have A Drink On Me.grid', None)
    # list_paths=['wavs\\c',
    #             'wavs\\river',
    #             'wavs\\estring',
    #             'wavs\\Sonniss.com - GDC 2017 - Game Audio Bundle\\Alexander Ahura -  Groats Part1',
    #             'wavs\\Sonniss.com - GDC 2017 - Game Audio Bundle\\Bluezone Corporation - War Zone (Designed Explosions)',
    #             'wavs\\Sonniss.com - GDC 2017 - Game Audio Bundle\\Bluezone Corporation - Titanium - Cinematic Trailer Samples',
    #             'wavs\\Sonniss.com - GDC 2017 - Game Audio Bundle\\Borg Sound - Harley Davidson Sportster Iron 883',
    #             'wavs\\Sonniss.com - GDC 2017 - Game Audio Bundle\\Borg Sound - Gym weights']
    #
    # path = 'D:\\thesis-data\\bulgar\\ACDC\\Back In Black'
    #
    # list_grid_setup = [(100, 100, 30, 30),
    #                    (150, 150, 60, 60)]
    #
    # alternate_grid = [(150, 150, 60, 60),
    #                   (200, 200, 70, 70),  # too high, but acceptable results
    #                   (250, 250, 80, 80)]  # seems to cap
    #
    # get_similarity(path, alternate_grid)

