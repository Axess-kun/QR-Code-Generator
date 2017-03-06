from src.enums import ErrorCorrection

#------------------------------
# Reed-Solomon block
#------------------------------
RS_BLOCK_TABLE = [
    ### Vertical Format
    # L
    # M
    # Q
    # H

    ### Horizontal Format
    # [Number of Blocks in Group 1 ,
    # Number of Data Codewords in Each of Group 1's Blocks ,
    # Error Correction Codewords per Block , # Group 1 & 2 are same
    # Number of Blocks in Group 2 ,
    # Number of Data Codewords in Each of Group 1's Blocks 2 ,
    # Error Correction Codewords per Block]

    # Version
    # 1
    [1, 19, 7],
    [1, 16, 10],
    [1, 13, 13],
    [1, 9, 17],

    # 2
    [1, 34, 10],
    [1, 28, 16],
    [1, 22, 22],
    [1, 16, 28],

    # 3
    [1, 55, 15],
    [1, 44, 26],
    [2, 17, 18],
    [2, 13, 22],

    # 4
    [1, 80, 20],
    [2, 32, 18],
    [2, 24, 26],
    [4, 9, 16],

    # 5
    [1, 108, 26],
    [2, 43, 24],
    [2, 15, 18, 2, 16, 18],
    [2, 11, 22, 2, 12, 22],
]

class RSBlock:
    def __init__(self, noOfBlocks, dataCodeword, ecCodeword):
        self.noOfBlocks = noOfBlocks
        self.dataCodeword = dataCodeword
        self.ecCodeword = ecCodeword

def blockinfo(version, errorCorrection : ErrorCorrection):
    offset = int(errorCorrection)
    info = RS_BLOCK_TABLE[(version - 1) * 4 + offset]

    blocks = []
    for i in range(0, len(info), 3):
        noOfBlocks, dataCodeword, ecCodeword = info[i:i+3]
        blocks.append(RSBlock(noOfBlocks, dataCodeword, ecCodeword))

    return blocks