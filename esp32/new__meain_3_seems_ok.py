import hashlib
import random
from ucryptolib import aes

# Simple elliptic curve parameters
p = 23  # prime number
a = 1   # coefficient a
b = 1   # coefficient b
Gx = 3  # x-coordinate of the base point
Gy = 10 # y-coordinate of the base point
n = 20  # order of the base point

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

G = Point(Gx, Gy)

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
    gcd, x, y = old_r, old_s, old_t
    return x % p

def point_addition(point1, point2):
    if point1 is None:
        return point2
    if point2 is None:
        return point1
    if point1 == point2:
        return point_doubling(point1)

    x1, y1 = point1.x, point1.y
    x2, y2 = point2.x, point2.y

    if x1 == x2 and (y1 + y2) % p == 0:
        return None

    m = (y2 - y1) * inverse_mod(x2 - x1, p) % p
    x3 = (m**2 - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p

    return Point(x3, y3)

def point_doubling(point):
    if point is None:
        return None

    x, y = point.x, point.y

    if y == 0:
        return None

    m = (3 * x**2 + a) * inverse_mod(2 * y, p) % p
    x3 = (m**2 - 2 * x) % p
    y3 = (m * (x - x3) - y) % p

    return Point(x3, y3)

def scalar_multiplication(k, point):
    result = None
    addend = point
    
    while k:
        if k & 1:
            result = point_addition(result, addend)
        addend = point_doubling(addend)
        k >>= 1
    
    return result

def generate_keypair():
    private_key = random.randint(1, n - 1)
    public_key = scalar_multiplication(private_key, G)
    return private_key, public_key

# Symmetric encryption using AES in CBC mode
def encrypt_aes_cbc(key, iv, plaintext):
    cipher = aes(key, 2, iv)  # AES-128 in CBC mode
    while len(plaintext) % 16 != 0:
        plaintext += b' '  # Padding to 16 bytes
    ciphertext = cipher.encrypt(plaintext)
    return ciphertext

def decrypt_aes_cbc(key, iv, ciphertext):
    cipher = aes(key, 2, iv)  # AES-128 in CBC mode
    plaintext = cipher.decrypt(ciphertext)
    return plaintext.rstrip(b' ')

# ECIES encryption using AES-CBC
def ecies_encrypt(public_key, message):
    ephemeral_private_key, ephemeral_public_key = generate_keypair()
    shared_secret = scalar_multiplication(ephemeral_private_key, public_key).x
    shared_secret_bytes = shared_secret.to_bytes(16, 'big')
    
    # Generate a random IV for AES-CBC
    iv = random.randint(0, 2**128 - 1).to_bytes(16, 'big')
    
    ciphertext = encrypt_aes_cbc(shared_secret_bytes, iv, message.encode('utf-8'))
    return ephemeral_public_key, iv, ciphertext

# ECIES decryption using AES-CBC
def ecies_decrypt(private_key, ephemeral_public_key, iv, ciphertext):
    shared_secret = scalar_multiplication(private_key, ephemeral_public_key).x
    shared_secret_bytes = shared_secret.to_bytes(16, 'big')
    plaintext = decrypt_aes_cbc(shared_secret_bytes, iv, ciphertext)
    return plaintext.decode('utf-8')

# Example usage
private_key, public_key = generate_keypair()
print(f"Private Key: {private_key}")
print(f"Public Key: ({public_key.x}, {public_key.y})")

message = "Hello, ECC!"

# Encrypt the message
ephemeral_public_key, iv, ciphertext = ecies_encrypt(public_key, message)
print(f"Ciphertext: {ciphertext}")

# Decrypt the message
decrypted_message = ecies_decrypt(private_key, ephemeral_public_key, iv, ciphertext)
print(f"Decrypted Message: {decrypted_message}")
