from py_ecc.bn128 import G1, G2, pairing, multiply, add, neg, curve_order as p
import random

# ---------------------------------------------------------
# Utilities
# ---------------------------------------------------------
def mod_inverse(a, m):
    return pow(a, -1, m)

def eval_poly(poly, x, mod):
    result = 0
    for i, coeff in enumerate(poly):
        result = (result + coeff * pow(x, i, mod)) % mod
    return result

# ---------------------------------------------------------
# 1) CRS Generation (KEEP t for attack)
# ---------------------------------------------------------
def generate_kzg_crs(max_degree):
    t = random.randint(1, p - 1)

    powers_of_t = [1]
    for i in range(1, max_degree + 1):
        powers_of_t.append((powers_of_t[-1] * t) % p)

    crs_g1 = [multiply(G1, power) for power in powers_of_t]
    crs_g2 = [multiply(G2, 1), multiply(G2, t)]  # H, H^t

    return crs_g1, crs_g2, t

# ---------------------------------------------------------
# Commitment using CRS (honest way)
# ---------------------------------------------------------
def commit(poly, crs_g1):
    result = None
    for i, coeff in enumerate(poly):
        term = multiply(crs_g1[i], coeff)
        result = term if result is None else add(result, term)
    return result

# ---------------------------------------------------------
# Verification (no t used here)
# ---------------------------------------------------------
def verify(C, z, y, pi, crs_g2):
    H, H_t = crs_g2

    # Left: C - y*g
    g_y = multiply(G1, y)
    left = add(C, neg(g_y))

    # Right: H^t - zH
    H_z = multiply(H, z)
    right = add(H_t, neg(H_z))

    return pairing(H, left) == pairing(right, pi)

# ---------------------------------------------------------
# 2) Setup + Commit
# ---------------------------------------------------------
print("\n=== KZG Forgery Demonstration ===\n")

MAX_DEGREE = 16

crs_g1, crs_g2, t = generate_kzg_crs(MAX_DEGREE)

# Random polynomial
poly = [random.randint(0, p-1) for _ in range(MAX_DEGREE + 1)]

print(f"[Setup] Toxic waste t (kept for attack): {t}")


# Commit
C = commit(poly, crs_g1)
print("[Committer] Commitment C generated.\n")

# ---------------------------------------------------------
# 3) Attack: Forge fake proof using t
# ---------------------------------------------------------
z = random.randint(1, p-1)

# Real value
y_real = eval_poly(poly, z, p)

# Fake value (ensure it's wrong)
y_fake = random.randint(1, p-1)

print(f"[Attack] Target point: z = {z}")
print(f"[Truth ] Actual P(z) = {y_real}")
print(f"[Attack] Fake claim P(z) = {y_fake} (WRONG)\n")

# Compute P(t)
P_t = eval_poly(poly, t, p)

# Forge gamma
numerator = (P_t - y_fake) % p
denominator = (t - z) % p
gamma = (numerator * mod_inverse(denominator, p)) % p

# Forge proof
pi_fake = multiply(G1, gamma)

print("[Attack] Forged proof generated using leaked t.\n")

# ---------------------------------------------------------
# 4) Verification
# ---------------------------------------------------------
print("[Verifier] Verifying forged claim...")

if verify(C, z, y_fake, pi_fake, crs_g2):
    print("[Verifier] ACCEPTED (Forgery succeeded)")
else:
    print("[Verifier] REJECTED")

# ---------------------------------------------------------
# 5) Show mismatch explicitly
# ---------------------------------------------------------
print("\n=== Ground Truth Check ===")
if y_fake != y_real:
    print("Claimed value is WRONG")
    print(f"Claimed: {y_fake}")
    print(f"Actual : {y_real}")
else:
    print("Rare collision (unlikely)")

print("\nAttack Summary:")
print("Verifier accepted a FALSE statement due to knowledge of t.")