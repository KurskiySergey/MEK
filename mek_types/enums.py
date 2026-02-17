class InformationSize:
    IOA_SIZE = 3
    NOF_SIZE = 2
    NOS_SIZE = 1
    SCQ_SIZE = 1


hex_data = {f'{i}': i for i in range(10)}
for i, ch in enumerate(['a', 'b', 'c', 'd', 'e', 'f']):
    hex_data[ch] = 10 + i

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
        return value & 0xf0

    
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
    def __init__(self, file_size):
        self._value = file_size % 256

    @property
    def chs(self):
        return self._value