from mek_types.enums import InformationSize
from utils.functions import array_to_int, parse_scq

def file_ready_decode(elements: bytes):
    pass

def call_directory_decode(elements: str):
    elements_data = elements.split(" ")[:-1]
    ioa = array_to_int(elements_data[:InformationSize.IOA_SIZE])
    nof = array_to_int(elements_data[InformationSize.IOA_SIZE:InformationSize.IOA_SIZE + InformationSize.NOF_SIZE])
    nos = array_to_int(elements_data[InformationSize.IOA_SIZE + InformationSize.NOF_SIZE:InformationSize.IOA_SIZE + InformationSize.NOF_SIZE + InformationSize.NOS_SIZE])
    scq = array_to_int(elements_data[InformationSize.IOA_SIZE + InformationSize.NOF_SIZE + InformationSize.NOS_SIZE:InformationSize.IOA_SIZE + InformationSize.NOF_SIZE + InformationSize.NOS_SIZE + InformationSize.SCQ_SIZE])
    print(ioa, nof, nos, scq)
    print(elements)
    return ioa, nof, nos, scq
