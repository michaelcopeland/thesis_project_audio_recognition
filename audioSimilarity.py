"""This script is mainly used for tests.
compute_jaccard and the main script are used to get the 
resemblance between two gridHash items"""

from datasketch import MinHash
from scipy.signal import correlate2d, correlate
from scipy.stats import pearsonr, linregress

import audioHelper as hlp
import exportData as export
import numpy as np
import matplotlib.pyplot as plt
import fingerprintWorker as fw


class AudioSimilarity:
    """[DEPRECATED]Class use to run cross signal cross correlation and other
    regresion analysis."""
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

def minHash(set1, set2):
    """Use minHash to compute the jaccard distance between two sets"""
    m1, m2 = MinHash(), MinHash()

    for d in set1:
        m1.update(d.encode('utf8'))
    for d in set2:
        m2.update(d.encode('utf8'))

    sim = m1.jaccard(m2)
    return sim

def get_similarity(list_dir, grid_setup):
    """[DEPRECATED]Receives a list of folders each containing audio files.
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


def compute_jaccard(s1, s2):
    """Computes jaccard distance between two gridHash files"""
    dir_map = export.build_dir_map(export.test_export)

    c1 = None
    c2 = None

    for itm in dir_map.keys():
        if itm == s1:
            c1 = export.load_grid(itm, local_dir=export.test_export)
        if itm == s2:
            c2 = export.load_grid(itm, local_dir=export.test_export)

    sim = c1.jaccard(c2)
    return sim


if __name__=='__main__':
    # Compute jaccard dist between gridHash objects in a directory
    dir_map = export.build_dir_map(export.test_export)

    for tr1 in dir_map.keys():
        for tr2 in dir_map.keys():
            if tr1 != tr2:
                sim = compute_jaccard(tr1, tr2)
                print(sim, tr1, '||', tr2)

