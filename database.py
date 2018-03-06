# Based on Will Drevo's DejaVu

import MySQLdb as mysql

FINGERPRINT_TABLE = 'fingerprints'
SONGS_TABLE = 'audioextraction.songs'

FINGERPRINT_FILED_HASHKEY = 'hashkey'
FINGERPRINT_FILED_SONGNAME = 'song_name'
FINGERPRINT_FILED_TIMEOFFSET = 'time_offset'

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

connection = connect()
cur = connection.cursor()

CREATE_FINGERPRINTS_TABLE= """
CREATE TABLE IF NOT EXISTS {} (
{}     varchar(20) PRIMARY KEY,
{}     varchar(100) NOT NULL,
{}     int unsigned NOT NULL,
INDEX({}));""".format(FINGERPRINT_TABLE, FINGERPRINT_FILED_HASHKEY,
                      FINGERPRINT_FILED_SONGNAME, FINGERPRINT_FILED_TIMEOFFSET,
                      FINGERPRINT_FILED_HASHKEY)

CREATE_SONGS_TABLE= """
CREATE TABLE IF NOT EXISTS {} (
{}       int unsigned AUTO_INCREMENT PRIMARY KEY,
{}       varchar(100) NOT NULL,
{}       BOOL DEFAULT TRUE 
);
""".format(SONGS_TABLE, SONGS_FIELD_SONG_ID,
           SONGS_FIELD_SONG_NAME, SONGS_FIELD_FINGERPRINTED)

INSERT_SONG = """INSERT INTO {} ({}, {}) VALUES (%s, %s));""".format(SONGS_TABLE, SONGS_FIELD_SONG_NAME,
                                                                     SONGS_FIELD_FINGERPRINTED)

def clear_database():
    DROP_FINGERPRINTS = 'DROP TABLE IF EXISTS {}'.format(FINGERPRINT_TABLE)
    DROP_SONGS        = 'DROP TABLE IF EXISTS {}'.format(SONGS_TABLE)
    try:
        cur.execute(DROP_FINGERPRINTS)
        cur.execute(DROP_SONGS)
        connection.commit()
        print('Database cleared!')
    except:
        connection.rollback()

def setup():
    try:
        cur.execute(CREATE_FINGERPRINTS_TABLE)
        cur.execute(CREATE_SONGS_TABLE)
        connection.commit()
        print('Setup complete!')
    except:
        connection.rollback()

def insert_song(song_name='', fgp=0):
    insert_query = INSERT_SONG % (song_name, fgp)
    print(insert_query)

    try:
        cur.execute(insert_query)
        connection.commit()
        print('Song inserted!')
    except:
        connection.rollback()

    print(cur.fetchall())

def test():
    #query = """CREATE TABLE vlad(name varchar(20) PRIMARY KEY)"""
    #cur.execute(query)
    var = 'true name'
    insert = 'INSERT INTO vlad(name) VALUES (\'{}\');'.format(var)
    print(insert)
    cur.execute('INSERT INTO vlad(name) VALUES (\'dsadsa\')')

    connection.commit()

connect()
#clear_database()
#setup()
test()
#insert_song('vlad did it!', True)

close_database()


