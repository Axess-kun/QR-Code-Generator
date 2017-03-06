class BitBuffer:
    # Declare & initialize variable
    def __init__(self):
        # Buffer, store each item as 8-bit data
        self.buffer = []
        # Now buffer's length
        self.length = 0

    # Put number in length-bit
    # Parameters:
    #   num    : number to put
    #   length : length of bit to put number into
    def put(self, num, length):
        # Inverse right-shift loop to find that position bit from left-to-right
        for i in range(length):
            # Determine 'how many position' to shift
            shift = (length - i - 1)

            # Shift & Check that bit is 1 or 0
            bitToPut = (num >> shift) & 1

            # Put that bit into buffer
            self.putBit(bitToPut)

    # Put each bit in 8-bit index
    def putBit(self, bit):
        # Finding now item's index
        itemIndex = self.length // 8

        # Check no. of items in buffer
        # If less than or equal to index, create 0 (to do OR operation)
        if len(self.buffer) <= itemIndex:
            self.buffer.append(0)
        # If bit to store is 1
        if bit:
            # Store after last one
            self.buffer[itemIndex] |= (0x80 >> (self.length % 8))
        # Either 0 or 1, after put it, the length will increased
        self.length += 1

    # Copy from type(BitBuffer) using operator =
    def __eq__(self, other):
        if isinstance(other, BitBuffer):
            self.buffer = other.buffer[:]
            self.length = other.length

    # Copy from type(list)
    def copyList(self, byteList = []):
        self.buffer = byteList[:]
        self.length = len(byteList) * 8

    # Return length of buffer
    def __len__(self):
        return self.length

    # bitBuffer[n]
    def __getitem__(self, n):
        return self.buffer[n]

    # Debug print()
    def __str__(self):
        return str(self.buffer)
    

# Debug
#buff = BitBuffer()
#buff.put(2,4) #0010 0000 = 32
#buff.put(2,3) #0010 0100 = 36
#buff.put(11,9) #0010 0100 0000 1011 = 36, 11
#print(buff)