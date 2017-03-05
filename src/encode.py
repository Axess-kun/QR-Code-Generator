from src.BitBuffer import BitBuffer
from src.enums import *
from src.blocks import *

def enc(string : str):
    buff = BitBuffer()

    # TODO: determine string type & strlen, then select mode & version to encode
    strlen = len(string)

    ## Doing in Alphanumeric Mode
    
    #------------------------------
    # Pre-encode Data
    #------------------------------
    mode = int(ModeIndicator.ALPHANUM)
    buff.put(mode,4)

    charin = int(EncodeSize_S.ALPHANUM)
    buff.put(strlen,charin)
    
    #------------------------------
    # Encode Data
    #------------------------------
    # Loop for every 2 characters
    for i in range(0, len(string), 2):
        # substr every 2 positions
        char = string[i:i+2]
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
    
    print('string: {0:s}'.format(string))
    print(buff.bitstr())
    print('length: {0}'.format(len(buff)))
    buff.dbg_str()
    

    #------------------------------
    # Determine the Required Number of Bits for this QR Code
    #------------------------------
    blocks = blockinfo(1, ErrorCorrection.Q) # Try @ Version 1 & Error Correction Level = Q
    maxbit = 0
    for i in range(len(blocks)):
        maxbit += blocks[i].noOfBlocks * blocks[i].dataCodeword * 8
    
    print('maxbit: {0}'.format(maxbit))

    #------------------------------
    # Add a Terminator
    #------------------------------
    bufflen = len(buff)
    if bufflen < maxbit:
        diff = maxbit - bufflen
        if diff >= 4:
            buff.put(0,4)
        else:
            buff.put(0,diff)
    del bufflen

    print('terminater added len: {0}'.format(len(buff)))
    #------------------------------
    # Add More 0s to Make the Length a Multiple of 8
    #------------------------------
    remain = len(buff) % 8
    if remain != 0:
        buff.put(0,8-remain)
    del remain

    print('multiple of 8 len: {0}'.format(len(buff)))
    #------------------------------
    # Add Pad Bytes if the String is Still too Short
    #------------------------------
    diff = maxbit - len(buff)
    if diff > 0:
        fill = [0b11101100, 0b00010001] # 236 and 17, respectively
        for i in range(diff // 8):
            buff.put(fill[i%2],8)
    del diff


    print('fill cap len: {0}'.format(len(buff)))

    #buff.dbg_str()
    buff.dbg_str8()
    print('------------------------------')
    
    
    try:
        input("Press enter to continue")
    except SyntaxError:
        pass