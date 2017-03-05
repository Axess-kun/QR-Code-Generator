from src.BitBuffer import BitBuffer
from src.enums import *

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
    print('------------------------------')
    
    try:
        input("Press enter to continue")
    except SyntaxError:
        pass