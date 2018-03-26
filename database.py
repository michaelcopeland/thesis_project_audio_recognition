# Based on Will Drevo's DejaVu

import MySQLdb as mysql
from itertools import zip_longest

FINGERPRINTS_TABLE = 'fingerprints'
SONGS_TABLE = 'songs'

FINGERPRINT_FIELD_ID = 'id'
FINGERPRINT_FIELD_HASHKEY = 'hash_key'
FINGERPRINT_FIELD_SONGNAME = 'song_name'
FINGERPRINT_FIELD_TIMEOFFSET = 'time_offset'

SONGS_FIELD_SONG_ID = 'song_id'
SONGS_FIELD_SONG_NAME = 'song_name'
SONGS_FIELD_FINGERPRINTED = 'is_fingerprinted'


def connect():
    db = mysql.connect(
        host='127.0.0.1',
        user='root',
        passwd='iamfuzzy222',
        db='audioExtraction'
    )
    print('Connected to database!')
    return db


def close_database():
    connection.close()
    print('Connection closed.')


connection = connect()
cur = connection.cursor()

##### CREATE STATEMENTS #####

CREATE_FINGERPRINTS_TABLE = """
CREATE TABLE IF NOT EXISTS {} (
{}     int AUTO_INCREMENT PRIMARY KEY,
{}     varchar(20),
{}     varchar(100) NOT NULL,
{}     int unsigned NOT NULL,
INDEX({}),
FOREIGN KEY ({}) REFERENCES {}({}) ON DELETE CASCADE 
);""".format(FINGERPRINTS_TABLE, FINGERPRINT_FIELD_ID, FINGERPRINT_FIELD_HASHKEY,
             FINGERPRINT_FIELD_SONGNAME, FINGERPRINT_FIELD_TIMEOFFSET,
             FINGERPRINT_FIELD_HASHKEY,
             FINGERPRINT_FIELD_SONGNAME, SONGS_TABLE, SONGS_FIELD_SONG_NAME)

CREATE_SONGS_TABLE = """
CREATE TABLE IF NOT EXISTS {} (
{}       int unsigned AUTO_INCREMENT PRIMARY KEY,
{}       varchar(100) NOT NULL,
{}       tinyint DEFAULT 0,
UNIQUE KEY {}({})
);
""".format(SONGS_TABLE, SONGS_FIELD_SONG_ID,
           SONGS_FIELD_SONG_NAME, SONGS_FIELD_FINGERPRINTED,
           SONGS_FIELD_SONG_NAME, SONGS_FIELD_SONG_NAME)

##### BOBBY STATEMENTS #####

DROP_FINGERPRINTS = 'DROP TABLE IF EXISTS {}'.format(FINGERPRINTS_TABLE)
DROP_SONGS = 'DROP TABLE IF EXISTS {}'.format(SONGS_TABLE)

##### INSERT STATEMENTS #####

INSERT_SONG = 'INSERT INTO {}({}, {}) VALUES (\'%s\', \'%s\');'.format(SONGS_TABLE,
                                                                       SONGS_FIELD_SONG_NAME,
                                                                       SONGS_FIELD_FINGERPRINTED)

INSERT_FINGERPRINT = 'INSERT INTO {}({},{},{}) VALUES (\'%s\', \'%s\', \'%s\');'.format(FINGERPRINTS_TABLE,
                                                                                        FINGERPRINT_FIELD_HASHKEY,
                                                                                        FINGERPRINT_FIELD_SONGNAME,
                                                                                        FINGERPRINT_FIELD_TIMEOFFSET)
###### SELECT STATEMENTS #####

SELECT = 'SELECT {}, {} FROM {} WHERE {} = \'%s\';'.format(FINGERPRINT_FIELD_SONGNAME,
                                                           FINGERPRINT_FIELD_TIMEOFFSET,
                                                           FINGERPRINTS_TABLE,
                                                           FINGERPRINT_FIELD_HASHKEY)

