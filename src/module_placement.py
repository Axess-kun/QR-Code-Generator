from PIL import Image, ImageDraw
from src.BitBuffer import BitBuffer
from math import floor
from src.enums import *

AlignmentPosition = [
    # Each line represent each version from 1 to 40 respectively
    [],
    [6, 18],
    [6, 22],
    [6, 26],
    [6, 30],
    [6, 34],
    [6, 22, 38],
    [6, 24, 42],
    [6, 26, 46],
    [6, 28, 50],
    [6, 30, 54],
    [6, 32, 58],
    [6, 34, 62],
    [6, 26, 46, 66],
    [6, 26, 48, 70],
    [6, 26, 50, 74],
    [6, 30, 54, 78],
    [6, 30, 56, 82],
    [6, 30, 58, 86],
    [6, 34, 62, 90],
    [6, 28, 50, 72, 94],
    [6, 26, 50, 74, 98],
    [6, 30, 54, 78, 102],
    [6, 28, 54, 80, 106],
    [6, 32, 58, 84, 110],
    [6, 30, 58, 86, 114],
    [6, 34, 62, 90, 118],
    [6, 26, 50, 74, 98, 122],
    [6, 30, 54, 78, 102, 126],
    [6, 26, 52, 78, 104, 130],
    [6, 30, 56, 82, 108, 134],
    [6, 34, 60, 86, 112, 138],
    [6, 30, 58, 86, 114, 142],
    [6, 34, 62, 90, 118, 146],
    [6, 30, 54, 78, 102, 126, 150],
    [6, 24, 50, 76, 102, 128, 154],
    [6, 28, 54, 80, 106, 132, 158],
    [6, 32, 58, 84, 110, 136, 162],
    [6, 26, 54, 82, 110, 138, 166],
    [6, 30, 58, 86, 114, 142, 170]
]

# Return function to determine mask
def getMaskPatternFunc(maskNumber : int):
    if maskNumber == 0:
        return lambda row, col: (row + column) % 2 == 0
    if maskNumber == 1:
        return lambda row, col: row % 2 == 0
    if maskNumber == 2:
        return lambda row, col: col % 3 == 0
    if maskNumber == 3:
        return lambda row, col: (row + col) % 3 == 0
    if maskNumber == 4:
        return lambda row, col: (floor(row / 2) + floor(col / 3)) % 2 == 0
    if maskNumber == 5:
        return lambda row, col: ((row * col) % 2) + ((row * col) % 3) == 0
    if maskNumber == 6:
        return lambda row, col: (((row * col) % 2) + ((row * col) % 3)) % 2 == 0
    if maskNumber == 7:
        return lambda row, col: (((row + col) % 2) + ((row * col) % 3)) % 2 == 0
    raise ValueError("No Mask Number {0}".format(maskNumber))

# Error Correction Dictionary for Format String Calculation
ECDic = {
    ErrorCorrection.L: 1,
    ErrorCorrection.M: 0,
    ErrorCorrection.Q: 2,
    ErrorCorrection.H: 3,
}

