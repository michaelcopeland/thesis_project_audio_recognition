"""Stores audio information and allows to compute various similarity searches"""

from datasketch import MinHash
from fingerprint import Fingerprint
import fingerprintWorker as fw

from scipy.signal import correlate2d, correlate
from scipy.stats import pearsonr, linregress
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

    def minHash(self, set1, set2):
        m1, m2 = MinHash(), MinHash()

        for d in set1:
            m1.update(d.encode('utf8'))
        for d in set2:
            m2.update(d.encode('utf8'))
        print("Estimated Jaccard for set1 and set2 is ", m1.jaccard(m2))

        s1 = set(set1)
        s2 = set(set2)
        actual_jaccard = float(len(s1.intersection(s2))) / float(len(s1.union(s2)))
        print("Actual Jaccard for set1 and set2 is ", actual_jaccard)

def get_similarity(dir_path):
    a = AudioSimilarity()
    fw.fgp_api.set_grid_attributes(100, 100, 30, 30)

    sets = {}
    files = fw.files_in_dir(dir_path)

    for tuple in files:
        dir = tuple[0]
        all_files = tuple[1]

        for current_file in all_files:
            if fw.has_valid_extension(dir+ '\\' + current_file):
                print(current_file)
                grid = fw.fingerprint_worker(dir_path + '\\' + current_file, grid_only=True)
                print(grid)
                sets[current_file] = grid

        # print(sets)
        main_track = 'Lock01_outdoor_opening_lite03.wav'
        main_Set = sets[main_track]

        for k, v in sets.items():
            if k is not main_track:
                print(main_track, ' vs ', k)
                a.minHash(main_Set, v)


if __name__=='__main__':
    get_similarity('C:\\Users\\Vlad\\Documents\\thesis\\audioExtraction\\wavs\\Sonniss.com - GDC 2017 - Game Audio Bundle\\Alexander Ahura - Locks & Keys')
