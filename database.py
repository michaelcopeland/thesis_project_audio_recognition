# Based on Will Drevo's DejaVu

import MySQLdb as mysql

FINGERPRINTS_TABLE = 'fingerprints'
SONGS_TABLE = 'songs'

FINGERPRINT_FIELD_HASHKEY = 'hashkey'
FINGERPRINT_FIELD_SONGNAME = 'song_name'
FINGERPRINT_FIELD_TIMEOFFSET = 'time_offset'

SONGS_FIELD_SONG_ID = 'song_id'
SONGS_FIELD_SONG_NAME = 'song_name'
SONGS_FIELD_FINGERPRINTED = 'fingerprint'

def connect():
    db = mysql.connect(
        host='127.0.0.1',
        user='root',
        passwd='',
        db='audioExtraction'
    )
    print('Connected to database!')
    return db

def close_database():
    connection.close()
    print('Connection closed.')

connection = connect()
cur = connection.cursor()

CREATE_FINGERPRINTS_TABLE= """
CREATE TABLE IF NOT EXISTS {} (
{}     varchar(20) PRIMARY KEY,
{}     varchar(100) NOT NULL,
{}     int unsigned NOT NULL,
INDEX({}),
FOREIGN KEY ({}) REFERENCES {}({}) ON DELETE CASCADE 
);""".format(FINGERPRINTS_TABLE, FINGERPRINT_FIELD_HASHKEY,
             FINGERPRINT_FIELD_SONGNAME, FINGERPRINT_FIELD_TIMEOFFSET,
             FINGERPRINT_FIELD_HASHKEY,
             FINGERPRINT_FIELD_SONGNAME, SONGS_TABLE, SONGS_FIELD_SONG_NAME)

CREATE_SONGS_TABLE= """
CREATE TABLE IF NOT EXISTS {} (
{}       int unsigned AUTO_INCREMENT PRIMARY KEY,
{}       varchar(100) NOT NULL,
{}       tinyint DEFAULT 0,
UNIQUE KEY {}({})
);
""".format(SONGS_TABLE, SONGS_FIELD_SONG_ID,
           SONGS_FIELD_SONG_NAME, SONGS_FIELD_FINGERPRINTED,
           SONGS_FIELD_SONG_NAME, SONGS_FIELD_SONG_NAME)

DROP_FINGERPRINTS = 'DROP TABLE IF EXISTS {}'.format(FINGERPRINTS_TABLE)
DROP_SONGS        = 'DROP TABLE IF EXISTS {}'.format(SONGS_TABLE)

INSERT_SONG = 'INSERT INTO {}({}, {}) VALUES (\'%s\', \'%s\');'.format(SONGS_TABLE,
                                                                       SONGS_FIELD_SONG_NAME,
                                                                       SONGS_FIELD_FINGERPRINTED)

INSERT_FINGERPRINT = 'INSERT INTO {}({},{},{}) VALUES (\'%s\', \'%s\', \'%s\');'.format(FINGERPRINTS_TABLE,
                                                                                        FINGERPRINT_FIELD_HASHKEY,
                                                                                        FINGERPRINT_FIELD_SONGNAME,
                                                                                        FINGERPRINT_FIELD_TIMEOFFSET)

SELECT = 'SELECT {}, {} FROM {} WHERE {} = \'%s\';'.format(FINGERPRINT_FIELD_SONGNAME,
                                                FINGERPRINT_FIELD_TIMEOFFSET,
                                                FINGERPRINTS_TABLE,
                                                FINGERPRINT_FIELD_HASHKEY)

SELECT_ALL = 'SELECT {}, {} FROM {};'.format(FINGERPRINT_FIELD_SONGNAME,
                                             FINGERPRINT_FIELD_TIMEOFFSET,
                                             FINGERPRINTS_TABLE)

def clear_database():
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
    insert_query = INSERT_FINGERPRINT % (hashkey, song_name, time_offset)
    insert_query.encode('utf-8')

    try:
        cur.execute(insert_query)
        connection.commit()
        print('Fingerprint inserted!')
    except:
        connection.rollback()

def query(hashkey=None):
    """
    Return all tuples associated with hash.
    If hash is None, returns all entries in the
    database (be careful with that one!).
    """
    print('query!')
    if hashkey is None:
        print('Select all')
        select_query = SELECT_ALL
    else:
        print('select')
        select_query = SELECT % hashkey

    print('query is ', select_query)
    cur.execute(select_query)
    connection.commit()
    for s_name, offset in cur:
        print(s_name, offset)
        yield (s_name, offset)

connect()
#clear_database()
#setup()
#insert_song('metric', 1)
insert_song('vlad', 1)
insert_fingerprint('fsfdsfdsfds', 'metric', 60)
insert_fingerprint('abc', 'vlad', 2)
query('fsfdsfdsfds')

#close_database()


