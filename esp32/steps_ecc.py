#  **************** find element over a finite filed *****************************
def finite_field_elements(p):
    if p < 2:
        raise ValueError("p must be a prime number greater than 1")
    elements = list(range(p))
    return elements

try:
    p = int(input("Enter a prime number p for the finite field GF(p): "))
    elements = finite_field_elements(p)
    print(f"Elements of GF({p}): {elements}")
except ValueError as e:
    print(e)


# ****************** determine all the points on the curve ***************************************
def find_elliptic_curve_points(p, a, b):
    points = []
    for x in range(p):
        rhs = (x**3 + a * x + b) % p
        for y in range(p):
            lhs = (y * y) % p
            if lhs == rhs:
                points.append((x, y))
    return points

# Example usage
p = 11  # Prime number
a = 1   # Curve parameter a
b = 1   # Curve parameter b

points = find_elliptic_curve_points(p, a, b)
print(f"Points on the elliptic curve y^2 = x^3 + {a}x + {b} over GF({p}):")
for point in points:
    print(point)

# ************************ checking if a point falls on the curve *******************************************
def check_points_falls_on_curve(p, a, b, x, y):
    # Calculate the left-hand side (LHS) of the equation y^2 mod p
    lhs = (y * y) % p
    
    # Calculate the right-hand side (RHS) of the equation x^3 + ax + b mod p
    rhs = (x**3 + a * x + b) % p
    
    # Check if LHS is equal to RHS
    return lhs == rhs

# Example usage:
p = 11  # Prime number
a = 1   # Curve parameter a
b = 1   # Curve parameter b
x = 3   # x-coordinate
y = 8   # y-coordinate

is_point_on_curve = check_points_falls_on_curve(p, a, b, x, y)
print(f"Point ({x}, {y}) on elliptic curve y^2 = x^3 + {a}x + {b} over GF({p}): {is_point_on_curve}")

# ******************** find addition of two points when the two points are not equal ********************************
def modular_inverse(a, p):
    """ Return the modular inverse of a under modulo p """
    return pow(a, p - 2, p)

def find_delta(x1, y1, x2, y2, p):
    """ Calculate delta (δ) = (y2 - y1) / (x2 - x1) mod p """
    numerator = (y2 - y1) % p
    denominator = (x2 - x1) % p
    if denominator == 0:
        raise ValueError("Denominator is zero, points have the same x-coordinate")

    inverse_denominator = modular_inverse(denominator, p)
    delta = (numerator * inverse_denominator) % p
    return delta

# Example usage:
x1, y1 = 3, 8
x2, y2 = 6, 5
p = 11

try:
    delta = find_delta(x1, y1, x2, y2, p)
    print(f"Delta (δ) for points ({x1}, {y1}) and ({x2}, {y2}) over GF({p}) is: {delta}")
except ValueError as e:
    print(e)

# ***************** using delta, check if the resulting points are on the curve **********************************
def modular_inverse(a, p):
    """ Return the modular inverse of a under modulo p """
    return pow(a, p - 2, p)

def find_delta(x1, y1, x2, y2, p):
    """ Calculate delta (δ) = (y2 - y1) / (x2 - x1) mod p """
    numerator = (y2 - y1) % p
    denominator = (x2 - x1) % p
    if denominator == 0:
        raise ValueError("Denominator is zero, points have the same x-coordinate")

    inverse_denominator = modular_inverse(denominator, p)
    delta = (numerator * inverse_denominator) % p
    return delta

def is_point_on_curve(x, y, a, b, p):
    """ Check if the point (x, y) satisfies the elliptic curve equation y^2 ≡ x^3 + ax + b (mod p) """
    left_hand_side = (y ** 2) % p
    right_hand_side = (x ** 3 + a * x + b) % p
    return left_hand_side == right_hand_side

def elliptic_curve_point_addition(x1, y1, x2, y2, a, b, p):
    """ Calculate the resulting point (x3, y3) from adding points (x1, y1) and (x2, y2) on the elliptic curve """
    if not is_point_on_curve(x1, y1, a, b, p) or not is_point_on_curve(x2, y2, a, b, p):
        raise ValueError("One or both points are not on the elliptic curve")

    # Calculate delta (δ)
    delta = find_delta(x1, y1, x2, y2, p)
    
    # Calculate x3
    x3 = (delta**2 - x1 - x2) % p

    # Calculate y3
    y3 = (delta * (x1 - x3) - y1) % p

    # Check if the resulting point is on the curve
    if not is_point_on_curve(x3, y3, a, b, p):
        raise ValueError(f"Resulting point ({x3}, {y3}) is not on the elliptic curve")

    return x3, y3

# Example usage:
p = 11  # Prime number
a = 1   # Curve parameter a
b = 1   # Curve parameter b
x1, y1 = 3, 8  # First point coordinates
x2, y2 = 6, 5  # Second point coordinates

try:
    x3, y3 = elliptic_curve_point_addition(x1, y1, x2, y2, a, b, p)
    print(f"Resulting point (x3, y3) on the elliptic curve: ({x3}, {y3})")
