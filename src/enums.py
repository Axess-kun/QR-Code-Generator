from enum import Enum
import re # regex

#------------------------------
# Mode Indicator
#------------------------------
class ModeIndicator(Enum):
    # Mode Name = Mode Indicator (4-bit binary)
    NUMERIC     = 0 # Numeric
    ALPHANUM    = 1 # Alphanumeric
    BYTE        = 2 # 8-bit byte
    KANJI       = 3 # Japanese

    def __int__(self):
        return self.value

#------------------------------
# Character Count Indicator
#------------------------------
            # [Num, AlphaNum, Byte, Kanji]
# Version 1 - 9
EncodeSize_S = [10, 9, 8, 8]
# Version 10 - 26
EncodeSize_M = [12, 11, 16, 10]
# Version 27 - 40
EncodeSize_L = [14, 13, 16, 12]

#------------------------------
# Alphanumeric
#------------------------------
AlphaNum = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:'

#------------------------------
# Hexadecimal
#------------------------------
HexNum = '0123456789abcdef'

#------------------------------
# Number of bits for numeric data lengths
# Can be calculated by using this formula
#   (len(str(num)) * 3) + 1
#     where 'num' is 1~3 digits number
#------------------------------
NumericLength = { 3 : 10, 2 : 7, 1 : 4 }

#------------------------------
# Regular Expression
#------------------------------
Numeric_Regex = re.compile("[0-9]*$")
AlphaNum_Regex = re.compile("[0-9A-Z $%*+-./:]*$")

#------------------------------
# Error Correction Level
#------------------------------
class ErrorCorrection(Enum):
    L, M, Q, H = range(4)
    def __int__(self):
        return self.value



#------------------------------
# Remainder Bits
#------------------------------
RemainderBits = [
                    # Version
    0, 7, 7, 7, 7,  # 1 - 5
    7, 0, 0, 0, 0,  # 6 - 10
    0, 0, 0, 3, 3,  # 11 - 15
    3, 3, 3, 3, 3,  # 16 - 20
    4, 4, 4, 4, 4,  # 21 - 25
    4, 4, 3, 3, 3,  # 26 - 30
    3, 3, 3, 3, 0,  # 31 - 35
    0, 0, 0, 0, 0   # 36 - 40
]

#------------------------------
# Alignment Position
#------------------------------
AlignmentPosition = [
    # Each line represent each version from 1 to 40 respectively
    [],
    [6, 18],
    [6, 22],
    [6, 26],
    [6, 30],
    [6, 34],
    [6, 22, 38],
    [6, 24, 42],
    [6, 26, 46],
    [6, 28, 50],
    [6, 30, 54],
    [6, 32, 58],
    [6, 34, 62],
    [6, 26, 46, 66],
    [6, 26, 48, 70],
    [6, 26, 50, 74],
    [6, 30, 54, 78],
    [6, 30, 56, 82],
    [6, 30, 58, 86],
    [6, 34, 62, 90],
    [6, 28, 50, 72, 94],
    [6, 26, 50, 74, 98],
    [6, 30, 54, 78, 102],
    [6, 28, 54, 80, 106],
    [6, 32, 58, 84, 110],
    [6, 30, 58, 86, 114],
    [6, 34, 62, 90, 118],
    [6, 26, 50, 74, 98, 122],
    [6, 30, 54, 78, 102, 126],
    [6, 26, 52, 78, 104, 130],
    [6, 30, 56, 82, 108, 134],
    [6, 34, 60, 86, 112, 138],
    [6, 30, 58, 86, 114, 142],
    [6, 34, 62, 90, 118, 146],
    [6, 30, 54, 78, 102, 126, 150],
    [6, 24, 50, 76, 102, 128, 154],
    [6, 28, 54, 80, 106, 132, 158],
    [6, 32, 58, 84, 110, 136, 162],
    [6, 26, 54, 82, 110, 138, 166],
    [6, 30, 58, 86, 114, 142, 170]
]

#------------------------------
# Format & Version Information
#------------------------------
# Format String Generator Polynomial
FormatStringGP = 0b10100110111
# Format String Mask
FormatStringMask = 0b101010000010010
# Version String Generator Polynomial
VersionStringGP = 0b1111100100101

#------------------------------
# Error Correction Dictionary for Format String Calculation
#------------------------------
ECDic = {
    ErrorCorrection.L: 1,
    ErrorCorrection.M: 0,
    ErrorCorrection.Q: 3,
    ErrorCorrection.H: 2,
}