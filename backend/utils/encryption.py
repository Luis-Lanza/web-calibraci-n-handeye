import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from backend.config import settings
import base64

# Seguridad A02: Cifrado AES-256-GCM para datos sensibles en reposo

class EncryptionService:
    _key = None

    @classmethod
    def get_key(cls):
        if cls._key is None:
            # Use SECRET_KEY to derive a 32-byte key for AES-256
            # In production, this should be a separate key
            key_material = settings.SECRET_KEY.encode()
            if len(key_material) < 32:
                # Pad if too short (not ideal but works for demo)
                key_material = key_material.ljust(32, b'0')
            cls._key = key_material[:32]
        return cls._key

    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        """Encrypt string using AES-256-GCM."""
        if not plaintext:
            return None
        
        aesgcm = AESGCM(cls.get_key())
        nonce = os.urandom(12)
        data = plaintext.encode()
        
        ciphertext = aesgcm.encrypt(nonce, data, None)
        
        # Return as base64: nonce + ciphertext
        return base64.b64encode(nonce + ciphertext).decode('utf-8')

    @classmethod
    def decrypt(cls, ciphertext_b64: str) -> str:
        """Decrypt base64 encoded string using AES-256-GCM."""
        if not ciphertext_b64:
            return None
            
        try:
            raw = base64.b64decode(ciphertext_b64)
            nonce = raw[:12]
            ciphertext = raw[12:]
            
            aesgcm = AESGCM(cls.get_key())
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        except Exception:
            return None
