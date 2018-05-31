# This script is used in storing or retrieving generated gridHash objects

from datasketch import MinHash
import numpy as np
import fingerprintWorker as fw
import pickle
import os

# You may want to set your own paths

#file paths
EXPORT_PATH     = 'C:\\Users\\Vlad\\Documents\\thesis\\audioExtraction\\exported_grids'
WAV_GRIDS       = 'C:\\Users\\Vlad\\Documents\\thesis\\audioExtraction\\wav_grids'

wav_root        = 'D:\\thesis-data'
mpeg_root       = 'D:\\xmpeg-bulgar'

# test paths
db_test         = 'D:\\db_test'
test_export     = 'D:\\grid_test\\mp3\\7535'

wav_test        = 'D:\\grid_test\\wav_test'
flac_test       = 'C:\\Users\\Vlad\Documents\\thesis\\audioExtraction\\flac_test'


##### supported audio encodings #####
VALID_EXT   = ['.wav', '.ogg', '.mp3', '.flac', '.grid', '.mpeg']
CUSTOM_EXT  = '.grid'


##### DIRECTORY STRUCTURE METHODS #####
def _get_dir_structure(dir_path):
    """Returns all stored files"""
    files = []

    for (dirpath, dirname, filenames) in os.walk(dir_path):
        files.append([dirpath, filenames])

    return files


def has_valid_extension(path_to_file):
    """Checks if file extension is valid
    Valid extensions: '.wav', '.ogg', '.mp3', '.flac', '.grid', '.mpeg'
    """
    path, ext = os.path.splitext(path_to_file)
    if ext in VALID_EXT:
        return True
    return False


def build_dir_map(root):
    """creates a dictionary directory structure.
    It maps files to their relative path.

    file.wav -> c//dir/dir2/dir_with_wavs

    Attributes:
        root - where to start looking

    Return:
        map  - dictionary structure
    """
    dir_struct = _get_dir_structure(root)
    map = dict()

    for tup in dir_struct:
        current_directory = tup[0]
        files_in_dir      = tup[1]

        for f in files_in_dir:
            relative_path = current_directory + '\\' + f
            # add key if not already in dict and if file has a valid extension
            if f not in map and has_valid_extension(relative_path):
                map[f] = current_directory

    return map


##### IO METHODS #####
def export_file(file_name, data, dest_dir=EXPORT_PATH):
    """Stores gridHash file to specified location

    Attributes:
        file_name - name of file
        data      - information to package to the file
        dest_dir  - file path
    """
    name = file_name[:-4] + CUSTOM_EXT
    path = dest_dir + '\\' + name

    with open(path, mode='wb') as f:
        try:
            min_data = get_minHash(data)
            pickle.dump(min_data, f)
            f.close()
            print('Exported: {}'.format(name))
            return True
        except:
            print('Export failed: {}'.format(name))
            return False


def load_grid(file_name, local_dir=test_export):
    """Loads gridHash file from specified location.

    Attributes:
        file_name - name of file to load
        local_dir - load path

    Return:
        data - retrieved information
    """
    path = local_dir + '\\' + file_name
    filename, ext = os.path.splitext(path)

    if ext != CUSTOM_EXT:
        path = path[:-len(ext)] + CUSTOM_EXT

    with open(path, 'rb') as f:
        data = pickle.load(f)

    return data


##### minHash helper method ######
def get_minHash(input_set):
    """Generates minHash object from input set
    Attributes:
        input_set - list of strings to minHash
    Returns:
        minHash object
    """
    min_h = MinHash()

    for itm in input_set:
        min_h.update(itm.encode('utf8'))

    return min_h


def export_many(limit=0):
    """Exports multiple gridHash objects"""
    # initialize counter for files to be indexed
    counter = 0
    # build directory maps
    dir_map = build_dir_map(wav_test)
    indexed = build_dir_map(test_export)

    # set grid hash parameters
    fw.fgp_api.set_grid_attributes(150, 150, 75, 75)

    # go file by file
    for tr in dir_map.keys():
        if counter < limit:
            # check if the file has not already been exported
            pre = tr[:-4] + CUSTOM_EXT
            if pre not in indexed.keys():
                _path      = dir_map[tr] + '\\' + tr

                # ensure a valid extension
                if has_valid_extension(_path):
                    set_data = fw.fingerprint_worker(_path, grid_only=True, plot=False)
                    #print(tr, set_data)

                    # generate gridhash
                    res = export_file(tr, set_data, dest_dir=test_export)

                    if res:
                        counter += 1
                    else:
                        return

    print('Exported {} grids'.format(counter))


if __name__=='__main__':
    export_many(14)
