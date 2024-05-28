import hashlib
import random

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

# Elliptic Curve Parameters for secp256k1
# P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
# A = 0
# B = 7
# G = Point(
#     0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
#     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
# )
# N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

P = 0x3B9ACA07
A = 0
B = 7
G = Point(0x2, 0x8F681D19)
N =  0x3B9ACA05

def inverse_mod(k, p):
    if k == 0:
        raise ZeroDivisionError('division by zero')
    if k < 0:
        return p - inverse_mod(-k, p)
    s, old_s = 0, 1
    t, old_t = 1, 0
    r, old_r = p, k
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_s % p

def point_add(point1, point2):
    if point1 is None:
        return point2
    if point2 is None:
        return point1
    if point1.x == point2.x and (point1.y != point2.y or point1.y == 0):
        return None
    if point1 == point2:
        m = (3 * point1.x**2 + A) * inverse_mod(2 * point1.y, P)
    else:
        m = (point2.y - point1.y) * inverse_mod(point2.x - point1.x, P)
    x3 = m**2 - point1.x - point2.x
    y3 = m * (point1.x - x3) - point1.y
    return Point(x3 % P, y3 % P)

def scalar_mult(k, point):
    if k % N == 0 or point is None:
        return None
    if k < 0:
        return scalar_mult(-k, Point(point.x, -point.y % P))
    result = None
    addend = point
    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result

def generate_keypair():
    private_key = random.randint(1, N-1)
    public_key = scalar_mult(private_key, G)
    return private_key, public_key

def sign_message(private_key, message):
    z = int.from_bytes(hashlib.sha256(message).digest(), 'big')
    r = 0
    s = 0
    while r == 0 or s == 0:
        k = random.randint(1, N-1)
        p = scalar_mult(k, G)
        r = p.x % N
        s = ((z + r * private_key) * inverse_mod(k, N)) % N
    return (r, s)

def verify_signature(public_key, message, signature):
    z = int.from_bytes(hashlib.sha256(message).digest(), 'big')
    r, s = signature
    w = inverse_mod(s, N)
    u1 = (z * w) % N
    u2 = (r * w) % N
    p = point_add(scalar_mult(u1, G), scalar_mult(u2, public_key))
    return p.x % N == r

# Example usage
private_key, public_key = generate_keypair()
print(f"Private Key: {private_key}")
print(f"Public Key: {public_key}")

message = b"Hello, MicroPython!"
signature = sign_message(private_key, message)
print(f"Signature: {signature}")

is_valid = verify_signature(public_key, message, signature)
print(f"Signature valid: {is_valid}")

