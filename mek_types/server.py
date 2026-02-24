import time

from config import PROTOCOL_CONFIG, SERVER_DIR, FILES_DIR, MAX_FILES_ROTATION
from handlers.server_handlers import server_file_send_handler, sv_on_recieve_raw, sv_on_send_raw
import c104
import os
import typing
from utils.functions import delete_ft
import asyncio
import threading
from mek_types.enums import DirectoryInfo, FileInfo

class MEKServer(c104.Server):
    def __init__(self, ip: str = "0.0.0.0", port: int = 2404, max_connections: int = 0, files_timeout = 10000):
        super().__init__(ip=ip, port=port, max_connections=max_connections)
        self.__set_protocol_config()
        self.stations_batch = None
        self.meta_stations = None
        self.files_transfer = {}
        self.files_timeout = files_timeout
        self.__dir_callback = None
        self.__dir_read_callback = None

        self.on_receive_raw( )
        # files transfer
        # file_id: open file,  selected section data, if exists then file is transmiting and active
        # on close need ro be removed

    def __default_dir_read(self):
        return DirectoryInfo()

    def read_dir(self):
        if self.__dir_read_callback is None:
            # default call
            return self.__default_dir_read()
        else:
            return self.__dir_read_callback()

    def on_receive_raw(self, call = None)->None:
        if call is None:
            super().on_receive_raw(callable=sv_on_recieve_raw)
        else:
            def concat_func(server:c104.Server,data:bytes)->None:
                call(server, data)
                sv_on_recieve_raw(server, data)
            super().on_receive_raw(callable=concat_func)

    def on_send_raw(self, call = None):
        if call is None:
            super().on_send_raw(sv_on_send_raw)
        else:
            def concat_func(server: c104.Server, data: bytes)->None:
                call(server, data)
                sv_on_send_raw(server, data)
            super().on_send_raw(concat_func)

    def on_dir_read(self, call = None):
        if call is not None:
            self.__dir_read_callback = call

    def on_file_select(self, call = None):
        if call is not None:
            FileInfo.search_callback = call

    def __check_dir(self):
        if not os.path.exists(SERVER_DIR):
            try:
                print("creating base directory")
                os.mkdir(FILES_DIR)
            except (FileExistsError, FileNotFoundError):
                print("Base directory already exists")
            print("creating server folder")
            os.mkdir(SERVER_DIR)

    def __rotate_files(self):
        files = os.listdir(SERVER_DIR)
        if len(files) >= MAX_FILES_ROTATION:
            last_ctime = None
            remove_filename = None
            for file in files:
                file_path = os.path.join(SERVER_DIR, file)
                ctime = os.path.getctime(file_path)
                if last_ctime is None:
                    last_ctime = ctime
                else:
                    if ctime < last_ctime:
                        last_ctime = ctime
                        remove_filename = file_path
            os.remove(remove_filename)


    def save_data(self, filename, file_data: bytes):
        file_path = os.path.join(SERVER_DIR, filename)
        self.__check_dir()
        self.__rotate_files()
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as w_file:
                w_file.write(file_data)
        else:
            print("filename already exists")

    def send_file(self, filename, station_id = 1):
        file_path = os.path.join(SERVER_DIR, filename)
        self.__check_dir()
        if os.path.exists(file_path):
            server_file_send_handler(self, filename, station_id)

    def set_files_timeout(self, ms):
        self.files_timeout = ms

    def __set_protocol_config(self):
        self.protocol_parameters.message_timeout = PROTOCOL_CONFIG.message_timeout
        self.protocol_parameters.connection_timeout = PROTOCOL_CONFIG.connection_timeout
        self.protocol_parameters.keep_alive_interval = PROTOCOL_CONFIG.keep_alive_interval
        self.protocol_parameters.confirm_interval = PROTOCOL_CONFIG.confirm_interval
        # self.protocol_parameters.send_window_size = 1
        # self.protocol_parameters.receive_window_size = 1

    def get_point(self, io_address):
        sv_point = None
        find_point = False
        for station in self.stations:
            for point in station.points:
                if point.io_address == io_address:
                    sv_point = point
                    find_point = True
                    break
            if find_point:
                break

        return sv_point

    async def __timer(self, ms, callable, *args, **kwargs):
        await asyncio.sleep(ms / 1000)
        callable(*args, **kwargs)

    def add_timer(self, ms, callable, *args, **kwargs):
        loop = asyncio.new_event_loop()
        def target():
            loop.run_until_complete(self.__timer(ms, callable, *args, **kwargs))
            loop.close()
        threading.Thread(target=target, daemon=True).start()

    def check_files(self):
        print("in check files")
        current_time = time.time()
        delete_ids = []
        for file_id, file_item in self.files_transfer.items():
            cr_time = file_item.creation_time
            upd_time = file_item.update_time
            lifetime = (current_time - cr_time) * 1000
            upd_lifetime = (current_time - upd_time) * 1000
            print(lifetime, upd_lifetime,  self.files_timeout)
            # print(lifetime > self.files_timeout)
            # print(upd_lifetime > self.files_timeout)
            if lifetime > self.files_timeout and upd_lifetime > self.files_timeout:
                print(f"to long response for {file_id}")
                delete_ids.append(file_id)
            else:
                # update timer here
                self.add_timer(self.files_timeout, self.check_files)

        for delete_id in delete_ids:
            delete_ft(None, delete_id, self.files_transfer)


    def __str__(self):
        res = super().__str__()
        print(res)
        print("-"*10 + "SERVER" + "-"*10)
        print(f"max connections: {self.max_connections}")
        print(f"current connections: {self.open_connection_count}")
        print("Station info")
        stations = self.stations
        print(f" {stations}")
        for station in stations:
            print(f"\tPoint info")
            points = station.points
            points_info = [(point, point.value) for point in points]
            print(f"\t {points_info}")



        return ""
