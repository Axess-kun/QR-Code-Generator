class BitBuffer:
    # Declare & initialize variable
    def __init__(self):
        self.buffer = []
        # Debug
        self.dbg_buff = [] # Type: List of string

    # Put number in length-bit
    # Parameters:
    #   num    : number to put
    #   length : length of bit to put number into
    def put(self, num, length):
        temp = '' # Debug
        # Inverse right-shift loop to find that position bit from left-to-right
        for i in range(length):
            # Determine 'how many position' to shift
            shift = (length - i - 1)

            # Shift & Check that bit is 1 or 0
            bitToPut = (num >> shift) & 1

            # Put that bit into buffer
            self.buffer.append(bitToPut)
            temp += str(bitToPut) # Debug
        self.dbg_buff.append(temp) # Debug

    # Return length of buffer
    def __len__(self):
        return len(self.buffer)

    # Return buffer as String
    def bitstr(self):
        return self.to_str(self.buffer)

    # Convert form list to string
    def to_str(self, buf_list):
        s = ''
        for i in range(len(buf_list)):
            s += str(buf_list[i])
        return s

    # Get groups of byte as decimal integer
    def getByteGroups(self):
        groups = []
        for i in range(0, len(self.buffer), 8):
            group = self.buffer[i:i+8]
            byte = 0
            for j in range(8):
                byte |= group[j] << (7-j)
            groups.append(byte)
        return groups

    # Debug
    def dbg_str(self):
        for i in range(len(self.dbg_buff)):
            print(self.dbg_buff[i])

    def dbg_str8(self):
        for i in range(0, len(self.buffer), 8):
            group = self.buffer[i:i+8]
            print(self.to_str(group))