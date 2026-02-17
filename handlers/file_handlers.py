import c104
from utils.parsers import call_directory_decode
from utils.functions import get_file_id
from mek_types.enums import SOF, SCQ, LSQ, CHS
from config import SERVER_DIR
import os

def server_file_receive_handler(server, type, data_dict: dict):
    common_address = data_dict.get("commonAddress")
    cot = data_dict.get('cot')
    station = server.get_station(common_address=common_address)
    zero_point = station.get_point(io_address=0)
    if zero_point is None:
        zero_point = station.add_point(io_address=0, type=c104.Type.F_AF_NA_1)
    elements = data_dict.get("elements")
    print(type, data_dict)
    if type == c104.Type.F_SC_NA_1:
        print("CALL DIRECTORY")
        # directory call here
        # get main info
        ioa, nof, nos, scq = call_directory_decode(elements)
        scq = SCQ(scq)
        if scq.isSelectFile():
            # file call here
            if cot == c104.Cot.REQUEST:
                # directory list
                sv_dir_read_handler(zero_point, ioa, nof, nos)
            elif cot == c104.Cot.FILE_TRANSFER:
                # file select here
                sv_select_file_handler(zero_point, ioa, nof, nos)
        elif scq.isCallFile():
            if cot == c104.Cot.FILE_TRANSFER:
                sv_call_file_handler(zero_point, ioa, nof, nos)

        elif scq.isCallSection():
            if cot == c104.Cot.FILE_TRANSFER:
                sv_call_section_handler(zero_point, ioa, nof, nos)

        elif scq.isSelectSection():
            if cot == c104.Cot.FILE_TRANSFER:
                # file section select here
                sv_select_section_handler(zero_point, ioa, nof, nos)



    elif type == c104.Type.F_AF_NA_1:
        print("CONFIRM FILE/SECTION")
        zero_point.type = c104.Type.F_AF_NA_1
        # file or section acknowledgement
        ...
    else:
        print("Unexpected type")


def server_file_send_handler():
    pass

def sv_call_section_handler(zero_point, ioa, nof, nos):
    if ioa == 0:
        # main dir here
        ## send segments here
        zero_point.type = c104.Type.F_SG_NA_1
        test_data = [1 for i in range(250)]
        split_size = 10
        segment_count = 0
        while segment_count*split_size < 250:
            segment_data = test_data[segment_count*split_size: (segment_count + 1)*split_size]
            segment_info = c104.FileSegmentCall(nof = c104.Int16(nof), nos=c104.Uint8(nos), los=c104.Uint8(split_size), data=segment_data)
            zero_point.info = segment_info
            zero_point.transmit(c104.Cot.FILE_TRANSFER)
            segment_count += 1


        ## if last segment call last segment call
        ## or if last segment/section of file call last file call
        zero_point.type = c104.Type.F_LS_NA_1
        lsq = LSQ()
        lsq.setLastFile()
        chs = CHS(sum(test_data))
        last_segment_info = c104.FileLastSegmentOrSectionCall(nof=c104.Int16(nof), nos=c104.Uint8(nos), lsq=c104.Uint8(lsq.lsq), chs=c104.Uint8(chs.chs))
        zero_point.info = last_segment_info
        zero_point.transmit(c104.Cot.FILE_TRANSFER)

def sv_select_file_handler(zero_point, ioa, nof, nos):
    if ioa == 0:
        # from main dir
        file_names = os.listdir(SERVER_DIR)
        file_is_found = False
        file_size = 0
        for filename in file_names:
            file_id = get_file_id(filename)
            print(file_id, nof)
            if file_id == nof:
                # file is found
                file_is_found = True
                file_size = os.path.getsize(os.path.join(SERVER_DIR, filename))
                break
        # file ready ack
        zero_point.type = c104.Type.F_FR_NA_1
        print(file_size)
        file_ready_info = c104.FileReadyCall(nof=c104.Int16(nof), lof=c104.Uint32(file_size), positive=file_is_found)
        print(file_ready_info)
        zero_point.info = file_ready_info
        zero_point.transmit(cause = c104.Cot.FILE_TRANSFER)

def sv_select_section_handler(zero_point, ioa, nof, nos):
    if ioa == 0:
        # file from main dir
        # get nof data
        # get nos
        ## slice data from nof
        ...
        # transmit section ready
        zero_point.type = c104.Type.F_SR_NA_1
        section_ready_info = c104.FileSectionReadyCall(nof=c104.Int16(nof), nos=c104.Uint8(nos), lof=c104.Uint32(250), notReady=False)
        zero_point.info = section_ready_info
        zero_point.transmit(cause = c104.Cot.FILE_TRANSFER)



def sv_dir_read_handler(zero_point, ioa, nof, nos):

    if ioa == 0:
        # main dir here
        file_names = os.listdir(SERVER_DIR)
        scq = SCQ()
        scq.setCallFile()
        zero_point.type = c104.Type.F_SC_NA_1
        directory = c104.DirectoryCall(nof=c104.Int16(nof), nos=c104.UInt7(nos), scq=c104.UInt7(scq.scq))
        zero_point.info = directory
        zero_point.transmit(cause=c104.Cot.ACTIVATION_CON)

        zero_point.type = c104.Type.F_DR_TA_1
        for filename in file_names:
            # transmit files
            file_path = os.path.join(SERVER_DIR, filename)
            file_id = get_file_id(filename)
            file_size = os.path.getsize(file_path)

            sof = SOF(0)
            if filename == file_names[-1]:
                sof.setIsLast()
            if os.path.isdir(filename):
                sof.setIsDirectory()

            file_dir = c104.FileDirectoryCall(nof=c104.Int16(file_id), lof=c104.Uint32(file_size),
                                              sof=c104.Uint8(sof.sof))
            zero_point.info = file_dir
            zero_point.transmit(cause=c104.Cot.REQUEST)




        # terminate conn
        zero_point.type = c104.Type.F_SC_NA_1
        zero_point.info = directory
        zero_point.transmit(cause=c104.Cot.ACTIVATION_TERMINATION)

def sv_call_file_handler(zero_point, ioa, nof, nos):
    if ioa == 0:
        #main dir
        sv_select_section_handler(zero_point, ioa, nof, nos)