SELECT_ALL = 'SELECT {}, {}, {} FROM {};'.format(FINGERPRINT_FIELD_SONGNAME,
                                                 FINGERPRINT_FIELD_HASHKEY,
                                                 FINGERPRINT_FIELD_TIMEOFFSET,
                                                 FINGERPRINTS_TABLE)

SELECT_MULTIPLE = 'SELECT {}, {}, {} FROM {} WHERE {} IN (%s)'.format(FINGERPRINT_FIELD_HASHKEY,
                                                                      FINGERPRINT_FIELD_SONGNAME,
                                                                      FINGERPRINT_FIELD_TIMEOFFSET,
                                                                      FINGERPRINTS_TABLE,
                                                                      FINGERPRINT_FIELD_HASHKEY)

SELECT_SONG_NAME = 'SELECT {}, {}, {} FROM {} WHERE {} IN (%s)'.format(SONGS_FIELD_SONG_ID,
                                                                       SONGS_FIELD_SONG_NAME,
                                                                       SONGS_FIELD_FINGERPRINTED,
                                                                       SONGS_TABLE,
                                                                       SONGS_FIELD_SONG_NAME)


def drop_all_tables():
    try:
        cur.execute(DROP_FINGERPRINTS)
        cur.execute(DROP_SONGS)
        connection.commit()
        print('Database cleared!')
    except:
        connection.rollback()


def setup():
    try:
        cur.execute(CREATE_SONGS_TABLE)
        print('Created songs table.')
        cur.execute(CREATE_FINGERPRINTS_TABLE)
        print('Created fingerprints table.')
        connection.commit()
        print('Setup complete!')
    except:
        connection.rollback()


def insert_song(song_name='', fgp=0):
    insert_query = INSERT_SONG % (song_name, fgp)
    insert_query.encode('utf-8')

    try:
        cur.execute(insert_query)
        connection.commit()
        print('Song inserted!')
    except:
        connection.rollback()


def insert_fingerprint(hashkey, song_name, time_offset):
    """
    Inserts a fingerprint in the database.

    There can be duplicate fingerprints.
    """
    insert_query = INSERT_FINGERPRINT % (hashkey, song_name, time_offset)
    insert_query.encode('utf-8')

    try:
        cur.execute(insert_query)
        connection.commit()
        # print('Fingerprint inserted!')
    except:
        connection.rollback()


def get_song_by_name(song_name):
    select_query = SELECT_SONG_NAME % song_name

    song_id = 0
    song_name = ''
    is_fingerprinted = 0

    try:
        song_id, song_name, is_fingerprinted = cur.execute(select_query)
        connection.commit()
    except:
        print('Error in get_song_by_name')
        connection.rollback()

    if song_id is not None and song_name is not '':
        return True, song_id, song_name, is_fingerprinted
    return False, song_id, song_name, is_fingerprinted

def query_all_fingerprints():
    """
    Returns song name, hash key, time offset
    of all items in the fingerprints table
    """
    try:
        cur.execute(SELECT_ALL)
        connection.commit()

        for s_name, h_key, t_offset in cur:
            yield (s_name, h_key, t_offset)

    except:
        print('Error retrieving all fingerprints')
        connection.rollback()


def query(hashkey=None):
    """
    Return all tuples associated with hash.
    If hash is None, returns empty list.
    """

    if hashkey is None:
        return []
    else:
        print('Querying for ', hashkey)
        select_query = SELECT % hashkey

    cur.execute(select_query)
    connection.commit()
    for s_name, offset in cur:
        # print(s_name, offset)
        yield (s_name, offset)


def get_matches(list_of_hashes):
    print('Get matches!')
    map = dict()
    for hash_key, offset in list_of_hashes:
        map[hash_key] = offset

    values = map.keys()
    values = list(filter(None, values))
    values = list(values)
    num_query = len(values)

    query = SELECT_MULTIPLE
    query = query % ', '.join(['%s'] * num_query)

    cur.execute(query, values)

    for hash_k, song_name, time_offset in cur:
        # print('result: ', hash_k, song_name, time_offset)
        yield (song_name, time_offset - map[hash_k])
