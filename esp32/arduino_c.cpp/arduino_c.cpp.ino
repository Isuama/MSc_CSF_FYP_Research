#include <dummy.h>

#include <Arduino.h>
#include <stdio.h>
#include <time.h>  // for clock
// #include <BigNumber.h>

struct Point {
    BigNumber x;
    BigNumber y;
    Point(BigNumber x_val = 0, BigNumber y_val = 0) {
      x = x_val;
      y = y_val;
    }
};

struct Keys {
  BigNumber private_key;
  Point public_key;
};

struct signature{
  BigNumber r;
  BigNumber s;
};

// Elliptic Curve Parameters
//128
// long P = 115792089237316195423570985008687907853269984665640564039457584007913129639935;
// long A = 115792089237316195423570985008687907853269984665640564039457584007913129639932;
// long B = 104435791132094804968412250928839515403108655044084993145722015010646329212307;
// long Gx = 11459917076332302411809324954468629674414944373310402161832570714756312338886; // generator point x
// long Gy = 93734360075520105935896615051713239724156644137986295677537775776576196419267; // generator point y
// long N = 115792089084919303222329660308867048659239241117203725042929404535774633321621; // random number < P

Point G(Gx, Gy);

// const long A = 1;
// const long B = 1;
// const long P = 11;
// const long Gx = 3; // generator point x
// const long Gy = 8; // generator point y
// Point G(Gx, Gy);
// const long Hx = 6; // another point x
// const long Hy = 5; // another point y
// Point H(Hx, Hy);

// long P = 11;
// long A = 1;
// long B = 1;
// const long Gx = 1; // generator point x
// const long Gy = 5; // generator point y
// Point G(Gx, Gy);
// long N = 2;

// Define the constants as BigNumber
  BigNumber P("11");
  BigNumber A("1");
  BigNumber B("1");
  const BigNumber Gx("1");
  const BigNumber Gy("5");
  BigNumber N("2");



// Function prototypes
// Point elliptic_curve_point_addition(long x1, long y1, long x2, long y2);
// long modular_inverse(long a, long p);

void setup() {
    // Initialize serial communication at 9600 bits per second
    Serial.begin(9600);
    delay(1000); // Wait for 1 second
    
    // Initialize the BigNumber library
    BigNumber::begin();
    
    //// Perform elliptic curve point addition and store the result
    //Point result = elliptic_curve_point_addition(G.x, G.y, H.x, H.y);
    //// Print the result to the Serial Monitor
    // Serial.print("The resulting point is: (");
    // Serial.print(result.x);
    // Serial.print(", ");
    // Serial.print(result.y);
    // Serial.println(")");

    // // Perform elliptic curve point doubling and store the result
    // long k = N;
    // Point result = elliptic_curve_point_multiplication(k,G.x, G.y);
    // // Print the result to the Serial Monitor
    // Serial.print("The resulting point is when point doubling: (");
    // Serial.print(result.x);
    // Serial.print(", ");
    // Serial.print(result.y);
    // Serial.println(")");

    clock_t start_time, end_time;
    Keys keys;
    double cpu_time_used;
    start_time = clock();
    keys = generate_keypair();
    end_time = clock();
    cpu_time_used = ((double) (end_time - start_time)) / CLOCKS_PER_SEC;
    Serial.print("private key:");
    Serial.println(keys.private_key);
    Serial.print("public key:");
    Serial.println(keys.public_key.y);
    printf("Keypair Generation Time: %f seconds\n", cpu_time_used);
}

void loop() {
    // Nothing to do here
}

Point elliptic_curve_point_addition(BigNumber x1, BigNumber y1, BigNumber x2, BigNumber y2) {
  BigNumber numerator, denominator, delta, x3, y3;
  if (x1 == x2 && y1 == y2) {
    // Point doubling
    numerator = (3 * x1 * x1 + A) % P;
    denominator = (2 * y1) % P;
  } else {
    // Point addition
    numerator = (y2 - y1 + P) % P;
    denominator = (x2 - x1) % P;
  }
  BigNumber inverse_denominator = modular_inverse(denominator, P);
  delta = (numerator * inverse_denominator) % P;
  x3 = (delta * delta - x1 - x2) % P;
  y3 = (delta * (x1 - x3) - y1) % P;
  // Ensure the result is non-negative
  if (x3 < 0) x3 += P;
  if (y3 < 0) y3 += P;
  // Serial.print("Point addition returns: (");
  // Serial.print(x3);
  // Serial.print(",");
  // Serial.print(y3);
  // Serial.println(")");
  return Point(x3, y3);
}

BigNumber modular_inverse(BigNumber a, BigNumber p) {
    BigNumber result = 1;
    BigNumber exponent = p - 2;
    while (exponent > 0) {
        if (exponent % 2 == 1) {
            result = (result * a) % p;
        }
        a = (a * a) % p;
        exponent /= 2;
    }
    return result;
}

