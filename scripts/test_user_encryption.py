from backend.models.user import User
from backend.utils.encryption import EncryptionService

def test_user_encryption():
    print("🔒 Testing User Model Encryption Integration...")
    
    # Create a dummy user instance (not saved to DB, just in memory)
    user = User(username="test_user", email="test@example.com")
    
    secret = "my_super_secret_key_123"
    print(f"Original Secret: {secret}")
    
    # 1. Set the secret (should encrypt it)
    user.set_mfa_secret(secret)
    print(f"Stored in User.mfa_secret (Encrypted): {user.mfa_secret}")
    
    # Verify it's not stored in plain text
    if user.mfa_secret == secret:
        print("❌ FAILURE: Secret stored in plain text!")
        return
    else:
        print("✅ Secret is NOT stored in plain text.")
        
    # 2. Get the secret (should decrypt it)
    retrieved_secret = user.get_mfa_secret()
    print(f"Retrieved Secret (Decrypted): {retrieved_secret}")
    
    # Verify match
    if retrieved_secret == secret:
        print("✅ SUCCESS: Retrieved secret matches original.")
    else:
        print("❌ FAILURE: Retrieved secret does not match.")

if __name__ == "__main__":
    test_user_encryption()
