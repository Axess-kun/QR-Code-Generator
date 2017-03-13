from PIL import Image, ImageDraw
from src.BitBuffer import BitBuffer
from math import floor, ceil
from src.constants import *
from builtins import next
from src.look_up_table import AlignmentPosition

# TODO: using thread to speed-up best mask test

"""
### Module class ###
Members
- version: int
    Version of QR Code.
- errorCorrection: constants.ErrorCorrection
    Error Correction Level of QR Code.
- size: int
    Module size (width and height) of QR Code.
- modules: list[list, list, ...]
    2D Array of lists.
    Contains None, True, False as flag for drawing dark (black) or light (white) module.

Methods
- makeModule(BitBuffer dataBuffer, int maskNumber) -> void
    Create QR Code from "dataBuffer" with mask pattern "maskNumber".
- paintFinderSeparatorPattern(int row, int col) -> void
    Paint finder separator pattern at "row" and "col" where "row" and "col" are Top-Left of pattern.
- paintAlignmentPattern() -> void
    Paint alignment pattern of that QR version.
- paintTimingPattern() -> void
    Paint timing pattern.
- paintFormatInfo(int maskNumber) -> void
    Paint format information with mask "maskNumber".
- paintVersionInfo() -> void
    Paint version information (when version is 7 or above).
- paintDatas(BitBuffer dataBuffer, int maskNumber) -> void
    Paint data from "dataBuffer" with mask "maskNumber".

- countBits(int num) -> int
    Count number of bits from binary number "num".
- get15bitsFormatString(int first5bits) -> int
    Create 15 bits format information string.
- get18bitsVersionString() -> int
    Create 18 bits version information string.

- calcPenaltyScore() -> int
    Calculate total penalty score with 4 rules.
- calcPenaltyScoreRule1() -> int
    Calculate penalty score using rule #1.
- calcPenaltyScoreRule2() -> int
    Calculate penalty score using rule #2.
- calcPenaltyScoreRule3() -> int
    Calculate penalty score using rule #3.
- calcPenaltyScoreRule4() -> int
    Calculate penalty score using rule #4.

- int2rgb(int value) -> tuple(R, G, B)
    Convert "value" number to tuple as R, G, B values.
- int2rgba(int value) -> tuple(R, G, B, A)
    Convert "value" number to tuple as R, G, B, A values.


### getMaskPatternFunc() function ###
Get lambda function of specific mask pattern.

Parameters
- maskNumber: int
    Mask pattern, from 0 to 7.
"""

