"""Script for processing information and bundling information"""

from os import walk
import audioSimilarity
import waveReader
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

def get_audio_from_dir(dir='test_data/', list_of_wavs=[]):
    files = get_all_files(dir)

    sim = audioSimilarity.AudioSimilarity()

    for f in files:
        fs, wave_data = waveReader.read_wave_file(dir+f)
        peaks = worker.retrieve_unfiltered_peaks(dir+f)

        f_series = [x[0] for x in peaks]
        t_series = [x[1] for x in peaks]

        refined_peaks = np.array([f_series, t_series])
        sim.add_audio_data(f, [fs, wave_data, refined_peaks])

    res = sim.storedAudio
    return res

data = get_audio_from_dir()

wav1 = data['estring.wav'][1]
wav2 = data['river2.wav'][1]

sim.plot_waves(wav2, wav1)

peaks1 = data['estring.wav'][2]
peaks2 = data['river2.wav'][2]

sim.get_pearson_correlation(peaks1[0], peaks2[0])
sim.get_correlated_coefficients(peaks1[0], peaks2[0])
sim.get_xcorr_2d(peaks1, peaks2)
sim.get_xcorr(peaks1[0], peaks2[0])
sim.get_linear_regression(wav1, wav2)

