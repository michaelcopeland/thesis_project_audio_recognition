import sys
from database import Database
from fingerprintWorker import Worker


class Wrapper(object):

    def __init__(self, config):

        self.config = config
        # initialize database

        if self.config:
            
            # read config file
            db_params = config.get('database')
            self.host = db_params.get('host', '127.0.0.1')
            self.user = db_params.get('user', 'root')
            self.pswd = db_params.get('passwd', '')
            self.db_name = db_params.get('db', '')
            self.port = db_params.get('port', 3306)

            self.db = Database(self.host, self.port, self.user, self.pswd, self.db_name)
            self.worker = Worker(self.db)
        
        else:
            print('Configuration file could not be found.')
            sys.exit(1)

    def config_info(self):
        return str(self.config)

    def get_connection(self):
        self.wrapper_connection = self.db.connection

    def handle_db_reset(self):
        self.db.drop_all_tables()
        self.db.setup()

    def handle_insert_songs(self, path, count):
        self.worker.fingerprint_songs(user_path=path, num_tracks=count)
