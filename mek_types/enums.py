from utils.functions import bytes_to_int_list

class InformationSize:
    IOA_SIZE = 3
    NOF_SIZE = 2
    NOS_SIZE = 1
    SCQ_SIZE = 1
    AFQ_SIZE = 1


# hex_data = {f'{i}': i for i in range(10)}
# for i, ch in enumerate(['a', 'b', 'c', 'd', 'e', 'f']):
#     hex_data[ch] = 10 + i

class Flag:

    def __init__(self, value = 0):
        self._value = value

    
    def _setNthBit(self, value, n):
        mask = 1 << n
        result = value | mask
        return result

    
    def _getNthBit(self, value, n):
        result = (value >> n) & 1
        return result

    
    def _rmNthBit(self, value, n):
        mask = ~(1 << n)
        result = value & mask
        return result

    
    def _getRValue(self, value):
        return (value & 0xf0) >> 4

    
    def _getLValue(self, value):
        return value & 0x0f

    
    def _setLeftValue(self, value, l_value):
        r_value = self._getRValue(value)
        res_value = r_value + l_value
        return res_value

    
    def _checkLeftValue(self, value, l_value):
        l_v = self._getLValue(value)
        return l_v == l_value

    
    def _setRightValue(self, value, r_value):
        left_value = self._getLValue(value)
        right_value = r_value << 4
        res_value = right_value + left_value

        return res_value


    def _checkRightValue(self, value, r_value):
        r_v = self._getRValue(value)
        return r_v == r_value

class SOF(Flag):

    def setIsLast(self):
        self._value = self._setNthBit(self._value, 5)

    def isLast(self):
        res = self._getNthBit(self._value, 5)
        return res == 1

    def setIsDirectory(self):
        self._value = self._setNthBit(self._value, 6)

    def isDirectory(self):
        res = self._getNthBit(self._value, 6)

        return res == 1

    def setFileIsActive(self):
        self._value = self._setNthBit(self._value, 7)

    def fileIsActive(self):
        res = self._getNthBit(self._value, 7)

        return res == 1

    def setStatus(self, status_value):
        if 0 >= status_value > 15:
            left_val = self._value >> 4
            right_val = status_value
            self._value = (left_val << 4) + right_val

    def getStatus(self):
        status = self._value & 0x0f

        return status

    @property
    def sof(self):
        return self._value

class SCQ(Flag):

    @property
    def scq(self):
        return self._value

    # def _setLeftValue(self, l_value):
    #     r_value = self._getRValue(self._value)
    #     self._value = r_value + l_value
    #
    # def _checkLeftValue(self, l_value):
    #     l_v = self._getLValue(self._value)
    #     return l_v == l_value
    #
    # def _setRightValue(self, r_value):
    #     left_value = self._getLValue(self._value)
    #     right_value = r_value << 4
    #     self._value = right_value + left_value
    #
    # def _checkRightValue(self, r_value):
    #     r_v = self._getRValue(self._value)
    #     return r_v == r_value

    def setDefaultCommand(self):
        self._value = self._getRValue(self._value)

    def isDefaultCommand(self):
        command = self._getLValue(self._value)
        return command == 0

    def setSelectFile(self):
        self._value = self._setLeftValue(self._value, 1)

    def isSelectFile(self):
        return self._checkLeftValue(self._value, 1)

    def setCallFile(self):
        self._value = self._setLeftValue(self._value, 2)

    def isCallFile(self):
        return self._checkLeftValue(self._value, 2)

    def setDeactivateFile(self):
        self._value = self._setLeftValue(self._value, 3)

    def isDeactivateFile(self):
        return self._checkLeftValue(self._value, 3)

    def setDeleteFile(self):
        self._value = self._setLeftValue(self._value, 4)

    def isDeleteFile(self):
        return self._checkLeftValue(self._value, 4)

    def setSelectSection(self):
        self._value = self._setLeftValue(self._value, 5)

    def isSelectSection(self):
        return self._checkLeftValue(self._value, 5)

    def setCallSection(self):
        self._value = self._setLeftValue(self._value, 6)

    def isCallSection(self):
        return self._checkLeftValue(self._value, 6)

    def setDeactivateSection(self):
        self._value = self._setLeftValue(self._value, 7)

    def isDeactivateSection(self):
        return self._checkLeftValue(self._value, 7)

    def setDefaultStatus(self):
        self._value = self._setRightValue(self._value, 0)

    def isDefaultStatus(self):
        return self._checkRightValue(self._value, 0)

    def setMemoryUnreached(self):
        self._value = self._setRightValue(self._value, 1)

    def isMemoryUnreached(self):
        return self._checkRightValue(self._value, 1)

    def setCHSError(self):
        self._value = self._setRightValue(self._value, 2)

    def isCHSError(self):
        return self._checkRightValue(self._value, 2)

    def setUnknownError(self):
        self._value = self._setRightValue(self._value, 3)

    def isUnknownError(self):
        return self._checkRightValue(self._value, 3)

    def setNoFilename(self):
        self._value = self._setRightValue(self._value, 4)

    def isNoFilename(self):
        return self._checkRightValue(self._value, 4)

    def setNoSectionName(self):
        self._value = self._setRightValue(self._value, 5)

    def isNoSectionName(self):
        return self._checkRightValue(self._value, 5)

