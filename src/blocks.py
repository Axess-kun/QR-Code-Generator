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
    # Number of Blocks in Group 2 ,
    # Number of Data Codewords in Each of Group 1's Blocks 2]

    # Version
    # 1
    [1, 19],
    [1, 16],
    [1, 13],
    [1, 9],

    # 2
    [1, 34],
    [1, 28],
    [1, 22],
    [1, 16],

    # 3
    [1, 55],
    [1, 44],
    [2, 17],
    [2, 13],

    # 4
    [1, 80],
    [2, 32],
    [2, 24],
    [4, 9],

    # 5
    [1, 108],
    [2, 43],
    [2, 15, 2, 16],
    [2, 11, 2, 12],
]

class RSBlock:
    def __init__(self, noOfBlocks, dataCodeword):
        self.noOfBlocks = noOfBlocks
        self.dataCodeword = dataCodeword

def blockinfo(version, errorCorrection : ErrorCorrection):
    offset = int(errorCorrection)
    info = RS_BLOCK_TABLE[(version - 1) * 4 + offset]

    blocks = []
    for i in range(0, len(info), 2):
        noOfBlocks, dataCodeword = info[i:i+2]
        blocks.append(RSBlock(noOfBlocks, dataCodeword))

    return blocks