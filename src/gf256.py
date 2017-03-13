"""
Galois Field a.k.a. GF

### EXP_TABLE and LOG_TABLE ###
Log Antilog table of finite field GF(256)


### exp2int() function ###
Get value of alpha notations.

Parameters
- n: int
    Where n is alpha notations.
    Every number over 255 will be modulated by 256


### int2exp() function ###
Get alpha notations from value.

Parameters
- n: int
    Where n is value in range 1 to 255


### Polynomial class ###
Members
- coefficients: list
    List of coefficients.
    Where first coefficients is at x^(lenght of list - 1) term and last coefficient is at x^0 term.

Methods
- getGenerator(int n) -> Polynomial
    Create error correction codewords generator polynomial.
    Where n is number of error correction codewords.

Operations
- [int n] -> int
    Get coefficients of index n.
- iter(Polynomial obj) -> iter
    Get iterator from coefficients.
- len(Polynomial obj) -> int
    Get length of coefficients.
- * Polynomial -> Polynomial
    Multiply other Polynomial using GF(256).
- % Polynomial -> Polynomial
    Modulate other Polynomial using GF(256).
    Return the remainder as Polynomial
"""


####################################################################################################
# Exponent of a in GF(256) / Galois Field 256
####################################################################################################

# Exponent of a -> Integer
EXP_TABLE = list(range(256))

# Precompute
for i in range(8):
	EXP_TABLE[i] = 1 << i

for i in range(8, 256):
    #mul2 = EXP_TABLE[i-1]*2
    #if mul2 > 255:
    #    EXP_TABLE[i] = mul2 ^ 285
    #else:
    #    EXP_TABLE[i] = mul2

    # Since it use byte-wise modulo 285 (100011101) arithmetic.
    # So, above if-statement can be rewritten as below.
    EXP_TABLE[i] = (EXP_TABLE[i-4] ^ EXP_TABLE[i-5] ^ EXP_TABLE[i-6] ^ EXP_TABLE[i-8])

# Integer -> Exponent of a
LOG_TABLE = list(range(256))

# Precompute
# Since Exponent of a at 255 is 1, duplicated of exponent at 0.
# It'll cause a bug, so loop only 0 ~ 254.
for i in range(255):
    LOG_TABLE[EXP_TABLE[i]] = i

####################################################################################################
# Get data from table
####################################################################################################
def exp2int(n: int):
    return EXP_TABLE[n % 255]
def int2exp(n: int):
    if n < 1:
        raise ValueError("Error! Can't get value at LOG_TABLE[{0}]".format(n))
    return LOG_TABLE[n]


####################################################################################################
# GF(256) Polynomial
####################################################################################################
class Polynomial:
    #--------------------------------------------------
    # Constructor
    #
    # Parameters:
    #   coefficients: list of coefficients, NOT alpha notations.
    #     eg. a3*x2 + a27*x1 + a0 --> [8,12,1]
    #   termShift: Error Correction Codewords.
    #     To make sure that the exponent of the lead term doesn't become too small during the division,
    #     multiply the message polynomial by xn where n is the number of error correction codewords that are needed.
    #--------------------------------------------------
    def __init__(self, coefficients: list, termShift: int = 0):
        # Offset to kill first(front) term(s) that coefficient is 0 until it not.
        offset = 0
        for i in range(len(coefficients)):
            if coefficients[i] != 0:
                break;
            offset += 1

        # Create blank list.
        self.coefficients = [0] * (len(coefficients) - offset + termShift)

        # Copy to class' member.
        for i in range(len(coefficients) - offset):
            self.coefficients[i] = coefficients[i + offset]

    #--------------------------------------------------
    # polynomial[n]
    #--------------------------------------------------
    def __getitem__(self, n: int):
        return self.coefficients[n]

    #--------------------------------------------------
    # for-loop iterator
    #--------------------------------------------------
    def __iter__(self):
        return iter(self.coefficients)

    #--------------------------------------------------
    # len(polynomial)
    #--------------------------------------------------
    def __len__(self):
        return len(self.coefficients)

    #--------------------------------------------------
    # * Polynomial
    #--------------------------------------------------
    def __mul__(self, other):
        # Create blank list.
        coef = [0] * (len(self) + len(other) - 1)

        # Index & Item Loop.
        for i, item in enumerate(self):
            for j, otherItem in enumerate(other):
                # Addition in GF(256) is performed by XOR.
                coef[i + j] ^= exp2int(int2exp(item) + int2exp(otherItem))

        return Polynomial(coef)

    #--------------------------------------------------
    # % Polynomial
    #--------------------------------------------------
    def __mod__(self, other):
        diff = len(self) - len(other)
        #------------------------------
        # Find remainder
        #------------------------------
        # If len(dividend) < len(divisor), then return dividend itself because can't divide it.
        # ... used as recursive break.
        if diff < 0:
            return self

        firstTermExpDiff = int2exp(self[0]) - int2exp(other[0])

        # Create copied list.
        coef = self[:]
        
        for i, (item, otherItem) in enumerate(zip(self, other)):
            coef[i] = item ^ exp2int(int2exp(otherItem) + firstTermExpDiff)

        # Recursive until can't divide.
        return Polynomial(coef) % other

    #--------------------------------------------------
    # Get Generator Polynomial
    #
    # Parameters:
    #   n: Error Correction Codewords
    #--------------------------------------------------
    def getGenerator(n: int):
        # Create a0 = 1 as initial polynomial.
        poly = Polynomial([1])
        for i in range(n):
            poly = poly * Polynomial([1, exp2int(i)])
        return poly

    #--------------------------------------------------
    # Debug
    #--------------------------------------------------
    def __str__(self):
        return str(self.coefficients)