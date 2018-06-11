import sys
#from fingerprintWorker import fingerprint_songs, reset_database


class Wrapper(object):

    def __init__(self, config):

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
