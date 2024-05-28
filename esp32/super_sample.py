import hashlib
import random
import time
import sys

# Point class to represent points on the curve
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if other is None:
            return False
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

# Elliptic Curve Parameters for secp256k1
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A = 0
B = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


#128
#P = 0xFFFFFFFDFFFFFFFFFFFFFFFFFFFFFFFF
#A = 0xFFFFFFFDFFFFFFFFFFFFFFFFFFFFFFFC
#B = 0xE87579C11079F43DD824993C2CEE5ED3
#Gx = 0x161FF7528B899B2D0C28607CA52C5B86
#Gy = 0xCF5AC8395BAFEB13C02DA292DDED7A83
#N = 0xFFFFFFFE0000000075A30D1B9038A115

#64
#P = 0x1D0D9A6FF
#A = 0x1
#B = 0x1
#G = Point(0x0, 0x1)
#N = 0x1D0D9A6FE

#P = 0xB
#A = 0x1
#B = 0x1
#G = Point(0x1,0x5)
#N = 0x2

G = Point(Gx, Gy)

#def inverse_mod(k, p):
#    """Return the modular inverse of k modulo p."""
#    return pow(k, p - 2, p)


#def point_add(point1, point2):
#    if point1 is None:
#        return point2
#    if point2 is None:
#        return point1
#    if point1.x == point2.x and (point1.y != point2.y or point1.y == 0):
#        return None
#    if point1 == point2:
#        m = (3 * point1.x**2 + A) * inverse_mod(2 * point1.y, P)
#    else:
#        m = (point2.y - point1.y) * inverse_mod(point2.x - point1.x, P)
#    x3 = m**2 - point1.x - point2.x
#    y3 = m * (point1.x - x3) - point1.y
#    return Point(x3 % P, y3 % P)

#def scalar_mult(k, point):
#    if k % N == 0 or point is None:
#        return None
#    if k < 0:
#        return scalar_mult(-k, Point(point.x, -point.y % P))
#    result = None
#    addend = point
#    while k:
#        if k & 1:
#            result = point_add(result, addend)
#        addend = point_add(addend, addend)
#        k >>= 1
#    return result

#def generate_keypair():
#    private_key = random.randint(1, N-1)
#    public_key = scalar_mult(private_key, G)
#    return private_key, public_key

def modular_inverse(a, p):
    """ Return the modular inverse of a under modulo p """
    return pow(a, p - 2, p)

def elliptic_curve_point_addition(x1, y1, x2, y2, a, p):
    """ Calculate the resulting point (x3, y3) from adding points (x1, y1) and (x2, y2) on the elliptic curve """
    if x1 == x2 and y1 == y2:
        # Point doubling
        numerator = (3 * x1**2 + a) % p
        denominator = (2 * y1) % p
    else:
        # Point addition
        numerator = (y2 - y1) % p
        denominator = (x2 - x1) % p

    if denominator == 0:
        raise ValueError("Denominator is zero, cannot compute delta")

    inverse_denominator = modular_inverse(denominator, p)
    delta = (numerator * inverse_denominator) % p

    # Calculate x3
    x3 = (delta**2 - x1 - x2) % p

    # Calculate y3
    y3 = (delta * (x1 - x3) - y1) % p

    return x3, y3

def elliptic_curve_point_multiplication(k, x, y, a, p):
    """ Multiply a point (x, y) by an integer k on the elliptic curve """
    result_x, result_y = x, y
    k_bin = bin(k)[2:]
    
    for i in range(1, len(k_bin)):
        result_x, result_y = elliptic_curve_point_addition(result_x, result_y, result_x, result_y, a, p)
        if k_bin[i] == '1':
            result_x, result_y = elliptic_curve_point_addition(result_x, result_y, x, y, a, p)
    
    return result_x, result_y

def generate_keypair_2():
    """ Generate private and public keys """
    # Generate a random private key
    private_key = random.randint(1, P - 1)
    
    # Calculate the public key
    #public_key_x, public_key_y = elliptic_curve_point_multiplication(private_key, G.x, G.y, A, P)
    public_key = elliptic_curve_point_multiplication(private_key, G.x, G.y, A, P)
    return private_key, public_key
    #return private_key, public_key_x, public_key_y)