except ValueError as e:
    print(e)

# ******************************************************* adding point with itself ( p + p ) when p is not equal to q ******************************
def modular_inverse(a, p):
    """ Return the modular inverse of a under modulo p """
    return pow(a, p - 2, p)

def find_delta(x1, y1, x2, y2, a, p):
    """ Calculate delta (δ) for elliptic curve point addition """
    if x1 == x2 and y1 == y2:
        # Use the point doubling formula
        numerator = (3 * x1 ** 2 + a) % p
        denominator = (2 * y1) % p
    else:
        # Use the point addition formula
        numerator = (y2 - y1) % p
        denominator = (x2 - x1) % p

    if denominator == 0:
        raise ValueError("Denominator is zero, cannot compute delta")

    inverse_denominator = modular_inverse(denominator, p)
    delta = (numerator * inverse_denominator) % p
    print("delta is:", delta)
    return delta

def is_point_on_curve(x, y, a, b, p):
    """ Check if the point (x, y) satisfies the elliptic curve equation y^2 ≡ x^3 + ax + b (mod p) """
    left_hand_side = (y ** 2) % p
    right_hand_side = (x ** 3 + a * x + b) % p
    print(f"left vs right handed ({left_hand_side}, {right_hand_side}) is on the elliptic curve")
    return left_hand_side == right_hand_side

def elliptic_curve_point_addition(x1, y1, x2, y2, a, b, p):
    """ Calculate the resulting point (x3, y3) from adding points (x1, y1) and (x2, y2) on the elliptic curve """
    if not is_point_on_curve(x1, y1, a, b, p) or not is_point_on_curve(x2, y2, a, b, p):
        raise ValueError("One or both points are not on the elliptic curve")

    # Calculate delta (δ)
    delta = find_delta(x1, y1, x2, y2, a, p)
    
    # Calculate x3
    x3 = (delta ** 2 - x1 - x2) % p

    # Calculate y3
    y3 = (delta * (x1 - x3) - y1) % p

    # Check if the resulting point is on the curve
    if not is_point_on_curve(x3, y3, a, b, p):
        raise ValueError(f"Resulting point ({x3}, {y3}) is not on the elliptic curve")

    return x3, y3

# Example usage:
p = 11  # Prime number
a = 1   # Curve parameter a
b = 1   # Curve parameter b
x1, y1 = 4, 6  # First point coordinates (for point doubling example)
x2, y2 = 4, 6  # Second point coordinates (same as the first point for doubling)

try:
    x3, y3 = elliptic_curve_point_addition(x1, y1, x2, y2, a, b, p)
    print(f"Resulting point ({x3}, {y3}) on the elliptic curve: ({x3}, {y3})")
except ValueError as e:
    print(e)


# ***************** compress and decompress point **************************
def compress_point(x, y, p):
    """ Compress the elliptic curve point (x, y) """
    # Determine the parity of y
    parity = y % 2  # 0 if y is even, 1 if y is odd
    
    # Return the compressed point as a tuple (x, parity)
    return (x, parity)

def decompress_point(x, parity, a, b, p):
    """ Decompress the elliptic curve point (x, parity) """
    # Calculate y^2 = x^3 + ax + b (mod p)
    y_squared = (x**3 + a * x + b) % p
    
    # Find y such that y^2 ≡ x^3 + ax + b (mod p)
    y = pow(y_squared, (p + 1) // 4, p)  # This works if p ≡ 3 (mod 4)
    
    if (y % 2) != parity:
        y = p - y
    
    return (x, y)

# Example usage:
p = 11  # Prime number
a = 1   # Curve parameter a
b = 1   # Curve parameter b
x, y = 4, 6  # Point coordinates

# Compress the point
compressed_point = compress_point(x, y, p)
print(f"Compressed point: {compressed_point}")

# Decompress the point
decompressed_point = decompress_point(*compressed_point, a, b, p)
print(f"Decompressed point: {decompressed_point}")

# ******************** generate public and private key *******************************************
import random

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

def generate_keys(generator_x, generator_y, a, b, p):
    """ Generate private and public keys """
    # Generate a random private key
    private_key = random.randint(1, p - 1)
    
    # Calculate the public key
    public_key_x, public_key_y = elliptic_curve_point_multiplication(private_key, generator_x, generator_y, a, p)
    
    return private_key, (public_key_x, public_key_y)

# Example usage:
p = 11  # Prime number
a = 1   # Curve parameter a
b = 1   # Curve parameter b
generator_x, generator_y = 2, 7  # Generator point coordinates

try:
    private_key, public_key = generate_keys(generator_x, generator_y, a, b, p)
    print(f"Private key: {private_key}")
    print(f"Public key: {public_key}")
except ValueError as e:
    print(e)

# ************** hashing message ***********************
message = b"ECC beats RSA"
 
import hashlib
hashHex = hashlib.sha1(message).hexdigest()
hash = int(hashHex, 16)
 
print("message: ", message) #message:  b'ECC beats RSA'
print("hash: ", hash) #hash:  320026739459778556085970613903841025917693204146




