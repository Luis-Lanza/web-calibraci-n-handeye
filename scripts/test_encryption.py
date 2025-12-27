from backend.utils.encryption import EncryptionService
import sys

def test_encryption():
    print("🔒 Testing Encryption Service (AES-256-GCM)...")
    
    original_text = "This is a secret message! 12345"
    print(f"Original Text: {original_text}")
    
    # Encrypt
    try:
        encrypted_text = EncryptionService.encrypt(original_text)
        print(f"✅ Encrypted: {encrypted_text}")
    except Exception as e:
        print(f"❌ Encryption failed: {e}")
        return

    # Decrypt
    try:
        decrypted_text = EncryptionService.decrypt(encrypted_text)
        print(f"✅ Decrypted: {decrypted_text}")
    except Exception as e:
        print(f"❌ Decryption failed: {e}")
        return

    # Verify
    if original_text == decrypted_text:
        print("✅ SUCCESS: Original and decrypted text match.")
    else:
        print("❌ FAILURE: Text mismatch.")

if __name__ == "__main__":
    test_encryption()