class FRQ(Flag):

    @property
    def frq(self):
        return self._value

    def _getUint7(self):
        upd_value = self._rmNthBit(self._value, 7)
        return upd_value

    def setNegativeConfirm(self):
        self._value = self._setNthBit(self._value, 7)

    def isNegativeConfirm(self):
        res = self._getNthBit(self._value, 7)
        return res == 1

    def setFileReadyStatus(self, value):
        pass

    def getFileReadyStatus(self):
        return self._getUint7()

    @property
    def frq(self):
        return self._value

class SRQ(FRQ):

    def setSectionReadyStatus(self, value):
        self.setFileReadyStatus(value)

    def getSectionReadyStatus(self):
        return self.getFileReadyStatus()

    @property
    def srq(self):
        return self._value

class LSQ(Flag):

    def setLastFile(self):
        self._value = 1

    def isLastFile(self):
        return self._value == 1

    def setLastFileDeativation(self):
        self._value = 2

    def isLastFileDeactivation(self):
        return self._value == 2

    def setLastSection(self):
        self._value = 3

    def isLastSection(self):
        return self._value == 3

    def setLastSectionDeactivate(self):
        self._value = 4

    def isLastSectionDeactivate(self):
        return self._value == 4

    @property
    def lsq(self):
        return self._value

class AFQ(Flag):
    # def __init__(self, value = 0):
    #     super().__init__(value)
    #     print(self._getRValue(value))

    def setFilePositive(self):
        self._value = self._setLeftValue(self._value, 1)

    def isFilePositive(self):
        return self._checkLeftValue(self._value, 1)

    def setFileNegative(self):
        self._value = self._setLeftValue(self._value, 2)

    def isFileNegative(self):
        return self._checkLeftValue(self._value, 2)

    def setSectionPositive(self):
        self._value = self._setLeftValue(self._value, 3)

    def isSectionPositive(self):
        return self._checkLeftValue(self._value, 3)

    def setSectionNegative(self):
        self._value = self._setLeftValue(self._value, 4)

    def isSectionNegative(self):
        return self._checkLeftValue(self._value, 4)

    def setDefaultStatus(self):
        self._value = self._setRightValue(self._value, 0)

    def isDefaultStatus(self):
        return self._checkRightValue(self._value, 0)

    def setMemoryUnreached(self):
        self._value = self._setRightValue(self._value, 1)

    def isMemoryUnreached(self):
        return self._checkRightValue(self._value, 1)

    def setCHSError(self):
        self._value = self._setRightValue(self._value, 2)

    def isCHSError(self):
        return self._checkRightValue(self._value, 2)

    def setUnknownError(self):
        self._value = self._setRightValue(self._value, 3)

    def isUnknownError(self):
        return self._checkRightValue(self._value, 3)

    def setNoFilename(self):
        self._value = self._setRightValue(self._value, 4)

    def isNoFilename(self):
        return self._checkRightValue(self._value, 4)

    def setNoSectionName(self):
        self._value = self._setRightValue(self._value, 5)

    def isNoSectionName(self):
        return self._checkRightValue(self._value, 5)

class CHS:
    def __init__(self, data: list = None):

        self._value = 0
        if data is not None:
            self._value = sum(data) % 256


    @classmethod
    def from_chs(cls, chs):
        return cls([chs])

    @property
    def chs(self):
        return self._value

    def __add__(self, other):
        return CHS.from_chs(self.chs + other.chs)


class FileTransferInfo:
    def __init__(self, file=None, file_size = 0, section_id = 0, section = None, max_sections = 0, file_chs = CHS(), section_size = 5000):
        self.file_stream = file
        self.file_size_info = file_size
        self.section_id = section_id
        self.current_section = section
        self.section_data = None
        self.max_sections = max_sections
        self.file_check_sum = file_chs
        self.section_check_sum = CHS()
        self.section_size = section_size
        
    def prepare_section(self):
        result = True
        try:
            self.file_stream.seek(self.section_size * self.section_id)
            self.current_section = self.file_stream.read(self.section_size)
            self.section_data = bytes_to_int_list(self.current_section)
            self.section_check_sum = CHS(self.section_data)
        except Exception as e:
            print(f"ERROR IN PREPEARING {e}")
            result = False

        return result


    @property
    def file_size(self):
        return self.file_size_info

    @property
    def section_len(self):
        return len(self.section)

    @property
    def file(self):
        return self.file_stream

    @property
    def section(self):
        return self.section_data

    def update_file_chs(self):
        self.file_check_sum += self.section_check_sum
        self.section_check_sum = CHS()

    def get_full_chs(self):
        return (self.file_check_sum + self.section_check_sum).chs

    @property
    def file_chs(self):
        return self.file_check_sum.chs

    @property
    def section_chs(self):
        return self.section_check_sum.chs

    def next_section(self):
        self.section_id += 1