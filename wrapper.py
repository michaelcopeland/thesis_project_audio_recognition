import sys
import database as db

class Wrapper(object):

    def __init__(self, config, database_instance_or_connection):

        self.config = config
        # initialize database

        if self.config:
            
            # read config file
            self.host = config.get('host', {})
            self.user = config.get('user', {})
            self.pswd = config.get('passwd', {})
            self.db_name = config.get('db', {})
            self.port = config.get('port', {})
        
        else:
            print('Configuration file could not be found.')
            sys.exit(1)

    def info(self):
        return str(self.config)

    def connect_to_db(self):
        self.connection = db.connect()
        self.cursor = self.connection.cursor()