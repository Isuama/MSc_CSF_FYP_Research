# Curve parameters for secp256k1
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
a = 0
b = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (Gx, Gy)

# Modular arithmetic
def mod_inv(a, m):
    return pow(a, -1, m)

# Point addition
def point_add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1

    x1, y1 = p1
    x2, y2 = p2

    if x1 == x2 and y1 != y2:
        return None

    if p1 == p2:
        m = (3 * x1 * x1 + a) * mod_inv(2 * y1, p) % p
    else:
        m = (y2 - y1) * mod_inv(x2 - x1, p) % p

    x3 = (m * m - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p

    return (x3, y3)

# Point doubling
def point_double(p):
    return point_add(p, p)

# Scalar multiplication
def scalar_mult(k, p):
    result = None
    while k > 0:
        if k % 2 == 1:
            result = point_add(result, p)
        k //= 2
        p = point_double(p)
    return result

# Message to be signed
message = b"Hello, world!"

# Generate a random private key (integer)
import os
private_key = int.from_bytes(os.urandom(32), byteorder="big") % n

# Generate the public key
public_key = scalar_mult(private_key, G)

# Generate a random value (k)
k = int.from_bytes(os.urandom(32), byteorder="big") % n

# Calculate the point (x1, y1) = k * G
x1, y1 = scalar_mult(k, G)

# Calculate r = x1 mod n
r = x1 % n

# Calculate s = (z + r * dA) / k mod n
z = int.from_bytes(hashlib.sha256(message).digest(), byteorder="big")
s = (z + r * private_key) * mod_inv(k, n) % n

# The signature is the pair (r, s)
signature = (r, s)

# Verify the signature
def verify_signature(signature, message, public_key):
    r, s = signature
    if r < 1 or r > n-1 or s < 1 or s > n-1:
        return False

    z = int.from_bytes(hashlib.sha256(message).digest(), byteorder="big")
    w = mod_inv(s, n)
    u1 = z * w % n
    u2 = r * w % n

    x, y = point_add(scalar_mult(u1, G), scalar_mult(u2, public_key))
    if x is None or r != x % n:
        return False
    return True

# Verify the signature
if verify_signature(signature, message, public_key):
    print("Signature is valid.")
else:
    print("Signature is invalid.")