def sign_message(private_key, message):
    z = int.from_bytes(hashlib.sha256(message).digest(), 'big')
    r = 0
    s = 0
    while r == 0 or s == 0:
        k = random.randint(1, N-1)
        #p = scalar_mult(k, G)
        print("x:",G.x)
        print("y:",G.y)
        p = elliptic_curve_point_multiplication(k, G.x, G.y, A, P)
        #r = p.x % N
        #s = ((z + r * private_key) * inverse_mod(k, N)) % N
        r = p[0] % N
        s = ((z + r * private_key) * modular_inverse(k, N)) % N
    return (r, s)

def sign_message_2(private_key, message):
    """ Sign the message using ECDSA """
    # Calculate the message hash
    h = int.from_bytes(hashlib.sha256(message).digest(), 'big')

    r, s = 0, 0
    while r == 0 or s == 0:
        # Generate a random number k
        k = random.randint(1, N - 1)

        # Calculate the random point R = k * G and take its x-coordinate
        R = elliptic_curve_point_multiplication(k, G.x, G.y, A, P)
        r = R[0] % N

        # Calculate the signature proof s
        s = (modular_inverse(k, N) * (h + r * private_key)) % N

    return (r, s)

def verify_signature(public_key, message, signature):
    z = int.from_bytes(hashlib.sha256(message).digest(), 'big')
    r, s = signature
    #w = inverse_mod(s, N)
    w = modular_inverse(s, N)
    u1 = (z * w) % N
    u2 = (r * w) % N
    #print('u1:',u1)
    #print('u2:',u2)
    
    ##p = point_add(scalar_mult(u1, G), scalar_mult(u2, public_key))
    #scalr_mult_result_u1 = scalar_mult(u1, G)
    #scalr_mult_result_u2 = scalar_mult(u2, public_key)
    #p = point_add(scalr_mult_result_u1,scalr_mult_result_u2)
    
    scalr_mult_result_u1 = elliptic_curve_point_multiplication(u1, G.x, G.y, A, P)
    scalr_mult_result_u2 = elliptic_curve_point_multiplication(u2, public_key[0],public_key[1],A,P)
    u1_x = scalr_mult_result_u1[0]
    u1_y = scalr_mult_result_u1[1]
    u2_x = scalr_mult_result_u2[0]
    u2_y = scalr_mult_result_u2[1]
    p = elliptic_curve_point_addition(u1_x,u1_y,u2_x,u2_y,A,P)
    
    #elliptic_curve_point_multiplication(k, x, y, a, p)
    #p = elliptic_curve_point_addition(,elliptic_curve_point_multiplication(k, x, y, a, p),
    #return p.x % N == r
    return p[0] % N == r


# find the addition of the two points
# e = Point(1,5)
# f = Point(1,5)
# a = 1
# b = 1
# p = 11
# result = elliptic_curve_point_addition(e.x,e.y,f.x,f.y,a,p)
# print(f"({e.x}+{e.y})+({f.x}+{f.y})=",result)
# sys.exit()

# find multiplication of a given point n times - finding public key
#private_key = 2
#e = Point(1,5)
#a = 1
#p = 11
#public_key = elliptic_curve_point_multiplication(private_key, e.x, e.y, a, p)
#print(f"when multiplying point ({e.x}+{e.y}), {private_key} times: ",public_key)
#sys.exit()

for i in range(2):
    # Example usage
    start_time = time.time()
    
    private_key, public_key = generate_keypair_2()
    #print('generate key pair success:',private_key, public_key)
    keypair_time = time.time()
  
    message = b"Hello, MicroPython!"
    signature = sign_message_2(private_key, message)
    sign_time = time.time()
    #print('signature is:',signature)
    #message = b"Hello, MicroPython"
    is_valid = verify_signature(public_key, message, signature)
    verify_time = time.time()

    print(f"Iteration {i + 1}:")
    print(f"  Keypair Generation Time: {keypair_time - start_time:.6f} seconds")
    print(f"  Signing Time: {sign_time - keypair_time:.6f} seconds")
    print(f"  Verification Time: {verify_time - sign_time:.6f} seconds")
    print(f"  Total Time: {verify_time - start_time:.6f} seconds")
    #print(f"  Signature: {signature}")
    print(f"  Signature valid: {is_valid}")