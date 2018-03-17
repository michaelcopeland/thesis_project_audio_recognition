"""Script for processing information and bundling information"""

from os import walk
import audioSimilarity
import waveReader
import matplotlib.pyplot as plt
import numpy as np
import fingerprintWorker as worker

sim = audioSimilarity.AudioSimilarity()

def get_all_files(directory_path):
    """Returns all stored wavs"""
    files = []

    for (dirpath, dirname, filenames) in walk(directory_path):
        files.extend(filenames)
    #print(files)
    return files

def get_all_waveforms(dir='test_data/', list_of_wavs=[]):
    files = get_all_files(dir)

    sim = audioSimilarity.AudioSimilarity()

    for f in files:
        fs, data = waveReader.read_wave_file(dir+f)
        peaks = worker.retrieve_unfiltered_peaks(dir+f)

        sim.add_audio_data(f, [fs, data, peaks])

    res = sim.storedAudio
    return res

dictionary_of_wavs = get_all_waveforms()

s1 = dictionary_of_wavs['river1.wav'][2]
s2 = dictionary_of_wavs['c1.wav'][2]

wav1 = dictionary_of_wavs['river1.wav'][1]
wav2 = dictionary_of_wavs['c1.wav'][1]
print(wav1,'\n',wav2)

freq1 = [x[0] for x in s1]
time1 = [x[1] for x in s1]

freq2 = [x[0] for x in s2]
time2 = [x[1] for x in s2]

x1 = np.array([freq1, time1])
x2 = np.array([freq2, time2])

sim.plot_waves(wav1, wav2)
#pears = sim.get_pearson_correlation(wav1, wav2)
#corc  = sim.get_correlated_coefficients(freq1, freq2)
xcor   = sim.get_xcorr(wav2, wav1)
plt.xcorr(wav2, wav1)
plt.grid(True)
plt.show()


#print(pears)
#print(corc)
print(xcor)

