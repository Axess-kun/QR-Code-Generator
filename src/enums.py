from enum import Enum

#------------------------------
# Mode Indicator
#------------------------------
class ModeIndicator(Enum):
    # Mode Name = Mode Indicator (4-bit binary)
    NUMERIC     = 1 << 0 # Numeric
    ALPHANUM    = 1 << 1 # Alphanumeric
    BYTE        = 1 << 2 # 8-bit byte
    KANJI       = 1 << 3 # Japanese

    def __int__(self):
        return self.value

#------------------------------
# Character Count Indicator
#------------------------------
# Version 1 - 9
class EncodeSize_S(Enum):
    NUMERIC     = 10
    ALPHANUM    = 9
    BYTE        = 8
    KANJI       = 8

    def __int__(self):
        return self.value

# Version 10 - 26
class EncodeSize_M(Enum):
    NUMERIC     = 12
    ALPHANUM    = 11
    BYTE        = 16
    KANJI       = 10

    def __int__(self):
        return self.value

# Version 27 - 40
class EncodeSize_L(Enum):
    NUMERIC     = 14
    ALPHANUM    = 13
    BYTE        = 16
    KANJI       = 12

    def __int__(self):
        return self.value

#------------------------------
# Alphanumeric
#------------------------------
AlphaNum = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:'

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