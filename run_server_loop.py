from handlers.server_handlers import sv_on_recieve_raw
from main import configure_client_server
import json
import time

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
    server.on_receive_raw(callable=sv_on_recieve_raw)
    server.set_files_timeout(ms=10000) # set timeout for file transfer / 10 s
    print("START SERVER")
    server.start()
    print("SERVER RUNNING...")
    # save test file

    test_json = [1 for _ in range(10)]
    str_res = json.dumps(test_json)
    server.save_data("test_2.json", file_data=str_res.encode("utf-8"))

    file_init = False
    while True:
        time.sleep(10)
        if not file_init:
            # send file from server without request example
            print("Initialize file transfer")
            server.send_file(filename="test_2.json", station_id=255)
            # client can not accept file and file will be always open
            # timeout will close buffer for file if there was no response for a long time
            file_init = True