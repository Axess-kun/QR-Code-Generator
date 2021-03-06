from enum import Enum
import re # regex

#****************************************************************************************************
#------------------------------
# Error Correction Level
#------------------------------
class ErrorCorrection(Enum):
    L, M, Q, H = range(4)
    def __int__(self):
        return self.value


#------------------------------
# Regular Expression
#   [...]   Matches any single character in brackets.
#   *       Matches 0 or more occurrences of preceding expression.
#   $       Matches end of line.
#------------------------------
Numeric_Regex = re.compile("[0-9]*$")
AlphaNum_Regex = re.compile("[0-9A-Z $%*+-./:]*$")


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
# Number of bits for numeric data lengths
# Can be calculated by using this formula
#   (len(str(num)) * 3) + 1
#     where 'num' is 1~3 digits number
#------------------------------
NumericLength = { 3 : 10, 2 : 7, 1 : 4 }


#------------------------------
# Alphanumeric
#------------------------------
AlphaNum = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:'


#------------------------------
# Hexadecimal
#------------------------------
HexNum = '0123456789abcdef'


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


#****************************************************************************************************
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