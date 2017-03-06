from src.BitBuffer import BitBuffer
from src.enums import *
from src.blocks import *
from src.gf256 import Polynomial

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
    print(buff)
    print('length: {0}'.format(len(buff)))
    

    #------------------------------
    # Determine the Required Number of Bits for this QR Code
    #------------------------------
    blocks = blockinfo(1, ErrorCorrection.M) # Try @ Version 1 & Error Correction Level = Q
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

    #print(buff)
    print('------------------------------')

    #------------------------------
    # Error Correction Coding
    #------------------------------
    msg = Polynomial(buff[:])
    ecCodeword = blocks[0].ecCodeword
    gen = Polynomial.getGenerator(ecCodeword)
    newmsg = Polynomial(msg, ecCodeword)
    errCode = (newmsg % gen)[:]

    del msg, gen, newmsg, ecCodeword

    #------------------------------
    # Structure Final Message (One block of data codewords)
    #------------------------------
    for i in range(len(errCode)):
        buff.put(errCode[i], 8)

    print(buff)
    print('------------------------------')


    print('-------- DEBUG 5-Q ------')
    #------------------------------
    # Structure Final Message (Large data codewords)
    #------------------------------
# Debug
    large = [BitBuffer(), BitBuffer(), BitBuffer(), BitBuffer()]
    set1 = [67,85,70,134,87,38,85,194,119,50,6,18,6,103,38]
    set2 = [246,246,66,7,118,134,242,7,38,86,22,198,199,146,6]
    for i in range(15):
        large[0].put(set1[i],8)
        large[1].put(set2[i],8)
    set3 = [182,230,247,119,50,7,118,134,87,38,82,6,134,151,50,7]
    set4 = [70,247,118,86,194,6,151,50,16,236,17,236,17,236,17,236]
    for i in range(16):
        large[2].put(set3[i],8)
        large[3].put(set4[i],8)
    
    # Debug Show
    for i in range(4):
        print(large[i])

    rs5q = blockinfo(5, ErrorCorrection.Q)
    errCodes = []
    for i in range(4):
        msg = Polynomial(large[i][:])
        ecCodeword = rs5q[0].ecCodeword
        gen = Polynomial.getGenerator(ecCodeword)
        newmsg = Polynomial(msg, ecCodeword)
        errCode = (newmsg % gen)[:]
        # Debug Show
        #print(errCode)
        errCodes.append(errCode)

    # Debug Show
    for i in range(4):
        print(errCodes[i])

    #------------------------------
    # Interleave the Data Codewords & Error Correction Codewords
    #------------------------------
    #interleave = []
    ## Create new 2-D array to store data codewords table
    #dataTable = [0] * 4
    #errTable = [0] * 4

    #maxDataCodeword = 0
    #maxErrorCodeword = 0
    #for i in range(len(large)):
    #    maxDataCodeword = max(maxDataCodeword, len(large[i]))
    #    maxErrorCodeword = max(maxErrorCodeword, len(errCodes[i]))
    #    dataTable[i] = [0] * len(large[i])
    #    errTable[i] = [0] * len(errCodes[i])

    
    ## Store in table
    #for i in range(len(large)):
    #    for j in range(len(large[i])):
    #        dataTable[i][j] = large[i][j]

    #for i in range(len(errCodes)):
    #    for j in range(len(errCodes[i])):
    #        errTable[i][j] = errCodes[i][j]

    #newsort = []
    #for i in range(maxDataCodeword):
    #    for j in range(len(dataTable)):
    #        if i < len(dataTable[j]):
    #            newsort.append(dataTable[j][i])

    #for i in range(maxErrorCodeword):
    #    for j in range(len(errTable)):
    #        if i < len(errTable[j]):
    #            newsort.append(errTable[j][i])

    #print(newsort)

    try:
        input("Press enter to continue")
    except SyntaxError:
        pass