import c104
import time

# RUNNING TESTS
def client_test_run():
    client = c104.Client()
    start_t = time.time()
    print("Client start")
    client.start()
    client.stop()
    stop_t = time.time()
    print(f"Client stoped in {stop_t - start_t} sec")


def client_connection_test():
    client = c104.Client()
    connection = client.add_connection(ip="localhost", port=2404)
    print("Add new connection")
    print(connection)
    get_con = client.get_connection(ip="localhost", port=2404)
    print("Get existing connection")
    print(get_con)
    print("Disconnect all connections")
    client.disconnect_all()
    check_con = client.get_connection(ip="localhost", port=2404)
    print(check_con)
    print("client has connections")
    print(client.has_connections)
    print("Client has active connections")
    print(client.has_active_connections)
    print("Client has open connections")
    print(client.has_open_connections)
    print("originator adress")
    print(client.originator_address)
    print("Add station to connection")
    connection.add_station(common_address=15)

    print("Try to sync time")
    if not connection.clock_sync(common_address=15):
        print("Cannot send clock sync command")
    else:
        print("Sinc time")

    if not connection.counter_interrogation(common_address=47, cause=c104.Cot.ACTIVATION,
                                            qualifier=c104.Rqt.GENERAL, freeze=c104.Frz.COUNTER_RESET):
        print("Cannot send counter interrogation command")
    else:
        print("Send counter interrogation command")

    print("Try to connect to station")
    connection.connect()
    print("Try to get station")
    station = connection.get_station(common_address=15)
    print(station)

    print("Send test command")
    print(connection.test(common_address=15))




if __name__ == "__main__":
    client_test_run()
    client_connection_test()
