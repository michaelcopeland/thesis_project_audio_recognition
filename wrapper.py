import sys
from database import Database
from fingerprintWorker import Worker


class Wrapper(object):

    def __init__(self, config):

        self.config = config

        if self.config:

            # read config file
            db_params = config.get('database')
            grid_params = config.get('grid_settings')
            grid_paths = config.get('grid_paths')

            self.t_int = grid_params.get('time_interval', 100)
            self.f_int = grid_params.get('freq_interval', 100)
            self.t_tol = grid_params.get('time_tolerance', 30)
            self.f_tol = grid_params.get('freq_tolerance', 30)

            self.grid_in = grid_paths.get('files_in', '')
            self.grid_out = grid_paths.get('files_out', '')

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

    ### DB ###
    def config_info(self):
        s = 'Connected to host {}\n' \
            'Port {}\n' \
            'Database: {}\n'.format(self.host, self.port, self.db_name)
        print(s)

    def get_connection(self):
        self.wrapper_connection = self.db.connection

    def handle_db_reset(self):
        self.db.drop_all_tables()
        self.db.setup()

    ### landmark ###
    def handle_insert_songs(self, path, count):
        self.worker.fingerprint_songs(user_path=path, num_tracks=count)

    def handle_recognize_from_file(self, path, limit):
        sn, list_hash = self.worker.fingerprint_worker(path, limit=limit)
        matches = self.worker.fgp_db.get_matches(list_hash)
        result_track, matched_fam, res = self.worker.align_matches_weighted(matches)

        return result_track

    def handle_recognize_from_mic(self, limit):
        list_hash = self.worker.mic_recognize(limit=limit)
        matches = self.worker.fgp_db.get_matches(list_hash)
        result_track, matched_fam, res = self.worker.align_matches_weighted(matches)

        return res

    ### gridhash ###

    def set_attributes(self):
        self.worker.fgp_api.set_grid_attributes(self.t_int,
                                                self.f_int,
                                                self.t_tol,
                                                self.f_tol)

    def pretty_print_grid_settings(self):
        s = 'Grid hash settings:\n' \
            'Time interval: {}\n' \
            'Frequency interval: {}\n' \
            'Time tolerance: {}\n' \
            'Frequency tolerance: {}\n' \
            '\nFile source path: {}\n'\
            'GridHash destination path: {}'.format(self.t_int,
                                                   self.f_int,
                                                   self.t_tol,
                                                   self.f_tol,
                                                   self.grid_in,
                                                   self.grid_out)
        print(s)

    def handle_grid_export(self, count):
        self.set_attributes()

        files_in = self.grid_in
        files_out = self.grid_out

        self.worker.export_many(files_in, files_out, int(count))

    def handle_sim(self, prim):
        grid_folder = self.grid_out

        dir_map = self.worker.build_dir_map(grid_folder)
        li = []

        if prim not in dir_map.keys():
            print('{} does not have a gridHash\n')

        for tr in dir_map.keys():
            if tr != prim:
                sim = self.worker.compute_jaccard(prim, tr, grid_folder)
                token = (round(sim, 3), prim, tr)
                li.append(token)

        li.sort(key=lambda x: x[0], reverse=True)
        for elem in li:
            print(elem)

    def handle_list_folder_contents(self, switch=False):
        if not switch:
            dir_map = self.worker.build_dir_map(self.grid_out)
            print(self.grid_out, ' contains:')
        else:
            print(self.grid_in, ' contains:')
            dir_map = self.worker.build_dir_map(self.grid_in)

        for itm in dir_map.keys():
            print(itm)