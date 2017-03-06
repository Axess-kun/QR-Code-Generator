#------------------------------
# Exponent of a in GF(256)
#------------------------------

# Exponent of a -> Integer
EXP_TABLE = list(range(256))
for i in range(8):
	EXP_TABLE[i] = 1 << i

for i in range(8, 256):
    #mul2 = EXP_TABLE[i-1]*2
    #if mul2 > 255:
    #    EXP_TABLE[i] = mul2 ^ 285
    #else:
    #    EXP_TABLE[i] = mul2

    # Since it use byte-wise modulo 285 (100011101) arithmetic
    # So, above if-statement can be rewritten as below
    EXP_TABLE[i] = (EXP_TABLE[i-4] ^ EXP_TABLE[i-5] ^ EXP_TABLE[i-6] ^ EXP_TABLE[i-8])

# Integer -> Exponent of a
LOG_TABLE = list(range(256))
# Since Exponent of a at 255 is 1, duplicated of exponent at 0.
# It'll cause a bug, so loop only 0 ~ 254
for i in range(255):
    LOG_TABLE[EXP_TABLE[i]] = i

# Get data from table
def exp2int(n:int):
    return EXP_TABLE[n % 255]
def int2exp(n:int):
    if n < 1:
        raise ValueError("Error! Can't get value at LOG_TABLE[{0}]".format(n))
    return LOG_TABLE[n]


#------------------------------
# GF(256) Polynomial
#------------------------------
class Polynomial:
    # Parameters:
    #   coefficients: list of coefficients, NOT alpha notations
    #     eg. a3*x2 + a27*x1 + a0 --> [8,12,1]
    def __init__(self, coefficients: list):
        # Create blank list
        self.coefficients = [0] * len(coefficients)

        # Copy to class' member
        for i in range(len(coefficients)):
            self.coefficients[i] = coefficients[i]

    def __mul__(self, other):
        # Create blank list
        coef = [0] * (len(self.coefficients) + len(other.coefficients) - 1)

        # Index & Item Loop
        for i, item in enumerate(self.coefficients):
            for j, otherItem in enumerate(other.coefficients):
                # Addition in GF(256) is performed by XOR
                coef[i + j] ^= exp2int(int2exp(item) + int2exp(otherItem))

        return Polynomial(coef)

# Debug
#a = Polynomial([1,1])
#b = Polynomial([1,2])
#c = a*b
#print(c.coefficients) # should be 1,3,2
#d = Polynomial([1,4])
#e = c*d
#print(e.coefficients) # should be 1,7,14,8
#print('---------')