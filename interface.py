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

    # TODO: wrapper receives a db instance as a parameter
    return Wrapper(config)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Welcome to the audio search engine.')
    parser.add_argument('-i', '--insert',
                        type=str,
                        help='Folder from which to insert tracks to the database')           
    parser.add_argument('-c', '--count', type=int, default=0,
                        help='Number of items to process, zero will take all files form your directory\n'\
                        'USAGE: -i <path> -c <number>')
    parser.add_argument('-db', '--database', action='store_true', help='View your database credentials')
    parser.add_argument('-r', '--reset_db', action='store_true', help='Drops the database tables')

    args = parser.parse_args()

    try:
        # set database configuration
        wrapper = load_config()
    except IOError as err:
        print('Could not open config file \n', str(err))
        sys.exit(1)

    if args.database:
        print(wrapper.info())
        wrapper.connect_to_db()

    if args.insert and args.count:
        path  = args.insert[0]
        count = args.count[1]

    if args.reset_db:
        pass
