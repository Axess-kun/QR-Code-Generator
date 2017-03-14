from bisect import bisect_left
from src.BitBuffer import BitBuffer
from src.constants import *
from src.rsBlocks import *
from src.gf256 import Polynomial
from src.look_up_table import CapacityTable, GeneratorPolynomial
from src.module_placement import Module

"""
### create() function ###
Create QR Code

Parameters
- dataString: str
    String data to encode.
- ecLevel: constants.ErrorCorrection
    Error correction level.
    If None is given, automatically encode at level H.
- version: int
    Version to encode.
    If None is given, automatically detect best version to fit data.


### areAllCharKanji() function ###
Check all characters are Kanji or not.

Return "True" if all characters are multibyte Kanji on Rikai's Shift JIS Kanji Code Table.
Return "False" if any character is NOT Kanji found.

Parameters
- dataString: str
    String data to encode.


### structFinalMsg() function ###
Calculate, Encode, Interleave datas and construct encoded data.

Parameters
- buffer: BitBuffer
    Data buffer after padded with 0xEC and 0x11.
- blockInfos: list
    List of RSBlock.
"""


####################################################################################################
# Create QR Code
####################################################################################################
def create(dataString: str, ecLevel: ErrorCorrection = None, version: int = None):
    #------------------------------
    # Auto Error Correction Level
    #------------------------------
    if ecLevel is None:
        ecLevel = ErrorCorrection.H

    #------------------------------
    # Check Version
    #------------------------------
    if version is not None and (version < 1 or version > 40):
        raise ValueError("Wrong version!!")

    #------------------------------
    # Create Bit Buffer
    #------------------------------
    buff = BitBuffer()

    # Find string length
    strlen = len(dataString)
    if strlen == 0:
        raise ValueError("Try to encode 0 byte data")

    #------------------------------
    # Find mode to encode by check data type
    #------------------------------
    mode = 0
    # * NOT use isdigit() or isnumeric() or isdecimal() for checking Numeric.
    #   reason is written in README.md
    if Numeric_Regex.match(dataString) is not None:
        mode = int(ModeIndicator.NUMERIC)
    elif AlphaNum_Regex.match(dataString) is not None:
        mode = int(ModeIndicator.ALPHANUM)
    elif areAllCharKanji(dataString):
        mode = int(ModeIndicator.KANJI)
    else:
        mode = int(ModeIndicator.BYTE)

    #------------------------------
    # Find best fit version or check specific version
    #------------------------------
    # Create list of capacities in every mode by version from error correction level.
    listByVersion = [CapacityTable[i] for i in range(int(ecLevel), len(CapacityTable), 4)]

    # Create capacity list in specific mode
    capacityList = []
    if mode == int(ModeIndicator.NUMERIC):
        capacityList = list(map(lambda x: x[0], listByVersion))
    elif mode == int(ModeIndicator.ALPHANUM):
        capacityList = list(map(lambda x: x[1], listByVersion))
    elif mode == int(ModeIndicator.BYTE):
        capacityList = list(map(lambda x: x[2], listByVersion))
    else:
        capacityList = list(map(lambda x: x[3], listByVersion))

    # If version is not given.
    if version is None:
        # Get version by searching index to insert data.
        version = bisect_left(capacityList, len(dataString)) + 1

        # End of list. Not found suitable one.
        if version > 40:
            raise OverflowError("Data Overflow!")

    # Else, check data capacity
    else:
        if strlen > capacityList[version - 1]:
            raise OverflowError("Data Overflow! Data length = {0}, Capacity = {1}".format(strlen, capacityList[version - 1]))

    # Clear memory.
    del capacityList, listByVersion

    #------------------------------
    # Pre-encode Data
    #------------------------------
    # Mode Indicator
    buff.put((1 << mode), 4)

    # Character Count Indicator
    charin = 0
    if version <= 9:
        charin = EncodeSize_S[mode]
    elif version <= 26:
        charin = EncodeSize_M[mode]
    else:
        charin = EncodeSize_L[mode]
    buff.put(strlen, charin)

    # Clear memory.
    del strlen, charin
    
    #------------------------------
    # Encode Data
    #------------------------------
    # Numeric
    if mode == int(ModeIndicator.NUMERIC):
        for i in range(0, len(dataString), 3):
            # Data to convert
            numStr = dataString[i:i+3]
            # Put into buffer.
            buff.put(int(numStr), NumericLength[len(numStr)])

        # Clear memory.
        del numStr

    # Alphanumeric
    elif mode == int(ModeIndicator.ALPHANUM):
        # Loop for every 2 characters.
        for i in range(0, len(dataString), 2):
            # substr every 2 positions.
            char = dataString[i:i+2]

            # Check length
            # 2 characters
            if len(char) > 1:
                # Get numeric representation these 2 characters & calculate.
                num = AlphaNum.find(char[0]) * 45 + AlphaNum.find(char[1])
                # Put into buffer.
                buff.put(num, 11)
            # 1 character
            else:
                # Get numeric representation that character.
                num = AlphaNum.find(char[0])
                # Put into buffer.
                buff.put(num, 6)

        # Clear memory.
        del char, num

    # Byte
    elif mode == int(ModeIndicator.BYTE):
        charNums = []
        # Convert string to UTF-8 (make sure that this data can be encoded for QR).
        utf8 = dataString.encode("utf-8")

        # Store in list
        for char in utf8:
            charNums.append(char)

        # Put each character for 1 byte one-by-one.
        for c in charNums:
            # Put into buffer.
            buff.put(c, 8)

        # Clear memory
        del c, char, charNums, utf8

    # Kanji
    else:
        for i in range(len(dataString)):
            # Convert to Shift-JIS
            encodedChar = dataString[i].encode("shift-jis")
            # Get HEX value as string.
            encodedChar = encodedChar.hex()

            # Convert from string to number.
            num = (HexNum.find(encodedChar[0]) << 12 |
                    HexNum.find(encodedChar[1]) << 8 |
                    HexNum.find(encodedChar[2]) << 4 |
                    HexNum.find(encodedChar[3]))
        
            # In ranges 0x8140 to 0x9FFC
            if (num >= 0x8140 and num <= 0x9FFC):
                num -= 0x8140
            # In ranges 0xE040 to 0xEBBF
            elif (num >= 0xE040 and num <= 0xEBBF):
                num -= 0xC140

            # Most significant byte
            MSB = ((num >> 8) & 0xFF)
            # Least significant byte
            LSB = (num & 0xFF)

            # Calculate.
            num = (MSB * 0xC0) + LSB
            # Put into buffer.
            buff.put(num, 13)

        # Clear memory.
        del encodedChar, num, MSB, LSB

    # Clear memory.
    del mode
    
    #------------------------------
    # Determine the Required Number of Bits for this QR Code
    #------------------------------
    blocks = blockInfo(version, ecLevel)
    maxbit = 0
    for i in range(len(blocks)):
        maxbit += blocks[i].noDataCodeword * 8
    if len(buff) > maxbit:
        raise MemoryError("Capacity Overflow")
    
    #------------------------------
    # Add a Terminator
    #------------------------------
    if len(buff) < maxbit:
        diff = maxbit - len(buff)
        if diff >= 4:
            buff.put(0, 4)
        else:
            buff.put(0, diff)

    #------------------------------
    # Add More 0s to Make the Length a Multiple of 8
    #------------------------------
    remain = len(buff) % 8
    if remain != 0:
        buff.put(0, 8 - remain)

    # Clear memory.
    del remain

    #------------------------------
    # Add Pad Bytes if the String is Still too Short
    #------------------------------
    diff = maxbit - len(buff)
    if diff > 0:
        fill = [0b11101100, 0b00010001] # 236 (0xEC) and 17 (0x11), respectively
        for i in range(diff // 8):
            buff.put(fill[i % 2], 8)

    # Clear memory.
    del maxbit, diff, i

    #------------------------------
    # Error Correction Coding & Structure Final Message
    #------------------------------
    msg = structFinalMsg(buff, blocks)

    # Clear memory.
    del buff, blocks

    #------------------------------
    # Add Remainder Bits if Necessary
    #------------------------------
    if RemainderBits[version - 1] > 0:
        msg.put(0, RemainderBits[version - 1])

    #------------------------------
    # Create
    #------------------------------
    Module(msg, ecLevel, version)


    ## Debug
    #try:
    #    input("Press enter to continue")
    #except SyntaxError:
    #    pass


####################################################################################################
# Check all string are Kanji character or not
#
# Return "True" if all characters are multibyte Kanji on Rikai's Shift JIS Kanji Code Table
# Return "False" if contain Non-Kanji at least 1 character
####################################################################################################
def areAllCharKanji(dataString: str):
    for i in range(len(dataString)):
        encodedChar = b''
        # Try to encode to Shift-JIS
        try:
            encodedChar = dataString[i].encode("shift-jis")
        # Can't encode
        except UnicodeEncodeError:
            return False

        # Get HEX value as string
        encodedChar = encodedChar.hex()

        # Check Length
        if len(encodedChar) != 4:
            return False

        # Convert from string to number
        num = (HexNum.find(encodedChar[0]) << 12 |
                HexNum.find(encodedChar[1]) << 8 |
                HexNum.find(encodedChar[2]) << 4 |
                HexNum.find(encodedChar[3]))
        
        # In ranges 0x8140 to 0x9FFC and 0xE040 to 0xEBBF
        if (num >= 0x8140 and num <= 0x9FFC) or (num >= 0xE040 and num <= 0xEBBF):
            # OK
            continue
        else:
            return False

    # All are Kanji
    return True


####################################################################################################
# EC Coding for each block & Create final sequence
####################################################################################################
def structFinalMsg(buffer: BitBuffer, blockInfos: list):
    # Prepare for 2D Table
    maxDataCount = 0
    maxEcCount = 0
    dataTable = [0] * len(blockInfos)
    ecTable = [0] * len(blockInfos)

    # Count for index in buffer
    totalDataCount = 0

    # Calculate EC codewords, then fill data & ec table
    for block in range(len(blockInfos)):
        noDataCodeword = blockInfos[block].noDataCodeword
        noEcCodeword = blockInfos[block].noEcCodeword

        # Find max column of table
        maxDataCount = max(maxDataCount, noDataCodeword)
        maxEcCount = max(maxEcCount, noEcCodeword)

        # Copy 'Data' to table
        dataTable[block] = buffer.buffer[totalDataCount : totalDataCount + noDataCodeword]
        totalDataCount += noDataCodeword
        
        # EC Coding
        msg = Polynomial(dataTable[block][:], noEcCodeword) # Shifted message

        # Use Look Up Table for speed run
        if noEcCodeword in GeneratorPolynomial:
            gen = Polynomial(GeneratorPolynomial[noEcCodeword])
        else:
            gen = Polynomial.getGenerator(noEcCodeword)
        ecCodeword = msg % gen

        # Copy 'EC Codeword' to table
        ecTable[block] = ecCodeword[:]

    #------------------------------
    # Interleave the Data Codewords & Error Correction Codewords
    #------------------------------
    interleaved = []

    # Data Codewords
    for column in range(maxDataCount):
        for block in range(len(blockInfos)):
            # If not null
            if column < len(dataTable[block]):
                interleaved.append(dataTable[block][column])

    # Error Correction Codewords
    for column in range(maxEcCount):
        for block in range(len(blockInfos)):
            # If not null
            if column < len(ecTable[block]):
                interleaved.append(ecTable[block][column])

    # Output
    output = BitBuffer()
    output.copyList(interleaved)
    return output