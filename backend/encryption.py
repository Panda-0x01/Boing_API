from cryptography.fernet import Fernet
from config import settings
import base64

def get_cipher():
    """Get Fernet cipher instance"""
    key = settings.ENCRYPTION_KEY
    if not key:
        # Generate a key if not set (for development only)
        key = Fernet.generate_key().decode()
        print(f"WARNING: Using generated encryption key. Set ENCRYPTION_KEY in .env: {key}")
    
    if isinstance(key, str):
        key = key.encode()
    
    return Fernet(key)

def encrypt_secret(secret: str) -> str:
    """Encrypt API secret"""
    cipher = get_cipher()
    encrypted = cipher.encrypt(secret.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_secret(encrypted_secret: str) -> str:
    """Decrypt API secret"""
    cipher = get_cipher()
    encrypted_bytes = base64.b64decode(encrypted_secret.encode())
    decrypted = cipher.decrypt(encrypted_bytes)
    return decrypted.decode()
