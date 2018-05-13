# Based on Will Drevo's DejaVu

import MySQLdb as mysql

WAV_DB                      = 'audioExtraction'
MP3_DB                      = 'mpegExtraction'
TEST_DATABASE               = 'test_audio'

FINGERPRINTS_TABLE          = 'fingerprints'
SONGS_TABLE                 = 'songs'

FINGERPRINT_FIELD_ID        = 'id'
FINGERPRINT_FIELD_HASHKEY   = 'hash_key'
FINGERPRINT_FIELD_SONGNAME  = 'song_name'
FINGERPRINT_FIELD_TIMEOFFSET= 'time_offset'

SONGS_FIELD_SONG_ID         = 'song_id'
SONGS_FIELD_SONG_NAME       = 'song_name'
SONGS_FIELD_FINGERPRINTED   = 'is_fingerprinted'


def connect():
    db = mysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        passwd='iamfuzzy222',
        db=WAV_DB
    )
    print('Connected to database!')
    return db


def close_database():
    connection.close()
    print('Connection closed.')


##### CREATE STATEMENTS #####

CREATE_FINGERPRINTS_TABLE = """
CREATE TABLE IF NOT EXISTS {} (
{}     int AUTO_INCREMENT PRIMARY KEY,
{}     varchar(20),
{}     varchar(150) NOT NULL,
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
{}       varchar(150) NOT NULL,
{}       tinyint DEFAULT 0,
UNIQUE KEY {}({})
);
""".format(SONGS_TABLE, SONGS_FIELD_SONG_ID,
           SONGS_FIELD_SONG_NAME, SONGS_FIELD_FINGERPRINTED,
           SONGS_FIELD_SONG_NAME, SONGS_FIELD_SONG_NAME)

##### BOBBY STATEMENTS #####

DROP_FINGERPRINTS = 'DROP TABLE IF EXISTS {}'.format(FINGERPRINTS_TABLE)
DROP_SONGS = 'DROP TABLE IF EXISTS {}'.format(SONGS_TABLE)

DELETE_FINGERPRINTS = 'DELETE FROM {} WHERE {} IN (%s)'.format(FINGERPRINTS_TABLE,
                                                               FINGERPRINT_FIELD_SONGNAME)

DELETE_SONGS = 'DELETE FROM {} WHERE {} IN (%s)'.format(SONGS_TABLE,
                                                        SONGS_FIELD_SONG_NAME)

##### INSERT STATEMENTS #####

INSERT_SONG = 'INSERT INTO {}({}, {}) VALUES (\'%s\', \'%s\');'.format(SONGS_TABLE,
                                                                       SONGS_FIELD_SONG_NAME,
                                                                       SONGS_FIELD_FINGERPRINTED)

INSERT_FINGERPRINT = 'INSERT INTO {}({},{},{}) VALUES (\'%s\', \'%s\', \'%s\');'.format(FINGERPRINTS_TABLE,
                                                                                        FINGERPRINT_FIELD_HASHKEY,
                                                                                        FINGERPRINT_FIELD_SONGNAME,
                                                                                        FINGERPRINT_FIELD_TIMEOFFSET)

