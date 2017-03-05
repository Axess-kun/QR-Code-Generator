from enum import Enum

#------------------------------
# Mode Indicator
#------------------------------
class ModeIndicator(Enum):
    # Mode Name = Mode Indicator (4-bit binary)
    NUMERIC     = 1 << 0 # Numeric
    ALPHANUM    = 1 << 1 # Alphanumeric -> '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:'
    BYTE        = 1 << 2 # 8-bit byte
    KANJI       = 1 << 3 # Japanese

#------------------------------
# Character Count Indicator
#------------------------------
# Version 1 - 9
class EncodeSize_S(Enum):
    NUMERIC     = 10
    ALPHANUM    = 9
    BYTE        = 8
    KANJI       = 8

# Version 10 - 26
class EncodeSize_M(Enum):
    NUMERIC     = 12
    ALPHANUM    = 11
    BYTE        = 16
    KANJI       = 10

# Version 27 - 40
class EncodeSize_L(Enum):
    NUMERIC     = 14
    ALPHANUM    = 13
    BYTE        = 16
    KANJI       = 12