class Module:
    #------------------------------
    # Converter: Convert Integer to RGB/RGBA as tuple
    #------------------------------
    def int2rgb(self, value):
        return ((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)

    def int2rgba(self, value):
        return ((value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)

    def __init__(self, dataBuffer, version, errorCorrection):
        self.version = version
        self.errorCorrection = errorCorrection
        #------------------------------
        # Construct QR
        #------------------------------
        self.size = (((version-1)*4)+21)

        # Grey BG for debugging
        bg = self.int2rgb(0x888888)

        

        #------------------------------
        # Test for every mask patterns
        #------------------------------
        #for i in range(8):
        #    self.makeModule(i)
        self.makeModule(4)
        

        #------------------------------
        # Draw
        #------------------------------
        # Blank Canvas
        canvas = Image.new("RGB", (self.size, self.size), bg)
        
        # Put data into each module
        for i in range(len(self.modules)):
            for j in range(len(self.modules[i])):
                if self.modules[i][j] is not None:
                    canvas.putpixel((j,i), self.modules[i][j])

        # Save
        #canvas.save("QR.jpg", "JPEG", quality=100, optimize=True)
        filename = "QR_" + str(version) + ".png"
        canvas.save(filename, "PNG", optimize=True)

    #------------------------------
    # Make Module (QR Code)
    #------------------------------
    # Parameters:
    #   maskNumber: Mask pattern number (0~7)
    def makeModule(self, maskNumber = 0):
        # 2D Array / Create or Overwritten it as None
        self.modules = [None] * self.size
        for row in range(self.size):
            self.modules[row] = [None] * self.size

        #------------------------------
        # Paint Patterns
        #------------------------------
        # Finder Pattern & Separators
        self.paintFinderSeparatorPattern(0, 0)
        self.paintFinderSeparatorPattern(self.size - 7, 0)
        self.paintFinderSeparatorPattern(0, self.size - 7)
        # Alignment Patterns
        self.paintAlignmentPattern()
        # Timing Patterns
        self.paintTimingPattern()
        # Dark Module
        self.modules[(self.version*4)+9][8] = self.int2rgb(0)

        #------------------------------
        # Format & Version Information Area
        #------------------------------
        # Format Infos
        self.paintFormatInfo(maskNumber)
        # Version Infos (Version 7++)
        if self.version >= 7:
            self.paintVersionInfo()

        #------------------------------
        # Paint Datas
        #------------------------------
        #self.paintDatas(dataBuffer, maskNumber)

    #------------------------------
    # Finder Patterns & Separators
    #------------------------------
    def paintFinderSeparatorPattern(self, row, col):
        # Loop in 0 ~ 7 for Finder Pattern
        # Loop at -1, 8 for Separators
        for r in range(-1, 8):
            # Out of range
            if (row + r) < 0 or (row + r) >= self.size:
                continue
            
            for c in range(-1, 8):
                # Out of range
                if (col + c) < 0 or (col + c) >= self.size:
                    continue

                if (
                    (0 <= r and r <= 6 and (c == 0 or c == 6)) # Vertical Border
                    or
                    (0 <= c and c <= 6 and (r == 0 or r == 6)) # Horizontal Border
                    or
                    (2 <= r and r <= 4 and 2 <= c and c <= 4) # Middle 3x3
                    ):
                    # Black
                    self.modules[row + r][col + c] = self.int2rgb(0)
                else:
                    # White
                    self.modules[row + r][col + c] = self.int2rgb(0xFFFFFF)

    #------------------------------
    # Alignment Patterns
    #------------------------------
    def paintAlignmentPattern(self):
        # All possible position
        pos = AlignmentPosition[self.version - 1]

        # Loop for each pair
        for i in range(len(pos)):
            for j in range(len(pos)):
                # Current row & column (middle of alignment pattern to be placed)
                row = pos[i]
                col = pos[j]

                # Check if finder pattern placed -> Nothing to do with this position
                if self.modules[row][col] is not None:
                    continue

                # Else, loop for drawing
                for r in range(-2, 3):
                    for c in range(-2, 3):
                        if (r == -2 or r == 2 # Vertical Border
                            or
                            c == -2 or c == 2 # Horizontal Border
                            or
                            (r == 0 and c == 0) # Middle
                            ):
                            # Black
                            self.modules[row + r][col + c] = self.int2rgb(0)
                        else:
                            # White
                            self.modules[row + r][col + c] = self.int2rgb(0xFFFFFF)

    #------------------------------
    # Timing Patterns
    #------------------------------
    def paintTimingPattern(self):
        # Vertical loop from 8 ~ size-9
        for row in range(8, self.size - 8):
            if self.modules[row][6] is not None:
                continue
            if (row % 2) == 0:
                self.modules[row][6] = self.int2rgb(0)
            else:
                self.modules[row][6] = self.int2rgb(0xFFFFFF)

        # Horizontal loop
        for col in range(8, self.size - 8):
            if self.modules[6][col] is not None:
                continue
            if (col % 2) == 0:
                self.modules[6][col] = self.int2rgb(0)
            else:
                self.modules[6][col] = self.int2rgb(0xFFFFFF)

    #------------------------------
    # Count bits from number
    #------------------------------
    def countBits(self, num):
        cnt = 0
        while num != 0:
            cnt += 1
            num >>= 1
        return cnt

    #------------------------------
    # Format String Bits
    #------------------------------
    def get15bitsFormatString(self, first5bits):
        # Create 15 bits data
        data = first5bits << 10
        
        # While data has 11 bits or more (FormatStringGP has 11 bits)
        while self.countBits(data) - self.countBits(FormatStringGP) >= 0:
            # Pad generator polynomial to has a same bit size as data
            paddedGP = FormatStringGP << (self.countBits(data) - self.countBits(FormatStringGP))
            # XOR format string
            data ^= paddedGP

        # Now we have 10 bits data, put it behind first 5 bits
        data |= (first5bits << 10)

        # XOR with format string mask
        data ^= FormatStringMask

        return data

    #------------------------------
    # Version String Bits
    #------------------------------
    def get18bitsVersionString(self):
        # Create 18 bits data, first 6 bits is version in binary
        data = self.version << 12
        
        # While data has 13 bits or more (VersionStringGP has 13 bits)
        while self.countBits(data) - self.countBits(VersionStringGP) >= 0:
            # Pad generator polynomial to has a same bit size as data
            paddedGP = VersionStringGP << (self.countBits(data) - self.countBits(VersionStringGP))
            # XOR format string
            data ^= paddedGP

        # Now we have 12 bits data, put it behind first 6 bits
        data |= (self.version << 12)

        return data

    #------------------------------
    # Format Information Area
    #------------------------------
    def paintFormatInfo(self, maskNumber):
        # Format String
        first5bits = (ECDic[self.errorCorrection] << 3) | maskNumber
        dataToWrite = self.get15bitsFormatString(first5bits)

        # Vertical
        for row in range(15):
            # dataToWrite: Bit from left to right are most significant bit and least significant bit, respectively
            write = (dataToWrite >> row) & 1

            if row < 6:
                self.modules[row][8] = self.int2rgb(0) if write else self.int2rgb(0xFFFFFF)
            elif row < 8: # Skip timing
                self.modules[row+1][8] = self.int2rgb(0) if write else self.int2rgb(0xFFFFFF)
            else: # Bottom Line
                self.modules[self.size-15+row][8] = self.int2rgb(0) if write else self.int2rgb(0xFFFFFF)

        # Horizontal
        for col in range(15):
            write = (dataToWrite >> (14-col)) & 1
            if col < 6:
                self.modules[8][col] = self.int2rgb(0) if write else self.int2rgb(0xFFFFFF)
            elif col < 7: # Skip timing
                self.modules[8][col+1] = self.int2rgb(0) if write else self.int2rgb(0xFFFFFF)
            else: # Right Line
                self.modules[8][self.size-15+col] = self.int2rgb(0) if write else self.int2rgb(0xFFFFFF)

        

    #------------------------------
    # Version Information Area
    #------------------------------
    def paintVersionInfo(self):
        # Version String
        dataToWrite = self.get18bitsVersionString()

        # Top-Right (3x6)
        for row in range(6):
            for col in range(3):
                write = (dataToWrite >> ((row * 3) + col)) & 1
                self.modules[row][self.size-11+col] = self.int2rgb(0) if write else self.int2rgb(0xFFFFFF)

        # Bottom-Left (6x3)
        for col in range(6):
            for row in range(3):
                write = (dataToWrite >> ((col * 3) + row)) & 1
                self.modules[self.size-11+row][col] = self.int2rgb(0) if write else self.int2rgb(0xFFFFFF)

    #------------------------------
    # Datas
    #------------------------------
    def paintDatas(self, dataBuffer, maskNumber):
        totalDataBytes = len(dataBuffer.buffer)
        bitIndex = 7
        byteIndex = 0
        row = self.size - 1
        rowInc = -1 # Row increasement (up-down direction)

        # Loop from right to left
        for baseColumn in range(self.size-1,0,-2):
            # Skip timing line
            if baseColumn <= 6: # Since using loop, use '<=' to change value for next loop & next next loop ...
                baseColumn -= 1

            # Range to draw
            colRange = (baseColumn, baseColumn-1)

            # Draw in these 2 columns until hit top-bottom or break
            while True:
                for col in colRange:
                    # Blank slot
                    if self.modules[row][col] is None:
                        # Still readable
                        if byteIndex < totalDataBytes:
                            # Get bit by byteIndex & bitIndex
                            # bitIndex is from right to left as 0~7 respectively)
                            # 1
                            if (dataBuffer[byteIndex] >> bitIndex) & 1:
                                self.modules[row][col] = self.int2rgb(0)
                            # 0
                            else:
                                self.modules[row][col] = self.int2rgb(0xFFFFFF)
                            bitIndex -= 1

                            # Next byte
                            if bitIndex == -1:
                                bitIndex = 7
                                byteIndex += 1
                        # Unreadable // If capacity is filled, nothing like this can be happened
                        else:
                            break

                # Next row
                row += rowInc

                # Hit top or bottom
                if row < 0 or row >= self.size:
                    row -= rowInc # Go back 1 step
                    rowInc *= -1 # Swap direction
                    break