from c104f.mek_types.enums import InformationSize
from c104f.utils.functions import array_to_int, get_elements_data

def nof_nos_qualifier_decode(elements_data, qualifier_size):
    ioa = array_to_int(elements_data[:InformationSize.IOA_SIZE])
    nof = array_to_int(elements_data[InformationSize.IOA_SIZE:InformationSize.IOA_SIZE + InformationSize.NOF_SIZE])
    nos = array_to_int(elements_data[
                           InformationSize.IOA_SIZE + InformationSize.NOF_SIZE:InformationSize.IOA_SIZE + InformationSize.NOF_SIZE + InformationSize.NOS_SIZE])
    qualifier = array_to_int(elements_data[InformationSize.IOA_SIZE + InformationSize.NOF_SIZE + InformationSize.NOS_SIZE:InformationSize.IOA_SIZE + InformationSize.NOF_SIZE + InformationSize.NOS_SIZE + qualifier_size])

    return ioa, nof, nos, qualifier


def file_ready_decode(elements: bytes):
    pass

def call_directory_decode(elements: str):
    elements_data = get_elements_data(elements)
    ioa, nof, nos, scq = nof_nos_qualifier_decode(elements_data, qualifier_size=InformationSize.SCQ_SIZE)
    print(ioa, nof, nos, scq)
    print(elements)
    return ioa, nof, nos, scq

def ack_file_decode(elements: str):
    elements_data = get_elements_data(elements)
    ioa, nof, nos, afq = nof_nos_qualifier_decode(elements_data, qualifier_size=InformationSize.AFQ_SIZE)
    print(ioa, nof, nos, afq)
    print(elements)

    return ioa, nof, nos, afq