####################################################################################################
# Module
####################################################################################################
class Module:
    def __init__(self, dataBuffer: BitBuffer, version: int, errorCorrection: ErrorCorrection):
        #------------------------------
        # Assign variable to member
        #------------------------------
        self.version = version
        self.errorCorrection = errorCorrection
        self.size = (version * 4) + 17 # Equivalent to (((version - 1) * 4) + 21)

        #------------------------------
        # Test for every mask patterns & find the best one
        #------------------------------
        bestMask = 0
        minPenaltyScore = 0
        for i in range(8):
            # Create QR.
            self.makeModule(dataBuffer, i)
            # Calculate penalty score.
            penaltyScore = self.calcPenaltyScore()

            # First loop or found better one.
            if i == 0 or penaltyScore < minPenaltyScore:
                minPenaltyScore = penaltyScore
                bestMask = i

        #------------------------------
        # Real Making
        #------------------------------
        # Best mask is not last one, make it again!
        if bestMask != 7:
            self.makeModule(dataBuffer, bestMask)

        #------------------------------
        # Draw
        #------------------------------
        # White BG.
        bg = self.int2rgb(0xFFFFFF)
        # Blank Canvas with White Border
        canvas = Image.new("RGB", (self.size+2, self.size+2), bg)
        
        # Put data into each module.
        for i in range(len(self.modules)):
            for j in range(len(self.modules[i])):
                if self.modules[i][j] is not None:
                    canvas.putpixel((j+1,i+1), self.int2rgb(0) if self.modules[i][j] else self.int2rgb(0xFFFFFF))

        # Save
        canvas.save("QR.png", "PNG", optimize=True)


    #****************************************************************************************************
    #--------------------------------------------------
    # Make Module (QR Code)
    #
    # Parameters:
    #   maskNumber: Mask pattern number 0 to 7.
    #--------------------------------------------------
    def makeModule(self, dataBuffer: BitBuffer, maskNumber: int = 0):
        #------------------------------
        # Create or Overwritten it as None / 2D Array
        #------------------------------
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
        # Format Infos.
        self.paintFormatInfo(maskNumber)
        # Version Infos (Version 7 or above)
        if self.version >= 7:
            self.paintVersionInfo()

        #------------------------------
        # Paint Datas
        #------------------------------
        self.paintDatas(dataBuffer, maskNumber)


    #--------------------------------------------------
    # Finder Patterns & Separators
    #--------------------------------------------------
    def paintFinderSeparatorPattern(self, row: int, col: int):
        # Loop in 0 ~ 7 for Finder Pattern.
        # Loop at -1, 8 for Separators.
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


    #--------------------------------------------------
    # Alignment Patterns
    #--------------------------------------------------
    def paintAlignmentPattern(self):
        # All possible position
        pos = AlignmentPosition[self.version - 1]

        # Loop for each pair.
        for i in range(len(pos)):
            for j in range(len(pos)):
                # Current row & column (middle of alignment pattern to be placed).
                row = pos[i]
                col = pos[j]

                # Check if finder pattern placed -> Nothing to do with this position.
                if self.modules[row][col] is not None:
                    continue

                # Else, loop for drawing.
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

    
    #--------------------------------------------------
    # Timing Patterns
    #--------------------------------------------------
    def paintTimingPattern(self):
        # Vertical loop from 8 ~ size - 9
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

    
    #--------------------------------------------------
    # Format Information Area
    #--------------------------------------------------
    def paintFormatInfo(self, maskNumber: int):
        # Format String
        first5bits = (ECDic[self.errorCorrection] << 3) | maskNumber
        dataToWrite = self.get15bitsFormatString(first5bits)

        # Vertical
        for row in range(15):
            # dataToWrite: Bit from left to right are most significant bit and least significant bit, respectively.
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

        
    #--------------------------------------------------
    # Version Information Area
    #--------------------------------------------------
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


    #--------------------------------------------------
    # Datas
    #--------------------------------------------------
    def paintDatas(self, dataBuffer: BitBuffer, maskNumber: int):
        totalDataBytes = len(dataBuffer.buffer)
        bitIndex = 7
        byteIndex = 0
        row = self.size - 1
        rowInc = -1 # Row increasement (up-down direction)

        # Mask Function
        maskFunc = getMaskPatternFunc(maskNumber)

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
                        # Data to be written
                        # If capacity is not filled, get White color.
                        write = False

                        # Still readable
                        if byteIndex < totalDataBytes:
                            # Get bit by byteIndex & bitIndex.
                            # bitIndex is from right to left as 0~7 respectively.
                            write = ((dataBuffer[byteIndex] >> bitIndex) & 1) == 1
                            # Used 1 bit
                            bitIndex -= 1

                            if maskFunc(row, col):
                                # Toggle
                                write = not write

                            # Write
                            self.modules[row][col] = write

                            # Next byte
                            if bitIndex == -1:
                                bitIndex = 7
                                byteIndex += 1
                        # Unreadable // If capacity is filled, nothing like this can be happened.
                        else:
                            break

                # Next row
                row += rowInc

                # Hit top or bottom.
                if row < 0 or row >= self.size:
                    row -= rowInc # Go back 1 step.
                    rowInc *= -1 # Swap direction.
                    break


    #****************************************************************************************************
    #--------------------------------------------------
    # Count bits from number
    #--------------------------------------------------
    def countBits(self, num: int):
        cnt = 0
        while num != 0:
            cnt += 1
            num >>= 1
        return cnt


    #--------------------------------------------------
    # Format String Bits
    #--------------------------------------------------
    def get15bitsFormatString(self, first5bits: int):
        # Create 15 bits data.
        data = first5bits << 10
        
        # While data has 11 bits or more (FormatStringGP has 11 bits).
        while self.countBits(data) - self.countBits(FormatStringGP) >= 0:
            # Pad generator polynomial to has a same bit size as data.
            paddedGP = FormatStringGP << (self.countBits(data) - self.countBits(FormatStringGP))
            # XOR format string.
            data ^= paddedGP

        # Now we have 10 bits data, put it behind first 5 bits.
        data |= (first5bits << 10)

        # XOR with format string mask.
        data ^= FormatStringMask

        return data


    #--------------------------------------------------
    # Version String Bits
    #--------------------------------------------------
    def get18bitsVersionString(self):
        # Create 18 bits data, first 6 bits is version in binary.
        data = self.version << 12
        
        # While data has 13 bits or more (VersionStringGP has 13 bits).
        while self.countBits(data) - self.countBits(VersionStringGP) >= 0:
            # Pad generator polynomial to has a same bit size as data.
            paddedGP = VersionStringGP << (self.countBits(data) - self.countBits(VersionStringGP))
            # XOR format string.
            data ^= paddedGP

        # Now we have 12 bits data, put it behind first 6 bits.
        data |= (self.version << 12)

        return data


    #****************************************************************************************************
    #--------------------------------------------------
    # Calculate Penalty Scores of Masking
    #--------------------------------------------------
    def calcPenaltyScore(self):
        score = self.calcPenaltyScoreRule1()
        score += self.calcPenaltyScoreRule2()
        score += self.calcPenaltyScoreRule3()
        score += self.calcPenaltyScoreRule4()

        return score


    #--------------------------------------------------
    # Condition #1
    #--------------------------------------------------
    def calcPenaltyScoreRule1(self):
        """
        Check each row one-by-one.
        If there are five consecutive modules of the same color, add 3 to the penalty.
        If there are more modules of the same color after the first five, add 1 for each additional module of the same color.
        Afterward, check each column one-by-one, checking for the same condition.
        Add the horizontal and vertical total to obtain penalty score #1.
        """

        score = 0
        for row in range(self.size):
            lastDot = self.modules[row][0]
            sameCount = 1
            for col in range(1, self.size):
                # Same color
                if self.modules[row][col] == lastDot:
                    sameCount += 1
                    if sameCount == 5:
                        score += 3
                    elif sameCount > 5:
                        score += 1
                # Not same color
                else:
                    lastDot = self.modules[row][col]
                    sameCount = 1

        # Vertical
        for col in range(self.size):
            lastDot = self.modules[0][col]
            sameCount = 1
            for row in range(1, self.size):
                # Same color
                if self.modules[row][col] == lastDot:
                    sameCount += 1
                    if sameCount == 5:
                        score += 3
                    elif sameCount > 5:
                        score += 1
                # Not same color
                else:
                    lastDot = self.modules[row][col]
                    sameCount = 1

        return score


    #--------------------------------------------------
    # Condition #2
    #--------------------------------------------------
    def calcPenaltyScoreRule2(self):
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
        
        # Optimized
        moduleRange = range(self.size - 1)
        for row in moduleRange:
            # Use iterator and next() to skip next four-block.
            # e.g.
            #   A B C
            #   D E F
            # Look at left rectangle ABED,
            # if Top-Right != Botton-Right (B != E), then both ABED and BCEF won't lost any point.
            it = iter(moduleRange)
            for col in it:
                topRight = self.modules[row][col + 1]
                if topRight != self.modules[row + 1][col + 1]:
                    # Skip next one to reduce runtime.
                    # None: Raise nothing if there is no next item.
                    next(it, None)
                elif topRight != self.modules[row][col]:
                    continue
                elif topRight != self.modules[row + 1][col]:
                    continue
                else:
                    score += 3

        #--------------------------------------------------
        # Simple one
        #for row in range(self.size-1):
        #    for col in range(self.size-1):
        #        count = 0
        #        if self.modules[row][col]:
        #            count += 1
        #        if self.modules[row+1][col]:
        #            count += 1
        #        if self.modules[row][col+1]:
        #            count += 1
        #        if self.modules[row+1][col+1]:
        #            count += 1
        #        # 2x2 White or 2x2 Black
        #        if count == 0 or count == 4:
        #            score += 3
        #--------------------------------------------------

        return score


    #--------------------------------------------------
    # Condition #3
    #--------------------------------------------------
    def calcPenaltyScoreRule3(self):
        """
        Looks for patterns of dark-light-dark-dark-dark-light-dark that have four light modules on either side.
        In other words, it looks for any of the following two patterns:
        10111010000 (0x5D0)
        OR
        00001011101 (0x05D)
        Each time this pattern is found, add 40 to the penalty score.
        """
        # ^
        # Same patterns at index 1, 4, 5, 6, 9 which values are 0, 1, 0, 1, 0 respectively.

        # Pattern1:     10111010000
        # Pattern2: 00001011101

        score = 0
        # Horizontal
        for row in range(self.size):
            # Use iterator to skip those unmatched for sure.
            it = iter(range(self.size - 10))
            for col in it:
                if (    not self.modules[row][col+1]
                    and     self.modules[row][col+4]
                    and not self.modules[row][col+5]
                    and     self.modules[row][col+6]
                    and not self.modules[row][col+9]
                    and (
                            (       self.modules[row][col]
                            and     self.modules[row][col+2]
                            and     self.modules[row][col+3]
                            and not self.modules[row][col+7]
                            and not self.modules[row][col+8]
                            and not self.modules[row][col+10]
                            )
                        or
                            (   not self.modules[row][col]
                            and not self.modules[row][col+2]
                            and not self.modules[row][col+3]
                            and     self.modules[row][col+7]
                            and     self.modules[row][col+8]
                            and     self.modules[row][col+10]
                            )
                        )
                    ):
                    score += 40

                # Boyer–Moore–Horspool algorithm.
                # if this_row[col + 10] == True,  Pattern1 shift 4, Pattern2 shift 2. So min=2.
                # if this_row[col + 10] == False, Pattern1 shift 1, Pattern2 shift 1. So min=1.
                if self.modules[row][col+10]:
                    next(it, None)

        # Vertical
        for col in range(self.size):
            it = iter(range(self.size - 10))
            for row in it:
                if (    not self.modules[row+1][col]
                    and     self.modules[row+4][col]
                    and not self.modules[row+5][col]
                    and     self.modules[row+6][col]
                    and not self.modules[row+9][col]
                    and (
                            (       self.modules[row][col]
                            and     self.modules[row+2][col]
                            and     self.modules[row+3][col]
                            and not self.modules[row+7][col]
                            and not self.modules[row+8][col]
                            and not self.modules[row+10][col]
                            )
                        or
                            (   not self.modules[row][col]
                            and not self.modules[row+2][col]
                            and not self.modules[row+3][col]
                            and     self.modules[row+7][col]
                            and     self.modules[row+8][col]
                            and     self.modules[row+10][col]
                            )
                        )
                    ):
                    score += 40

                if self.modules[row+10][col]:
                    next(it, None)

        #--------------------------------------------------
        # Slower, comment outed
        ## Horizontal
        #for row in range(self.size):
        #    bits = 0
        #    for col in range(self.size):
        #        bits = ((bits << 1) & 0x7FF) # Keep 11 bits
        #        bits |= 1 if self.modules[row][col] else 0

        #        # Check from column 10~ & matched patterns.
        #        if col >= 10 and (bits in (0x5D0, 0x05D)):
        #            score += 40

        ## Vertical
        #for col in range(self.size):
        #    bits = 0
        #    for row in range(self.size):
        #        bits = ((bits << 1) & 0x7FF) # Keep 11 bits
        #        bits |= 1 if self.modules[row][col] else 0

        #        # Check from row 10~ & matched patterns.
        #        if row >= 10 and (bits in (0x5D0, 0x05D)):
        #            score += 40
        #--------------------------------------------------

        return score


    #--------------------------------------------------
    # Condition #4
    #--------------------------------------------------
    def calcPenaltyScoreRule4(self):
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
        # Find smaller number from 2 numbers -> use // to throw away remainder.
        score = (abs(percent - 50) // 5) * 10

        return score


    #****************************************************************************************************
    #--------------------------------------------------
    # Converter: Convert Integer to RGB/RGBA as tuple
    #--------------------------------------------------
    def int2rgb(self, value: int):
        return ((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)

    def int2rgba(self, value: int):
        return ((value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)


####################################################################################################
# Return lambda function to determine mask.
####################################################################################################
def getMaskPatternFunc(maskNumber: int):
    if maskNumber == 0:
        return lambda row, col: (row + col) % 2 == 0
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


####################################################################################################
# Return list of alignment position.
# Code from github.com/nayuki/QR-Code-generator/
# *** Using Look Up Table for speed run -> comment outed.
####################################################################################################
#def getAlignmentPosition(version : int):
#    if version == 1:
#        return []
#    else:
#        align = (version // 7) + 2
#        if version != 32:
#            step = (((ver * 4) + (align * 2) + 1) // ((2 * align) - 2)) * 2
#        else:
#            step = 26
#        result = [6]
#        # Last position number
#        pos = (version * 4) + 10
#        for i in range(align - 1):
#            result.insert(1, pos)
#            pos -= step
#        return result