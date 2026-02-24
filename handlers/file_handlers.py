import datetime
import time

import c104
from utils.parsers import call_directory_decode, ack_file_decode
from utils.functions import get_file_id, bytes_to_int_list, delete_ft, get_server_ft, get_file_info, get_zero_point, get_server
from mek_types.enums import SOF, SCQ, LSQ, CHS, AFQ, FileTransferInfo, FileInfo
from config import SERVER_DIR, SEGMENT_SIZE, SECTION_SIZE
import os

def server_file_receive_handler(server, type, data_dict: dict):
    common_address = data_dict.get("commonAddress")
    cot = data_dict.get('cot')
    station = server.get_station(common_address=common_address)
    if station:
        zero_point = get_zero_point(station)
        elements = data_dict.get("elements")
        print(type, data_dict)
        # call directory handle here
        if type == c104.Type.F_SC_NA_1:
            print("CALL DIRECTORY")
            # directory call here
            # get main info
            ioa, nof, nos, scq = call_directory_decode(elements)
            scq = SCQ(scq)
            # confirm file ready
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
            elif scq.isDeleteFile():
                pass



        elif type == c104.Type.F_AF_NA_1:
            print("CONFIRM FILE/SECTION")
            ioa, nof, nos, afq = ack_file_decode(elements)
            afq = AFQ(afq)
            sv_confirm_handler(zero_point, ioa, nof, nos, afq)
            # file or section acknowledgement
            ...
        else:
            print("Unexpected type")

def server_file_send_handler(server, filename, station_id):
    station = server.get_station(station_id)
    if station:
        file_id = get_file_id(filename)
        type = c104.Cot.SPONTANEOUS
        nos = 0
        zero_point = get_zero_point(station)
        sv_select_file_handler(zero_point, 0, file_id, nos, tr_type = type)

def sv_call_section_handler(zero_point, ioa, nof, nos):
    if ioa == 0:
        # main dir here
        ## send segments here
        zero_point.type = c104.Type.F_SG_NA_1
        file_info = get_file_info(zero_point, nof)
        if file_info:
            # file ready for transmition
            if file_info.section_id + 1 == nos:
                # correct selected section
                print(f"TRANSFERING {nos} / {file_info.max_sections} SECTION ...")
                segment_count = 0
                data_list = file_info.section
                print(len(data_list), file_info.section_chs)
                while segment_count*SEGMENT_SIZE < file_info.section_len:
                    segment_data = data_list[segment_count*SEGMENT_SIZE: (segment_count + 1)*SEGMENT_SIZE]
                    segment_info = c104.FileSegmentCall(nof = c104.Int16(nof), nos=c104.Uint8(nos), los=c104.Uint8(len(segment_data)), data=segment_data)
                    zero_point.info = segment_info
                    zero_point.transmit(c104.Cot.FILE_TRANSFER)
                    segment_count += 1

                ## if last segment call last segment call
                ## or if last segment/section of file call last file call
                zero_point.type = c104.Type.F_LS_NA_1
                print("SEND LAST SECTION CALL")
                lsq = LSQ()
                # if last section => last file
                if nos == file_info.max_sections:
                    #last section of file
                    print("last section of file")
                    lsq.setLastFile()
                    chs = file_info.get_full_chs()
                else:
                    print("will be next section")
                    lsq.setLastSection()
                    chs = file_info.section_chs

                # print(chs.chs, sum(data_list) % 256 )
                last_segment_info = c104.FileLastSegmentOrSectionCall(nof=c104.Int16(nof), nos=c104.Uint8(nos), lsq=c104.Uint8(lsq.lsq), chs=c104.Uint8(chs))
                zero_point.info = last_segment_info
                zero_point.transmit(c104.Cot.FILE_TRANSFER)
                print("TRANSMITING DONE")

