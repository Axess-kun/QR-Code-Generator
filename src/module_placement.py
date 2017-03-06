from PIL import Image, ImageDraw

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

class Module:
    #------------------------------
    # Converter: Convert Integer to RGB/RGBA as tuple
    #------------------------------
    def int2rgb(self, value):
        return ((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)

    def int2rgba(self, value):
        return ((value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)

    def __init__(self, version):
        self.version = version
        #------------------------------
        # Construct QR
        #------------------------------
        self.size = (((version-1)*4)+21)

        # Grey BG for debugging
        bg = self.int2rgb(0x888888)

        # 2D Array
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

Module(1)
Module(18)
Module(40)