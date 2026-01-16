"""
Password hash generator
"""
import os
import sys
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_passwords() -> list[str]:
    if len(sys.argv) > 1:
        return [item.strip() for item in sys.argv[1:] if item.strip()]

    env_passwords = os.getenv("PASSWORDS", "")
    if env_passwords:
        return [item.strip() for item in env_passwords.split(",") if item.strip()]

    return []


passwords = get_passwords()
if not passwords:
    print("Usage:")
    print("  python backend/generate_password.py <password1> <password2> ...")
    print("  or set env PASSWORDS=pass1,pass2")
    sys.exit(1)

print("=" * 60)
print("Password hashes generated:")
print("=" * 60)
for value in passwords:
    hashed = pwd_context.hash(value)
    print(f"\npassword: {value}")
    print(f"hash: {hashed}")
print("\n" + "=" * 60)
