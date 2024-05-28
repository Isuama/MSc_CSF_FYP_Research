def find_elliptic_curve_points(p, a, b):
    points = []
    for x in range(p):
        rhs = (x**3 + a * x + b) % p
        for y in range(p):
            lhs = (y * y) % p
            if lhs == rhs:
                points.append((x, y))
                print("",x,y)
    return points

# Example usage
p = 4969314367  # Prime number
a = 1   # Curve parameter a
b = 1   # Curve parameter b

points = find_elliptic_curve_points(p, a, b)
print(f"Points on the elliptic curve y^2 = x^3 + {a}x + {b} over GF({p}):")
for point in points:
    print(point)