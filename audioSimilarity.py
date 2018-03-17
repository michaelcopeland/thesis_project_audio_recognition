"""Stores audio information and allows to compute various similarity searches"""

import waveReader

from fingerprint import Fingerprint
from scipy.signal import correlate2d, correlate
from scipy.stats import pearsonr
import numpy as np
import matplotlib.pyplot as plt

class AudioSimilarity():
    def __init__(self):
        self.storedAudio = dict()

    def add_audio_data(self, wav_name, data):
        self.storedAudio[wav_name] = data

    def get_audio_data(self, wav_name):
        return self.storedAudio[wav_name]

    def get_xcorr(self, wav_file1, wav_file2):
        cor_arr = correlate(wav_file1, wav_file2, mode='same')
        return cor_arr

    def get_pearson_correlation(self, wav_file1, wav_file2):
        print('Computing Pearson correlation')
        l1 = len(wav_file1)
        l2 = len(wav_file2)

        # ensure the files are the same length
        if l1 > l2:
            wav_file1 = wav_file1[:l2]
        else:
            wav_file2 = wav_file2[:l1]

        res = pearsonr(wav_file1, wav_file2)
        return res

    def get_correlated_coefficients(self, wav_file1, wav_file2):
        print('Computing correlated coefficients')
        l1 = len(wav_file1)
        l2 = len(wav_file2)

        if l1 > l2:
            wav_file1 = wav_file1[:l2]
        else:
            wav_file2 = wav_file2[:l1]

        res = np.corrcoef(wav_file1, wav_file2)
        return res

    def plot_waves(self, wav1, wav2):
        l1 = len(wav1)
        l2 = len(wav2)

        if l1 > l2:
            wav1 = wav1[:l2]
        else:
            wav2 = wav2[:l1]
        #print(np.shape(wav1))
        #print(np.shape(wav2))
        plt.plot(wav1, wav2, 'bs', wav1, '--r', wav2)
        plt.show()

