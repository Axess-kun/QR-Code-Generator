from PIL import Image, ImageDraw

class Module:
    #------------------------------
    # Converter: Convert Integer to RGB/RGBA as tuple
    #------------------------------
    def int2rgb(self, value):
        return ((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)

    def int2rgba(self, value):
        return ((value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)

    def __init__(self, version):
        #------------------------------
        # Construct QR
        #------------------------------
        self.size = (((version-1)*4)+21)

        # Grey BG for debugging
        bg = self.int2rgb(0x888888)

        # 2D Array
        self.modules = [bg] * self.size
        for row in range(self.size):
            self.modules[row] = [bg] * self.size

        #------------------------------
        # Paint Patterns
        #------------------------------
        self.paintFinderPattern(0, 0)
        self.paintFinderPattern(self.size - 7, 0)
        self.paintFinderPattern(0, self.size - 7)

        # Blank Canvas
        canvas = Image.new("RGB", (self.size, self.size), bg)
        
        # Put data into each module
        for i in range(len(self.modules)):
            for j in range(len(self.modules[i])):
                canvas.putpixel((i,j), self.modules[i][j])

        # Save
        #canvas.save("QR.jpg", "JPEG", quality=100, optimize=True)
        canvas.save("QR.png", "PNG", optimize=True)

    #------------------------------
    # Finder Patterns
    #------------------------------
    def paintFinderPattern(self, row, col):
        for r in range(0, 7):
            # Out of range
            if (row + r) < 0 or (row + r > self.size):
                continue
            
            for c in range(0, 7):
                # Out of range
                if (col + c) < 0 or (col + c) > self.size:
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

    

Module(1)