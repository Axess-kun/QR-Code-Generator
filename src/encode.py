from src.BitBuffer import BitBuffer
from src.enums import *
from src.blocks import *
from src.gf256 import Polynomial
from src.lut import *
from src.module_placement import *

#----------
# EC Coding for each block & Create final sequence
#----------
def structFinalMsg(buffer: BitBuffer, blockInfos: RSBlock):
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



# Return "True" if all characters is multibyte Kanji on Rikai's Shift JIS Kanji Code Table
# Return "False" if contain Non-Kanji at least 1 character
def checkKanji(dataString: str):
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


def enc(dataString: str, version = None, ecLevel = None):
    # TODO: Find best fit
    version = 1
    ecLevel = ErrorCorrection.Q

    # Create Bit Buffer
    buff = BitBuffer()

    # Find string length
    strlen = len(dataString)
    if strlen == 0:
        raise ValueError("Try to encode 0 byte data")

    #------------------------------
    # Find mode to encode by check data type
    #------------------------------
    mode = 0
    # * NOT use isdigit() or isnumeric() or isdecimal() for checking Numeric
    #   reason is written in README.md
    if Numeric_Regex.match(dataString) is not None:
        mode = int(ModeIndicator.NUMERIC)
    elif AlphaNum_Regex.match(dataString) is not None:
        mode = int(ModeIndicator.ALPHANUM)
    elif checkKanji(dataString):
        mode = int(ModeIndicator.KANJI)
    else:
        mode = int(ModeIndicator.BYTE)

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
    
    #------------------------------
    # Encode Data
    #------------------------------
    if mode == int(ModeIndicator.NUMERIC):
        for i in range(0, len(dataString), 3):
            # Data to convert
            numStr = dataString[i:i+3]
            buff.put(int(numStr), NumericLength[len(numStr)])
    elif mode == int(ModeIndicator.ALPHANUM):
        # Loop for every 2 characters
        for i in range(0, len(dataString), 2):
            # substr every 2 positions
            char = dataString[i:i+2]
            # Check length
            # 2 characters
            if len(char) > 1:
                # Get numeric representation these 2 characters & Calculate
                num = AlphaNum.find(char[0]) * 45 + AlphaNum.find(char[1])
                # Put
                buff.put(num, 11)
            # 1 character
            else:
                # Get numeric representation that character
                num = AlphaNum.find(char[0])
                # Put
                buff.put(num, 6)
    elif mode == int(ModeIndicator.BYTE):
        charNums = []

        # Convert string to UTF-8 (make sure that this data can be encoded for QR)
        utf8 = dataString.encode("utf-8")

        # Store in list
        for char in utf8:
            charNums.append(char)

        # Put each character for 1 byte one-by-one
        for c in charNums:
            buff.put(c, 8)
    else:
        for i in range(len(dataString)):
            encodedChar = dataString[i].encode("shift-jis")
            # Get HEX value as string
            encodedChar = encodedChar.hex()

            # Convert from string to number
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
            # Calculate
            num = (MSB * 0xC0) + LSB
            buff.put(num, 13)
    
    #------------------------------
    # Determine the Required Number of Bits for this QR Code
    #------------------------------
    blocks = blockinfo(version, ecLevel)
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
    del remain

    #------------------------------
    # Add Pad Bytes if the String is Still too Short
    #------------------------------
    diff = maxbit - len(buff)
    if diff > 0:
        fill = [0b11101100, 0b00010001] # 236 (0xEC) and 17 (0x11), respectively
        for i in range(diff // 8):
            buff.put(fill[i % 2], 8)
    del diff

    #------------------------------
    # Error Correction Coding & Structure Final Message
    #------------------------------
    msg = structFinalMsg(buff, blocks)

    #------------------------------
    # Add Remainder Bits if Necessary
    #------------------------------
    if RemainderBits[version - 1] > 0:
        msg.put(0, RemainderBits[version - 1])

    #------------------------------
    # Create
    #------------------------------
    Module(msg, version, ecLevel)


    try:
        input("Press enter to continue")
    except SyntaxError:
        pass