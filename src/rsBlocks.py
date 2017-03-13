from src.constants import ErrorCorrection
from src.look_up_table import RS_BLOCK_TABLE

"""
### RSBlock class ###
Members
- noDataCodeword: int
    Number of data codewords.
- noEcCodeword: int
    Number of error correction codewords.


### blockInfo() function ###
Get every number of data codewords and error correction codewords from
Reed-Solomon block corresponding to error correction level.

Parameters
- version: int
    Version of QR Code.
- errorCorrection: constants.ErrorCorrection
    Error Correction Level of QR Code.
"""


####################################################################################################
# RSBlock
####################################################################################################
class RSBlock:
    def __init__(self, noDataCodeword: int, noEcCodeword: int):
        self.noDataCodeword = noDataCodeword
        self.noEcCodeword = noEcCodeword


####################################################################################################
# Return list of RSBlock
####################################################################################################
def blockInfo(version: int, errorCorrection: ErrorCorrection):
    offset = int(errorCorrection)
    info = RS_BLOCK_TABLE[(version - 1) * 4 + offset]

    blocks = []
    for i in range(1, len(info), 2):
        ecCodeword = info[0]
        noOfBlocks, dataCodeword = info[i:i+2]
        for j in range(noOfBlocks):
            blocks.append(RSBlock(dataCodeword, ecCodeword))

    return blocks