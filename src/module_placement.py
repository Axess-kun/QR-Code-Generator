from PIL import Image, ImageDraw
from src.BitBuffer import BitBuffer
from math import floor, ceil
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
        #    self.calcPenalty()
        self.makeModule(dataBuffer, 4)
        self.calcPenalty()
        

        #------------------------------
        # Draw
        #------------------------------
        # Blank Canvas
        canvas = Image.new("RGB", (self.size, self.size), bg)
        
        # Put data into each module
        for i in range(len(self.modules)):
            for j in range(len(self.modules[i])):
                if self.modules[i][j] is not None:
                    canvas.putpixel((j,i), self.int2rgb(0) if self.modules[i][j] == True else self.int2rgb(0xFFFFFF))

        # Save
        #canvas.save("QR.jpg", "JPEG", quality=100, optimize=True)
        filename = "QR_" + str(version) + ".png"
        canvas.save(filename, "PNG", optimize=True)

    #------------------------------
    # Make Module (QR Code)
    #------------------------------
    # Parameters:
    #   maskNumber: Mask pattern number (0~7)
    def makeModule(self, dataBuffer, maskNumber = 0):
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
        self.modules[(self.version*4)+9][8] = True

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
        self.paintDatas(dataBuffer, maskNumber) #* NOT applied mask yet!! just for debugging mask penalty score

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
                    self.modules[row + r][col + c] = True
                else:
                    # White
                    self.modules[row + r][col + c] = False

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
                            self.modules[row + r][col + c] = True
                        else:
                            # White
                            self.modules[row + r][col + c] = False

    #------------------------------
    # Timing Patterns
    #------------------------------
    def paintTimingPattern(self):
        # Vertical loop from 8 ~ size-9
        for row in range(8, self.size - 8):
            if self.modules[row][6] is not None:
                continue
            if (row % 2) == 0:
                self.modules[row][6] = True
            else:
                self.modules[row][6] = False

        # Horizontal loop
        for col in range(8, self.size - 8):
            if self.modules[6][col] is not None:
                continue
            if (col % 2) == 0:
                self.modules[6][col] = True
            else:
                self.modules[6][col] = False

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
            write = ((dataToWrite >> row) & 1) == 1

            if row < 6:
                self.modules[row][8] = write
            elif row < 8: # Skip timing
                self.modules[row+1][8] = write
            else: # Bottom Line
                self.modules[self.size-15+row][8] = write

        # Horizontal
        for col in range(15):
            write = ((dataToWrite >> (14-col)) & 1) == 1
            if col < 6:
                self.modules[8][col] = write
            elif col < 7: # Skip timing
                self.modules[8][col+1] = write
            else: # Right Line
                self.modules[8][self.size-15+col] = write

        

    #------------------------------
    # Version Information Area
    #------------------------------
    def paintVersionInfo(self):
        # Version String
        dataToWrite = self.get18bitsVersionString()

        # Top-Right (3x6)
        for row in range(6):
            for col in range(3):
                write = ((dataToWrite >> ((row * 3) + col)) & 1) == 1
                self.modules[row][self.size-11+col] = write

        # Bottom-Left (6x3)
        for col in range(6):
            for row in range(3):
                write = ((dataToWrite >> ((col * 3) + row)) & 1) == 1
                self.modules[self.size-11+row][col] = write

    #------------------------------
    # Datas
    # * NOT applied mask yet!!
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
                            # bitIndex is from right to left as 0~7 respectively
                            self.modules[row][col] = ((dataBuffer[byteIndex] >> bitIndex) & 1) == 1
                            # Used 1 bit
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

    #------------------------------
    # Calculate Penalty Scores of Masking
    #------------------------------
    def calcPenalty(self):
        score = self.calcPenalty1()
        score += self.calcPenalty2()
        score += self.calcPenalty3()
        score += self.calcPenalty4()

        return score

    # Condition #1
    def calcPenalty1(self):
        """
        Check each row one-by-one.
        If there are five consecutive modules of the same color, add 3 to the penalty.
        If there are more modules of the same color after the first five, add 1 for each additional module of the same color.
        Afterward, check each column one-by-one, checking for the same condition.
        Add the horizontal and vertical total to obtain penalty score #1.
        """

        score = 0
        lastDot = None
        sameCount = 1
        # Horizontal
        for row in range(self.size):
            for col in range(self.size):
                # First Column
                if col == 0:
                    # Get this dot color / Black or White
                    lastDot = self.modules[row][col]
                # Last Column
                elif col == self.size - 1:
                    # Same as previous?
                    if self.modules[row][col-1] == lastDot:
                        sameCount += 1
                    # Check
                    if sameCount >= 5:
                        score += (sameCount - 5) + 3
                # Second~
                else:
                    # Same as previous?
                    if self.modules[row][col-1] == lastDot:
                        sameCount += 1
                    else:
                        # Check
                        if sameCount >= 5:
                            score += (sameCount - 5) + 3
                        # Renew lastDot color
                        lastDot = self.modules[row][col]
                        # Reset sameCount
                        sameCount = 1

        # Debug
        colScore = score
        print("column count: {0}".format(colScore))

        # Vertical
        for col in range(self.size):
            for row in range(self.size):
                # First Row
                if row == 0:
                    # Get this dot color / Black or White
                    lastDot = self.modules[row][col]
                # Last Row
                elif row == self.size - 1:
                    # Same as previous?
                    if self.modules[row-1][col] == lastDot:
                        sameCount += 1
                    # Check
                    if sameCount >= 5:
                        score += (sameCount - 5) + 3
                # Second~
                else:
                    # Same as previous?
                    if self.modules[row-1][col] == lastDot:
                        sameCount += 1
                    else:
                        # Check
                        if sameCount >= 5:
                            score += (sameCount - 5) + 3
                        # Renew lastDot color
                        lastDot = self.modules[row][col]
                        # Reset sameCount
                        sameCount = 1
        # Debug
        print("row count: {0}".format(score-colScore))

        return score

    # Condition #2
    def calcPenalty2(self):
        """
        Look for areas of the same color that are at least 2x2 modules or larger.
        The QR code specification says that for a solid-color block of size m × n, the penalty score is 3 × (m - 1) × (n - 1).
        However, the QR code specification does not specify how to calculate the penalty
        when there are multiple ways of dividing up the solid-color blocks.

        Therefore, rather than looking for solid-color blocks larger than 2x2,
        simply add 3 to the penalty score for every 2x2 block of the same color in the QR code,
        making sure to count overlapping 2x2 blocks.
        For example, a 3x2 block of the same color should be counted as two 2x2 blocks, one overlapping the other. 
        """

        score = 0
        for row in range(self.size-1):
            for col in range(self.size-1):
                count = 0
                if self.modules[row][col]:
                    count += 1
                if self.modules[row+1][col]:
                    count += 1
                if self.modules[row][col+1]:
                    count += 1
                if self.modules[row+1][col+1]:
                    count += 1

                # 2x2 White or 2x2 Black
                if count == 0 or count == 4:
                    score += 3

        # Debug
        print("penalty #2 = {0}".format(score))
                    
        return score

    # Condition #3
    def calcPenalty3(self):
        """
        Looks for patterns of dark-light-dark-dark-dark-light-dark that have four light modules on either side.
        In other words, it looks for any of the following two patterns:
        10111010000
        OR
        00001011101
        Each time this pattern is found, add 40 to the penalty score.
        """
        # ^
        # Check only dark-light-dark-dark-dark-light-dark (1011101) is fine

        score = 0
        # Horizontal
        for row in range(self.size):
            for col in range(self.size-6):
                if (self.modules[row][col] and
                    not self.modules[row][col+1] and
                    self.modules[row][col+2] and
                    self.modules[row][col+3] and
                    self.modules[row][col+4] and
                    not self.modules[row][col+5] and
                    self.modules[row][col+6]):
                    score += 40

        # Vertical
        for col in range(self.size):
            for row in range(self.size-6):
                if (self.modules[row][col] and
                    not self.modules[row+1][col] and
                    self.modules[row+2][col] and
                    self.modules[row+3][col] and
                    self.modules[row+4][col] and
                    not self.modules[row+5][col] and
                    self.modules[row+6][col]):
                    score += 40

        # Debug
        print("penalty #3 = {0}".format(score))

        return score

    # Condition #4
    def calcPenalty4(self):
        """
        Do the following steps:
        1. Count the total number of modules in the matrix.
        2. Count how many dark modules there are in the matrix.
        3. Calculate the percent of modules in the matrix that are dark: (darkmodules / totalmodules) * 100
        4. Determine the previous and next multiple of five of this percent. For example, for 43 percent,
           the previous multiple of five is 40, and the next multiple of five is 45.
        5. Subtract 50 from each of these multiples of five and take the absolute value of the result.
           For example, |40 - 50| = |-10| = 10 and |45 - 50| = |-5| = 5.
        6. Divide each of these by five. For example, 10/5 = 2 and 5/5 = 1.
        7. Finally, take the smallest of the two numbers and multiply it by 10. In this example,
           the lower number is 1, so the result is 10. This is penalty score #4.
        """

        # Step 2
        darkCount = 0
        for row in range(self.size):
            for col in range(self.size):
                if self.modules[row][col]:
                    darkCount += 1

        # Step 1, 3
        percent = (darkCount / (self.size * self.size)) * 100.0
        # Step 4-7
        # Find smaller number from 2 numbers -> use // to throw away remainder
        score = (abs(percent - 50) // 5) * 10

        # Debug
        print("penalty #4 = {0}".format(score))

        return score