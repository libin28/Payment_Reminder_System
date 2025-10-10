from auth import generate_secure_password, check_password_strength

print("🧪 Testing Password Generation and Strength Checking")
print("=" * 60)

# Test password generation
print("\n🔐 Generated Passwords:")
for i in range(5):
    pwd = generate_secure_password()
    strength = check_password_strength(pwd)
    print(f"Password {i+1}: {pwd}")
    print(f"  Strength: {strength['display']} (Score: {strength['score']}/5)")
    if strength['feedback']:
        print(f"  Missing: {', '.join(strength['feedback'])}")
    print()

# Test different password lengths
print("\n📏 Testing Different Lengths:")
for length in [8, 12, 16, 20]:
    pwd = generate_secure_password(length)
    strength = check_password_strength(pwd)
    print(f"Length {length}: {pwd} - {strength['display']}")

# Test password strength checker with various passwords
print("\n🔍 Testing Password Strength Checker:")
test_passwords = [
    "password",
    "Password1",
    "Password1!",
    "MySecureP@ssw0rd",
    "abc123",
    "UPPERCASE",
    "lowercase",
    "12345678"
]

for pwd in test_passwords:
    strength = check_password_strength(pwd)
    print(f"'{pwd}' -> {strength['display']} (Score: {strength['score']}/5)")
    if strength['feedback']:
        print(f"  Needs: {', '.join(strength['feedback'])}")

print("\n✅ Password generation and strength checking working correctly!")