Point elliptic_curve_point_multiplication(BigNumber k, BigNumber x, BigNumber y) {
  // Serial.print("received x as:");
  // Serial.println(x);
  // Serial.print("received y as:");
  // Serial.println(y);
  // Initialize result with the original point
  Point temp_point;
  temp_point.x = x;
  temp_point.y = y;

  char k_bin[256];
  itoa(k, k_bin, 2);  
  BigNumber length_of_k_bin = strlen(k_bin);

  for (BigNumber i = 1; i < length_of_k_bin; i++) {
    temp_point = elliptic_curve_point_addition(temp_point.x, temp_point.y, temp_point.x, temp_point.y);
    if(k_bin[i] == '1'){
      temp_point = elliptic_curve_point_addition(temp_point.x, temp_point.y, x, y);
    }
  }
  // Return the final point (stored in temp variables)
  return temp_point;  // C doesn't support returning multiple values directly
}

 BigNumber random_int_in_range(BigNumber lower, BigNumber upper) {
  BigNumber random_number;
    do {
        random_number = rand() % (upper - lower) + 1; // Generate random number in the range [1, max-1]
    } while (random_number <= 0 || random_number >= upper);

    return random_number;
}

Keys generate_keypair() {
    BigNumber private_key = random_int_in_range(1, P);
    Point public_key = elliptic_curve_point_multiplication(private_key,G.x, G.y);
    Keys keys;
    keys.private_key = private_key;
    keys.public_key = public_key;
    return keys;
    // // Seed the random number generator for better randomness
    // srand(time(NULL));

    // long private_key = random_int_in_range(1, P - 1);  // Generate random private key
    // // Calculate public key (x-coordinate only)
    // Point public_key = elliptic_curve_point_multiplication(private_key, G.x, G.y);
    // Serial.print(public_key.x);
    // struct Keys genrated_keys;
    // genrated_keys.private_key = private_key;
    // genrated_keys.public_key = public_key;
    // Serial.print("private key iunside function:");
    // Serial.println(private_key);
    // Serial.print("public key iunside function:");
    // Serial.println(public_key.x);

    // return genrated_keys;  // Return only x-coordinate (modify if both are needed)
}

// int sign_message(int private_key, const char *message, int N, int Gx, int Gy, int A, int P) {
//     // Hash the message (assumed to be done externally)
//     // Replace this with your message hashing implementation (e.g., using SHA256)
//     int h = /* hash value of the message */;

//     int r = 0, s = 0;
//     while (r == 0 || s == 0) {
//         // Generate a random number k
//         k = random_int_in_range(1, N - 1);

//         // Calculate the random point R = k * G and take its x-coordinate
//         int R_x = elliptic_curve_point_multiplication(k, Gx, Gy, A, P);

//         // Calculate signature component r (avoiding potential modulo bias)
//         r = R_x % N;
//         if (r == 0) continue;  // Reject r = 0 (avoid potential signature malleability)

//         // Calculate the signature proof s
//         s = (modular_inverse(k, N) * (h + r * private_key)) % N;
//         if (s == 0) continue;  // Reject s = 0 (avoid potential signature malleability)
//     }

//     // Return the signature (modify return type if needed)
//     printf("Signature: (r, s) = (%d, %d)\n", r, s);
//     return 0;  // Modify return type to include both r and s if needed
// }

// int verify_signature(const char *message, int signature_r, int signature_s, int public_key_x, int public_key_y, int N, int Gx, int Gy, int A, int P) {
//     // Hash the message (assumed to be done externally)
//     // Replace this with your message hashing implementation (e.g., using SHA256)
//     int z = /* hash value of the message */;

//     // Calculate w (modular inverse of s)
//     int w = modular_inverse(signature_s, N);
//     if (w == 0) {
//         return 0;  // Invalid signature (modular inverse not found)
//     }

//     // Calculate u1 and u2
//     int u1 = (z * w) % N;
//     int u2 = (signature_r * w) % N;

//     // Calculate the point P = u1 * G + u2 * public_key
//     int u1_x = elliptic_curve_point_multiplication(u1, Gx, Gy, A, P);
//     int u1_y = elliptic_curve_point_multiplication(u1, Gy, -Gy, A, P);  // Handle negative y for point doubling optimization
//     int u2_x = elliptic_curve_point_multiplication(u2, public_key_x, public_key_y, A, P);
//     int u2_y = elliptic_curve_point_multiplication(u2, public_key_y, -public_key_y, A, P);  // Handle negative y for point doubling optimization
//     int p_x = elliptic_curve_point_addition(u1_x, u1_y, u2_x, u2_y, A, P);

//     // Verify the signature
//     return (p_x % N == signature_r);
// }