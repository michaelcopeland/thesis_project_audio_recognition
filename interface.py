import os
import sys
import json
import argparse

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

    parser = argparse.ArgumentParser(description='Welcome to the audio search engine.'\
                                     'The microphone recognition functionality is still under testing.'\
                                     'Low accuracy levels.')
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

    args = parser.parse_args()

    try:
        # set database configuration
        wrapper = load_config()
    except IOError as err:
        print('Could not open config file \n', str(err))
        sys.exit(1)

    if args.database:
        print(wrapper.config_info())
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
            list_hash = wrapper.worker.mic_recognize(limit=opt_arg)

            matches = wrapper.worker.fgp_db.get_matches(list_hash)

            result_track, matched_fam, res = wrapper.worker.align_matches_weighted(matches)

            print('Recognized tracks:\n')
            for t in res:
                print(t)

    if args.recognize_file:
        path = os.path.abspath(args.recognize_file[0])
        limit = int(args.recognize_file[1])

        sn, list_hash = wrapper.worker.fingerprint_worker(path, limit=limit)

        matches = wrapper.worker.fgp_db.get_matches(list_hash)

        result_track, matched_fam, res = wrapper.worker.align_matches_weighted(matches)

        print('Recognized track= ', result_track)
