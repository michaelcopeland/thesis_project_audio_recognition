import exportData as export
import audioHelper as hlp
import os
import numpy as np
import time
import math

from fingerprint import Fingerprint
from audioHelper import AudioHelper
fgp_api = Fingerprint()


class Worker(object):

    def __init__(self, db):
        self.fgp_db = db

    def mic_recognize(self, limit=None):
        if limit is None:
            limit = 30

        print('Microphone recognition: {} seconds'.format(limit))
        self.mic = AudioHelper()
        result = set()

        mic_data = self.mic.recognize(limit=limit)
        for num_channels, channel in enumerate(mic_data):
            hashes = fgp_api.fingerprint(channel, frame_rate=self.mic.samplerate, verbose=True, plot=True)

            result |= set(hashes)
        return result

    def fingerprint_worker(self, file_path, limit=None, grid_only=False, verbose=False, plot=False):
        #st = time.time()
        song_name, extension = os.path.splitext(file_path)
        # print('Fingerprinting: ', song_name, '\nFile extension: ', extension)

        # using different extraction method for mp3
        if extension is '.mp3' or '.mpeg':
            # print(file_path)
            num_channels, frame_rate, audio_data = hlp.retrieve_audio_mpeg(file_path, limit)
        else:
            num_channels, frame_rate, audio_data = hlp.retrieve_audio(file_path, limit)
        #print('from fingerprint worker\n frame rate {}, data {}'.format(frame_rate, channels))
        result = set()

        for num_channels, channel in enumerate(audio_data):
            # print('Channel number:', num_channels+1)
            hashes = fgp_api.fingerprint(channel, frame_rate=frame_rate, verbose=verbose, plot=plot)

            if grid_only:
                return fgp_api.fingerprint(channel, frame_rate=frame_rate, grid_only=grid_only, plot=plot)

            result |= set(hashes)

        #ft = time.time() - st
        #print('Elapsed fingerprinting time: ', ft)
        #print('Generated {} hashes'.format(len(result)))
        return song_name, result

    def insert_wav_to_db(self, song_n):
        #db.connect()
        song_name, list_hash = self.fingerprint_worker(song_n, limit=None)

        print('Song name: ', song_name)
        print('Number of generated hashes: ', len(list_hash))

        self.fgp_db.insert_song(song_name, 1)

        for h in list_hash:
            self.fgp_db.insert_fingerprint(h[0], song_name, h[1])

    def get_max_track_frequency(self, list_tracks):
        """Interates through a list of tuples (track, frequency of track) and returns the maximum value"""
        max_t_frequ = 0
        for t in list_tracks.keys():
            if list_tracks[t] > max_t_frequ:
                max_t_frequ = list_tracks[t]
        return max_t_frequ

    def align_matches_weighted(self, list_matches):
        candidates = dict()

        for tup in list_matches:
            track_name, time_delta = tup

            if time_delta not in candidates:
                candidates[time_delta] = dict()
            if track_name not in candidates[time_delta]:
                candidates[time_delta][track_name] = 1
            else:
                candidates[time_delta][track_name] += 1

        weighted_candidates = []
        # each candidate is a tuple of (weight, (k,v))
        # default weight = 1
        # formula    = (e ^ -(|time_delta|)) + max time delta value over a candidate list
        for k, v in candidates.items():
            cand_weight = float(math.e ** (-abs(k))) * 1000
            max_t_freq = self.get_max_track_frequency(v)
            cand_tup = (cand_weight + max_t_freq, k, v)

            weighted_candidates.append(cand_tup)

        weighted_candidates = sorted(weighted_candidates, key=lambda weight: weight[0])
        res = [elem for elem in weighted_candidates if elem[0] > 100.0]

        # escape case where list of candidates is empty
        if len(res) == 0:
            return {'song id': 0,
            'song name': 'No results found',
            'is fingerprinted': 0}, candidates, res

        prime_candidate = res[-1]
        prime_weight = prime_candidate[0]
        max_count = 0
        query_track = ''

        # query the track with most hits
        for k, v in prime_candidate[2].items():
            if v > max_count:
                max_count = v
                query_track = k

        query_hit, id, name, is_fng = self.fgp_db.get_song_by_name(query_track)

        # cut-off weight for candidates
        CUT_OFF_WEIGHT_1 = 368.87944117144235
        CUT_OFF_WEIGHT_2 = 1010
        if prime_weight <= CUT_OFF_WEIGHT_2 and max_count <= 10:
            track = {
                'song id': 0,
                'song name': 'No results found',
                'is fingerprinted': 0,
            }
            return track, candidates, res

        track = {
            'song id': id,
            'song name': name,
            'is fingerprinted': int(is_fng),
        }

        return track, candidates, res

    def fingerprint_songs(self, user_path='', num_tracks=None):
        #dir_structure = export.build_dir_map(export.mpeg_root)
        dir_structure = export.build_dir_map(user_path)

        # get fingerprinted files
        number_fgp, already_fingerprinted = self.get_wavs_by_fgp(1)
        #print(already_fingerprinted)
        #print('Number of fingerprints=', number_fgp)

        song_counter = 0

        # go through each file in the directory
        for file in dir_structure.keys():
            # don't re-fingerprint files
            if file in already_fingerprinted:
                print('Skipping: {}'.format(file))
                continue

            if song_counter == num_tracks:
                print('Added {} tracks to database.'.format(song_counter))
                self.fgp_db.connection.close()
                return

            # path of dir + actual file
            path = dir_structure[file] + '\\' + file

            # avoid invalid extensions
            _pth, ext = os.path.splitext(path)
            if ext not in export.VALID_EXT:
                continue

            # insert song returns true if it managed, false otherwise
            res = self.fgp_db.insert_song(file, 1)
            if res:
                song_counter += 1

                # generate and insert hashes
                _, list_hashes = self.fingerprint_worker(path)
                formatted_list = []
                for h in list_hashes:
                #     db.insert_fingerprint(h[0], file, h[1])
                    formatted_list.append((h[0], file, h[1]))
                res = self.fgp_db.dump_fingerprints(formatted_list)

                # stop everything in case of failure
                if not res:
                    self.fgp_db.delete_songs([file])
                    print('Fingerprinting failed for: {}'.format([file]))
                    return
            else:
                print('Fingerprinting skipped')
                continue

        print('Number of wavs: ', song_counter)

    def get_wavs_by_fgp(self, is_fgp=0):
        res = list(self.fgp_db.get_songs_by_fgp_status(is_fgp))

        clean_list = []
        for elem in res:
            temp = str(elem)[2:-3]
            clean_list.append(temp)
        # print(clean_list)

        number_of_tracks = len(clean_list)
        return number_of_tracks, clean_list

  
