import os
import sys
import json
import argparse, argcomplete

from wrapper import Wrapper

DB_CONFIG = 'cnf.cnf'

def load_config():
    try:
        with open(DB_CONFIG) as f:
            config = json.load(f)
    except IOError as err:
        print('Cannot load configuration file. Exiting application \n', str(err))
        sys.exit(1)

    return Wrapper(config)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Welcome to the audio search engine.\n'\
                                                 'You can change all settings by modifying the cnf.cnf file')
    parser.add_argument('-i', '--insert',
                        type=str,
                        help='Folder from which to insert tracks to the database')           
    parser.add_argument('-c', '--count', type=int, default=0,
                        help='Number of items to process\n' \
                        'USAGE: -i <path> -c <number>')
    parser.add_argument('-db', '--database', action='store_true', help='View your database credentials')
    parser.add_argument('-k', '--kill_db', action='store_true', help='Drops then resets tables. Careful.')
    parser.add_argument('-r', '--recognize', nargs=2,
                        help='Recognize a song through microphone\n'\
                        '--recognize mic <num_seconds>\n')

    parser.add_argument('-rf', '--recognize_file', nargs=2,
                        help='Recognize a song from a file\n' \
                        '--recognize <path> <num_seconds>\n')
    parser.add_argument('-ex', '--export', nargs=1,
                        help='Creates gridhash objects from a specified number of audio files '\
                        'and stores them in a preset location. If number is 0, all files are considered.\n'\
                        'Usage: --export <int>')
    parser.add_argument('-gs', '--gridsettings', action='store_true',
                        help='View grid settings')
    parser.add_argument('-sim', '--similarity', nargs=1, type=str,
                        help='Takes one grid file and compares with other files. Returns Jaccard similarity'\
                             ' coefficients between all grid files.')
    parser.add_argument('-ls', '--list', nargs=1, type=str,
                        help='Lists files in <grid> or <input> directory\n'\
                        'Usage:\n -ls grid\n-ls input')

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    try:
        # set database configuration
        wrapper = load_config()
    except IOError as err:
        print('Could not open config file \n', str(err))
        sys.exit(1)

    if args.database:
        wrapper.config_info()
        wrapper.get_connection()

    if args.insert and args.count:
        path  = os.path.abspath(args.insert)
        count = args.count

        wrapper.handle_insert_songs(path, count)

    if args.kill_db:
        wrapper.handle_db_reset()

    if args.recognize:
        result_track = None

        source = args.recognize[0]
        opt_arg = args.recognize[1]

        if source in ('mic', 'microphone'):
            res = wrapper.handle_recognize_from_mic(int(opt_arg))
            print('Recognized tracks:\n')
            for t in res:
                print(t)

    if args.recognize_file:
        path = os.path.abspath(args.recognize_file[0])
        limit = int(args.recognize_file[1])

        res = wrapper.handle_recognize_from_file(path, limit)
        print(res)

    if args.gridsettings:
        wrapper.pretty_print_grid_settings()

    if args.export:
        count = args.export[0]

        wrapper.handle_grid_export(int(count))

    if args.similarity:
        prim = args.similarity[0]
        wrapper.handle_sim(prim)

    if args.list:
        dir = args.list[0]

        if dir == 'grid':
            wrapper.handle_list_folder_contents(switch=False)
        elif dir == 'input':
            wrapper.handle_list_folder_contents(switch=True)
        else:
            print('<grid> to view contents of grid folder\n<input> to view contents of your source folder')