INSERT_FINGERPRINT_DUMP = 'INSERT INTO {}({}, {}, {}) VALUES %s;'.format(FINGERPRINTS_TABLE,
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

SELECT_SONG_NAME = 'SELECT {}, {}, {} FROM {} WHERE {} = (\'%s\')'.format(SONGS_FIELD_SONG_ID,
                                                                          SONGS_FIELD_SONG_NAME,
                                                                          SONGS_FIELD_FINGERPRINTED,
                                                                          SONGS_TABLE,
                                                                          SONGS_FIELD_SONG_NAME)

SELECT_SONG_BY_FGP = 'SELECT {} FROM {} WHERE {} = %s'.format(SONGS_FIELD_SONG_NAME,
                                                              SONGS_TABLE,
                                                              SONGS_FIELD_FINGERPRINTED)

##### UPDATE STATEMENTS #####
UPDATE_IS_FINGERPRINTED = 'UPDATE {} SET {}=(%s) WHERE {} IN (%s)'.format(SONGS_TABLE,
                                                                          SONGS_FIELD_FINGERPRINTED,
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
        print('Failed to setup tables.')
        connection.rollback()


def insert_song(song_name='', fgp=0):
    insert_query = INSERT_SONG % (song_name, fgp)
    insert_query.encode('utf-8')

    try:
        cur.execute(insert_query)
        connection.commit()
        print('Inserted song: {}'.format(song_name))
        return True
    except:
        connection.rollback()
        print('Could not insert {}'.format(song_name))
        print('Title may be over 150 chars long, or there are special characters in the string')
        return False


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


def dump_fingerprints(formatted_list):
    """Receives a list of fingerprints to insert to the database
    The row look like: hashkey, name of song, time offset
    """
    dump_insert = INSERT_FINGERPRINT_DUMP

    num_elem = len(formatted_list)
    dump_insert = dump_insert % ', '.join(['%s'] * num_elem)

    try:
        connection.ping()
        cur.execute(dump_insert, formatted_list)
        connection.commit()
    #print('dump successful!')
        return True
    except:
        connection.rollback()
        print('Dumping fingerprints failed')
        return False


def delete_fgp_by_song(list_song_n):
    """Deletes fingerprints for each song in the parameter list of song

    Attribute:
        list_song_n - list of songs for which to delete fingerprints
    """
    songs = ', '.join(str('\'' + x + '\'') for x in list_song_n)

    delete_statement = DELETE_FINGERPRINTS % songs

    if songs is not '':
        try:
            print('Deleting fingerprint for:\n {}'.format(songs))
            cur.execute(delete_statement)
            connection.commit()
        except:
            connection.rollback()
            print('Could not delete fingerprints')
            return
        print('Deletion successful!')

    else:
        print('Deletion failed: no songs in list')


def delete_songs(list_song_n):
    songs = ', '.join(str('\'' + x + '\'') for x in list_song_n)

    delete_statement = DELETE_SONGS % songs

    if songs is not '':
        try:
            print('Deleting songs:\n {}'.format(songs))
            cur.execute(delete_statement)
            connection.commit()
        except:
            connection.rollback()
            print('Could not delete songs')
            return
        print('Deletion successful!')


def update_is_fingerprinted(list_song_n, is_fingerprinted):
    """Set the is_fingerprinted filed of a list of song

    Attributes:
        list_song_n       - a list of song names
        is_fingerprinted  - 0 not fingerprinted, 1 fingerprinted
    """
    songs = ', '.join(str('\'' + x + '\'') for x in list_song_n)

    update_statement = UPDATE_IS_FINGERPRINTED % (is_fingerprinted, songs)

    if songs is not '':
        try:
            print('Updating songs to is_fingerprinted={}'.format(SONGS_FIELD_FINGERPRINTED))
            cur.execute(update_statement)
            connection.commit()
        except:
            connection.rollback()
            print('Update failed: is_fingerprinted status could not be written')
            return
        print('Success!')
    else:
        print('Update failed: No songs in list')


def get_songs_by_fgp_status(is_fgp=0):
    """Retrieves song names based on the is_fingerprinted value

    Attributes:
        is_fgp - 0 not fingerprinted, 1 is fingerprinted

    Return:
        res_list - a list of song names
    """

    select_query = SELECT_SONG_BY_FGP % is_fgp

    try:
        print('Retrieving songs with is_fingeprinted={}'.format(is_fgp))
        cur.execute(select_query)
        connection.commit()

        result = []
        for res in cur:
            result.append(res)
        return result
        #print('Success!')
    except:
        connection.rollback()
        print('Songs could not be retrieved')


def get_song_by_name(song_name):
    select_query = SELECT_SONG_NAME % song_name

    song_id = 0
    song_name = ''
    is_fingerprinted = 0

    try:
        cur.execute(select_query)
        connection.commit()
    except:
        print('Error in get_song_by_name')
        connection.rollback()

    for id, name, is_fgp in cur:
        song_id = id
        song_name = name
        is_fingerprinted = is_fgp

    if song_id is 0 and song_name == '':
        song_name = 'No results found'
        return False, song_id, song_name, is_fingerprinted

    return True, song_id, song_name, is_fingerprinted


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
    map = dict()
    for hash_key, offset in list_of_hashes:
        map[hash_key] = offset

    values = map.keys()
    values = list(filter(None, values))
    values = list(values)

    num_query = len(values)
    query_matches = SELECT_MULTIPLE

    # escape rare cases where the track is so short it generates no hash_keys
    if num_query == 0:
        return 'nothing_to_query', 0

    query_matches = query_matches % ', '.join(['%s'] * num_query)
    #print(query_matches)

    cur.execute(query_matches, values)

    for hash_k, song_name, time_offset in cur:
        # print('result: ', hash_k, song_name, time_offset)
        yield (song_name, time_offset - map[hash_k])


connection = connect()
cur = connection.cursor()
# For indexing: ensure large buffer
cur.execute('set global max_allowed_packet=67108864')

if __name__=='__main__':
    setup()
    print('Hello world!')