def sv_select_file_handler(zero_point, ioa, nof, nos, tr_type = None):
    if ioa == 0:
        # from main dir
        file_info = FileInfo.from_nof(nof)
        file_is_found = False
        file_size = 0
        if file_info:
            # found
            ft_info = file_info.get_file_transfer_info()
            if ft_info:
                # can be selected
                file_is_found = True
                file_size = file_info.file_size
                server_ft = get_server_ft(zero_point)
                file_ft_info = server_ft.get(file_info.file_id)
                if file_ft_info:
                    file_is_found = False
                else:
                    server_ft[file_info.file_id] = ft_info

        zero_point.type = c104.Type.F_FR_NA_1
        print(file_size)
        file_ready_info = c104.FileReadyCall(nof=c104.Int16(nof), lof=c104.Uint32(file_size), positive=file_is_found)
        print(file_ready_info)
        zero_point.info = file_ready_info
        zero_point.transmit(cause=c104.Cot.FILE_TRANSFER if tr_type is None else tr_type)
        server = get_server(zero_point)
        server.add_timer(ms=server.files_timeout, callable=server.check_files)
        print("Called file timer")

        # file_names = os.listdir(SERVER_DIR) # directory info here
        # file_is_found = False
        # file_size = 0
        # for filename in file_names:
        #     file_id = get_file_id(filename)
        #     print(file_id, nof)
        #     if file_id == nof:
        #         # file is found
        #         file_is_found = True
        #         file_size = os.path.getsize(os.path.join(SERVER_DIR, filename))
        #         # check activation here and create new file_transfer
        #         server_ft = get_server_ft(zero_point)
        #         file_info = server_ft.get(file_id)
        #         if file_info:
        #             # already opened ( error )
        #             file_is_found = False
        #         else:
        #             print(f"OPEN FILE {file_id} FOR TRANSFER")
        #             file_bytes = open(os.path.join(SERVER_DIR, filename), "rb")
        #             sections = file_size // SECTION_SIZE
        #             if sections * SECTION_SIZE < file_size:
        #                 sections += 1
        #             file_info = FileTransferInfo(file = file_bytes, file_size = file_size, max_sections = sections, section_size=SECTION_SIZE)
        #             server_ft[file_id] = file_info
        #         break
        # # file ready ack
        # zero_point.type = c104.Type.F_FR_NA_1
        # print(file_size)
        # file_ready_info = c104.FileReadyCall(nof=c104.Int16(nof), lof=c104.Uint32(file_size), positive=file_is_found)
        # print(file_ready_info)
        # zero_point.info = file_ready_info
        # zero_point.transmit(cause = c104.Cot.FILE_TRANSFER if tr_type is None else tr_type)
        # server = get_server(zero_point)
        # server.add_timer(ms=server.files_timeout, callable=server.check_files)
        # print("Called file timer")
        # # from here need to timer response to close file if no responce for a long time

def sv_select_section_handler(zero_point, ioa, nof, nos):
    if ioa == 0:
        # file from main dir
        # get nof data
        # get nos
        ## slice data from nof
        file_info = get_file_info(zero_point, nof)
        file_info.update_time = time.time()
        if file_info:
            # transmit section ready
            section_id = nos - 1 # in prot from 1 in real from zero
            if SECTION_SIZE * section_id >= file_info.file_size:
                print("no such section")
            else:
                notReady = False
                result = file_info.prepare_section()
                if not result:
                    notReady = True
                zero_point.type = c104.Type.F_SR_NA_1
                section_ready_info = c104.FileSectionReadyCall(nof=c104.Int16(nof), nos=c104.Uint8(nos), lof=c104.Uint32(file_info.section_len), notReady=notReady)
                zero_point.info = section_ready_info
                zero_point.transmit(cause = c104.Cot.FILE_TRANSFER)
        else:
            print("File not selected error")

def sv_confirm_handler(zero_point, ioa, nof, nos, afq:AFQ):

    if afq.isFilePositive():
        print("FILE TRANSMITING SUCCESS")
        # remove file from file transfer section
        delete_ft(zero_point, nof)

    elif afq.isSectionPositive():
        print("SECTION TRANSMITING SUCCESS")
        # update section
        # update file_chs
        file_info = get_file_info(zero_point, nof)
        file_info.update_time = time.time()
        file_info.update_file_chs()
        file_info.next_section()
        sv_select_section_handler(zero_point, ioa, nof, nos+1)

    else:
        print(afq._value)
        if afq.isCHSError():
            if afq.isFileNegative():
                print("FILE CHS ERROR")
            elif afq.isSectionNegative():
                print("SECTION CHS ERROR")
        else:
            print("TRANSMITING ERROR")

def sv_dir_read_handler(zero_point, ioa, nof, nos):

    if ioa == 0:
        # main dir here
        server = get_server(zero_point)
        directory_info = server.read_dir() # server Callback here
        # file_names = os.listdir(SERVER_DIR)
        # prepare response for client
        scq = SCQ()
        scq.setSelectFile() # confirm select file

        # transmit confirmation ( if necessary )
        zero_point.type = c104.Type.F_SC_NA_1 # confirm zero type
        directory = c104.DirectoryCall(nof=c104.Int16(nof), nos=c104.UInt7(nos), scq=c104.UInt7(scq.scq))
        zero_point.info = directory
        zero_point.transmit(cause=c104.Cot.ACTIVATION_CON)


        # start transmiting file list
        zero_point.type = c104.Type.F_DR_TA_1
        for file_info in directory_info:
            file_id, file_size, file_ctime, is_active, is_directory = file_info.get_file_info()
            sof = SOF(0)
            if file_info == directory_info[-1]:
                sof.setIsLast()
            if is_directory:
                sof.setIsDirectory()
            if is_active:
                sof.setFileIsActive()

            print("TIME INFO")
            file_dir = c104.FileDirectoryCall(nof=c104.Int16(file_id), lof=c104.Uint32(file_size),
                                              sof=c104.Uint8(sof.sof),
                                              creationTime=datetime.datetime.fromtimestamp(file_ctime))
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