from main import configure_client_server, sv_points_report_test
from mek_types.enums import FileInfo, DirectoryInfo
import json
import time
import random

def test_dir_read():
    # SELECT FROM BD COUND BE HERE
    random_files = ["test.txt"]
    file_info_list = []
    for i, rd_file in enumerate(random_files):
        rd_size = random.randint(10, 100)
        rd_file_id = i
        creation_time = random.randint(1000, 10000)
        file_info_list.append(FileInfo(filename=rd_file_id, file_id=rd_file_id, file_size=rd_size,
                                       creation_time=creation_time))

    # MUST RETURN DirectoryInfo type
    dir_info = DirectoryInfo(file_info_list)
    return dir_info


def search_select_file_test(name_id):
    # name_id === nof from MEK request === file_id
    test_dir = test_dir_read()
    file_info = test_dir.get_by_nof(name_id) # OR SELECT FROM DB CAN BE HERE
    if file_info:
        # ADD FILE BYTES HERE
        file_info.file_bytes = b"Hello World"

        # Or with FileInfo(filename=rd_file_id, file_id=rd_file_id, file_size=rd_size,
        #                                        creation_time=creation_time, file_bytes = file_bytes)
    # Must return FileInfo type
    return file_info





if __name__ == "__main__":
    # start settings
    stations = 1  # optochannels count
    start_station_address = 255
    start_client_address = 123
    server_id = 0

    # get client and server
    client, server = configure_client_server(stations=stations, start_client_address=123, start_station_address=255,
                                             server_id=server_id)

    station = server.get_station(common_address=start_station_address)
    # server.on_receive_raw(callable=sv_on_recieve_raw)
    server.set_files_timeout(ms=10000) # set timeout for file transfer / 10 s
    # set test points for monitor
    sv_points_report_test(server, points_number=10, start_point_ioa=2, report_ms=5000)
    # CALLBACK UPDATE HERE
    # ELSE BY DEFAULT
    server.on_dir_read(call=test_dir_read)
    server.on_file_select(call=search_select_file_test)

    print("START SERVER")
    server.start()
    print("SERVER RUNNING...")
    # save test file

    test_json = [1 for _ in range(10)]
    str_res = json.dumps(test_json)
    server.save_data("test_2.json", file_data=str_res.encode("utf-8"))





    file_init = False
    while True:
        if not file_init:
            # send file from server without request example
            print("Initialize file transfer")
            server.send_file(filename="test_2.json", station_id=255)
            # client can not accept file and file will be always open
            # timeout will close buffer for file if there was no response for a long time
            file_init = True