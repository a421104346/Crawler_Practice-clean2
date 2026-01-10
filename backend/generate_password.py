"""
Password hash generator
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generate password hashes
admin_hash = pwd_context.hash("admin123")
demo_hash = pwd_context.hash("demo123")

print("=" * 60)
print("Password hashes generated:")
print("=" * 60)
print(f"\nadmin user (password: admin123):")
print(f"Hash: {admin_hash}")
print(f"\ndemo user (password: demo123):")
print(f"Hash: {demo_hash}")
print("\n" + "=" * 60)

# Verify hashes
print("\nVerification test:")
print(f"admin123 verify: {pwd_context.verify('admin123', admin_hash)}")
print(f"demo123 verify: {pwd_context.verify('demo123', demo_hash)}")
