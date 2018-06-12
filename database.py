import MySQLdb as mysql

USER = 'root'
USER_HOST = '127.0.0.1'
USER_PORT = 3306

FINGERPRINTS_TABLE = 'fingerprints'
SONGS_TABLE = 'songs'

FINGERPRINT_FIELD_ID = 'id'
FINGERPRINT_FIELD_HASHKEY = 'hash_key'
FINGERPRINT_FIELD_SONGNAME = 'song_name'
FINGERPRINT_FIELD_TIMEOFFSET = 'time_offset'

SONGS_FIELD_SONG_ID = 'song_id'
SONGS_FIELD_SONG_NAME = 'song_name'
SONGS_FIELD_FINGERPRINTED = 'is_fingerprinted'

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


class Database(object):

    def __init__(self, host, port, user, pswd, db_name):
        self.host = host
        self.port = port
        self.user = user
        self.pswd = pswd
        self.db_name = db_name

        self.connection = self.connect()
        self.cur = self.connection.cursor()
        # ensure large buffer size
        self.cur.execute('set global max_allowed_packet=67108864')

    def connect(self):
        db = mysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.pswd,
            db=self.db_name)
        print('Connected to database!')
        return db

    def close_database(self):
        self.connection.close()
        print('Connection closed.')

    def drop_all_tables(self):
        try:
            self.cur.execute(DROP_FINGERPRINTS)
            self.cur.execute(DROP_SONGS)
            self.connection.commit()
            print('Database cleared!')
        except:
            self.connection.rollback()

    def setup(self):
        """Creates datablase tables"""
        try:
            self.cur.execute(CREATE_SONGS_TABLE)
            print('Created songs table.')
            self.cur.execute(CREATE_FINGERPRINTS_TABLE)
            print('Created fingerprints table.')
            self.connection.commit()
            print('Setup complete!')
        except:
            print('Failed to setup tables.')
            self.connection.rollback()

    def insert_song(self, song_name='', fgp=0):
        insert_query = INSERT_SONG % (song_name, fgp)
        insert_query.encode('utf-8')

        try:
            self.cur.execute(insert_query)
            self.connection.commit()
            print('Inserted song: {}'.format(song_name))
            return True
        except:
            self.connection.rollback()
            print('Could not insert {}'.format(song_name))
            print('Title may be over 150 chars long, or there are special characters in the string')
            return False

    def insert_fingerprint(self, hashkey, song_name, time_offset):
        """
        Inserts a fingerprint in the database.

        There can be duplicate fingerprints.
        """
        insert_query = INSERT_FINGERPRINT % (hashkey, song_name, time_offset)
        insert_query.encode('utf-8')

        try:
            self.cur.execute(insert_query)
            self.connection.commit()
            # print('Fingerprint inserted!')
        except:
            self.connection.rollback()

    def dump_fingerprints(self, formatted_list):
        """Receives a list of fingerprints to insert to the database
        The row look like: hashkey, name of song, time offset
        """
        dump_insert = INSERT_FINGERPRINT_DUMP

        num_elem = len(formatted_list)
        dump_insert = dump_insert % ', '.join(['%s'] * num_elem)

        try:
            self.connection.ping()
            self.cur.execute(dump_insert, formatted_list)
            self.connection.commit()
        #print('dump successful!')
            return True
        except:
            self.connection.rollback()
            print('Dumping fingerprints failed')
            return False

    def delete_fgp_by_song(self, list_song_n):
        """Deletes fingerprints for each song in the parameter list of song

        Attribute:
            list_song_n - list of songs for which to delete fingerprints
        """
        songs = ', '.join(str('\'' + x + '\'') for x in list_song_n)

        delete_statement = DELETE_FINGERPRINTS % songs

        if songs is not '':
            try:
                print('Deleting fingerprint for:\n {}'.format(songs))
                self.cur.execute(delete_statement)
                self.connection.commit()
            except:
                self.connection.rollback()
                print('Could not delete fingerprints')
                return
            print('Deletion successful!')

        else:
            print('Deletion failed: no songs in list')

    def delete_songs(self, list_song_n):
        """Deletes songs from the database

        Attributes:
             list_song_n - a list of song names to remove from database
        """
        songs = ', '.join(str('\'' + x + '\'') for x in list_song_n)

        delete_statement = DELETE_SONGS % songs

        if songs is not '':
            try:
                print('Deleting songs:\n {}'.format(songs))
                self.cur.execute(delete_statement)
                self.connection.commit()
            except:
                self.connection.rollback()
                print('Could not delete songs')
                return
            print('Deletion successful!')

    def update_is_fingerprinted(self, list_song_n, is_fingerprinted):
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
                self.cur.execute(update_statement)
                self.connection.commit()
            except:
                self.connection.rollback()
                print('Update failed: is_fingerprinted status could not be written')
                return
            print('Success!')
        else:
            print('Update failed: No songs in list')

    def get_songs_by_fgp_status(self, is_fgp=0):
        """Retrieves song names based on the is_fingerprinted value

        Attributes:
            is_fgp - 0 not fingerprinted, 1 is fingerprinted

        Return:
            res_list - a list of song names
        """
        select_query = SELECT_SONG_BY_FGP % is_fgp

        try:
            print('Retrieving songs with is_fingeprinted={}'.format(is_fgp))
            self.cur.execute(select_query)
            self.connection.commit()

            result = []
            for res in self.cur:
                result.append(res)
            return result
            #print('Success!')
        except:
            self.connection.rollback()
            print('Songs could not be retrieved')

    def get_song_by_name(self, song_name):
        """Checks if a song name is available in the database.

        Attributes:
            song_name - name of song to query

        Returns:
            True, song name, 1 - if song is found
            False, empty string, 0 - if song is not found
        """
        select_query = SELECT_SONG_NAME % song_name

        song_id = 0
        song_name = ''
        is_fingerprinted = 0

        try:
            self.cur.execute(select_query)
            self.connection.commit()
        except:
            print('Error in get_song_by_name')
            self.connection.rollback()

        for id, name, is_fgp in self.cur:
            song_id = id
            song_name = name
            is_fingerprinted = is_fgp

        if song_id is 0 and song_name == '':
            song_name = 'No results found'
            return False, song_id, song_name, is_fingerprinted

        return True, song_id, song_name, is_fingerprinted

    def query_all_fingerprints(self):
        """
        Returns song name, hash key, time offset
        of all items in the fingerprints table
        """
        try:
            self.cur.execute(SELECT_ALL)
            self.connection.commit()

            for s_name, h_key, t_offset in self.cur:
                yield (s_name, h_key, t_offset)

        except:
            print('Error query_all_fingerprints')
            self.connection.rollback()

    def query(self, hashkey=None):
        """
        Return all tuples associated with hash.
        If hash is None, returns empty list.
        """

        if hashkey is None:
            return []
        else:
            print('Querying for ', hashkey)
            select_query = SELECT % hashkey

        self.cur.execute(select_query)
        self.connection.commit()
        for s_name, offset in self.cur:
            # print(s_name, offset)
            yield (s_name, offset)

    def get_matches(self, list_of_hashes):
        """Receives a list of SHA1 hash digests. Queries the database and returns
        a generator object of matching songs and their time index precision."""
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

        self.cur.execute(query_matches, values)

        for hash_k, song_name, time_offset in self.cur:
            # print('result: ', hash_k, song_name, time_offset)
            yield (song_name, time_offset - map[hash_k])
