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
    #   termShift: Error Correction Codewords
    #     To make sure that the exponent of the lead term doesn't become too small during the division,
    #     multiply the message polynomial by xn where n is the number of error correction codewords that are needed.
    def __init__(self, coefficients: list, termShift = 0):
        # Offset to kill first(front) term(s) that coefficient is 0 until it not
        offset = 0
        for i in range(len(coefficients)):
            if coefficients[i] != 0:
                break;
            offset += 1

        # Create blank list
        self.coefficients = [0] * (len(coefficients) - offset + termShift)

        # Copy to class' member
        for i in range(len(coefficients) - offset):
            self.coefficients[i] = coefficients[i + offset]

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

    def __mod__(self, other):
        diff = len(self.coefficients) - len(other.coefficients)
        # Find remainder
        # If len(dividend) < len(divisor), then return dividend itself because can't divide it
        # ... used as recursive break
        if diff < 0:
            return self

        firstTermExpDiff = int2exp(self.coefficients[0]) - int2exp(other.coefficients[0])

        # Create blank list * Copy
        coef = self.coefficients[:]
        
        for i, (item, otherItem) in enumerate(zip(self.coefficients, other.coefficients)):
            coef[i] = item ^ exp2int(int2exp(otherItem) + firstTermExpDiff)

        # Recursive until can't divide
        return Polynomial(coef) % other

    def getGenerator(n:int):
        # Create a0 = 1 as initial polynomial
        poly = Polynomial([1])
        for i in range(n):
            poly = poly * Polynomial([1, exp2int(i)])
        return poly

        

a = Polynomial([1,7,14,8])
b = Polynomial([1,3,2])
c = a%b
print(c.coefficients) # Should be 0
print('---------')
d = Polynomial([32, 91, 11, 120, 209, 114, 220, 77, 67, 64, 236, 17, 236, 17, 236, 17])
e = Polynomial.getGenerator(10) # Shoud be 1, 216, 194, 159, 111, 199, 94, 95, 113, 157, 193
print(e.coefficients)
msg = Polynomial(d.coefficients, len(e.coefficients) - 1)
print(msg.coefficients)
f = msg%e
print(f.coefficients) # Should be 196, 35, 39, 119, 235, 215, 231, 226, 93, 23
print('---------')