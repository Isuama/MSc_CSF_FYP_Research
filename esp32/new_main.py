import hashlib
import random

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

def compress_point(point):
    return (point.x, point.y % 2)

def decompress_point(x, y_parity):
    y_square = (x**2 + a * x + b) % p
    y_root = pow(y_square, (p + 1) // 4, p)  # p ≡ 3 (mod 4) optimization
    if y_root % 2 != y_parity:
        y_root = p - y_root
    return Point(x, y_root)

def map_message_to_point_koblitz(message):
    """Map a message to an ECC point using Koblitz's method."""
    counter = 0
    while True:
        hasher = hashlib.sha256()
        hasher.update(message.encode('utf-8') + counter.to_bytes(1, 'big'))
        x = int.from_bytes(hasher.digest(), 'big') % p
        y_square = (x**2 + a * x + b) % p
        try:
            y = pow(y_square, (p + 1) // 4, p)
            if (y * y) % p == y_square:
                return Point(x, y), counter
        except ValueError:
            pass
        counter += 1

def point_to_message_koblitz(point, message):
    """Recover the message from the ECC point using Koblitz's method."""
    x = point.x
    counter = 0
    while True:
        hasher = hashlib.sha256()
        hasher.update(message.encode('utf-8') + counter.to_bytes(1, 'big'))
        test_digest = int.from_bytes(hasher.digest(), 'big') % p
        if test_digest == x:
            return message
        counter += 1
    return None

# Example usage
private_key, public_key = generate_keypair()
print(f"Private Key: {private_key}")
print(f"Public Key: ({public_key.x}, {public_key.y})")

message = "Hello ammata hufu{}"
point, counter = map_message_to_point_koblitz(message)
print(f"Mapped Point: {point}")

# Compress and decompress the point (optional)
compressed = compress_point(point)
print(f"Compressed Point: {compressed}")

decompressed = decompress_point(compressed[0], compressed[1])
print(f"Decompressed Point: ({decompressed.x}, {decompressed.y})")

# Recover the message from the point
recovered_message = point_to_message_koblitz(point, message)
print(f"Recovered Message: {recovered_message}")
