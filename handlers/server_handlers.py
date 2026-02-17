import time

import c104
from handlers.file_handlers import server_file_receive_handler, server_file_send_handler

def sv_on_connect(server:c104.Server,ip:str)->bool:
    print(f"TRY TO CONNECT ON SERVER {ip}")
    return True

def sv_on_set_command_receive(point:c104.Point,previous_info:c104.Information,message:c104.IncomingMessage)->c104.ResponseState:
    print("Receive set point command")
    print(f"Previous value = {previous_info.value}")
    print(f"Next value = {point.value}")
    return c104.ResponseState.SUCCESS

def sv_on_send_raw(server: c104.Server, data: bytes)->None:
    print("<--| {1} [{0}] | SERVER {2}:{3}".format(data.hex(), c104.explain_bytes(apdu=data), server.ip, server.port))


def sv_on_recieve_raw(server:c104.Server,data:bytes)->None:
    explain_dict = c104.explain_bytes_dict(data)
    type = explain_dict.get("type")

    if isinstance(type, c104.Type):
        if c104.Type.F_FR_NA_1.value <= type.value <= c104.Type.F_DR_TA_1.value:
            print(data)
            server_file_receive_handler(server, type, explain_dict)

    # if type == c104.Type.F_SC_NA_1:
    #     print("CALL DIRECTORY")
    #     print(explain_dict)
    #     common_address = explain_dict.get("commonAddress")
    #     originatorAddress = explain_dict.get('originatorAddress')
    #     station = server.get_station(common_address=common_address)
    #     zero_point = station.get_point(io_address=0)
    #     if zero_point is None:
    #         zero_point = station.add_point(io_address=0, type=c104.Type.F_SC_NA_1)
    #     zero_point.type = c104.Type.F_SC_NA_1
    #     directory = c104.DirectoryCall(nof=c104.Int16(0), nos=c104.UInt7(0), scq=c104.UInt7(1))
    #     zero_point.info = directory
    #     zero_point.transmit(cause=c104.Cot.ACTIVATION_CON)
    #     zero_point.type = c104.Type.F_DR_TA_1
    #     # file_dir = c104.FileDirectoryCall(nof=c104.Int16(0), lof=c104.Uint32(1), sof=c104.Uint8(0x60))
    #     # zero_point.info = file_dir
    #     # zero_point.transmit(cause=c104.Cot.REQUEST)
    #     file_dir = c104.FileDirectoryCall(nof=c104.Int16(1), lof=c104.Uint32(0), sof=c104.Uint8(0x10))
    #     zero_point.info = file_dir
    #     zero_point.transmit(cause=c104.Cot.REQUEST)
    #
    #     # terminate transmition
    #     # zero_point.transmit(cause=c104.Cot.ACTIVATION_TERMINATION)
    #     time.sleep(0.5)
    #     zero_point.type = c104.Type.F_SC_NA_1
    #     # directory = c104.DirectoryCall(nof=c104.Int16(0), nos=c104.UInt7(0), scq=c104.UInt7(1))
    #     zero_point.info = directory
    #     zero_point.transmit(cause=c104.Cot.ACTIVATION_TERMINATION)


    # print(type(c104.explain_bytes(data)))
    # print(c104.explain_bytes_dict(data))
    # print(c104.explain_bytes(data))