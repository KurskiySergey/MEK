from handlers.server_handlers import sv_on_recieve_raw
from main import configure_client_server
import json

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
    print("START SERVER")
    server.start()
    print("SERVER RUNNING...")
    # save test file

    test_json = [1 for _ in range(10)]
    str_res = json.dumps(test_json)
    server.save_data("test_2.json", file_data=str_res.encode("utf-8"))

    while True:
        ...