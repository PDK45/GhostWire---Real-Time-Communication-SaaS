import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from stegano import lsb
import secrets

def _derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derives a url-safe base64 encoded 32-byte key from a passphrase and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
    return key

def encrypt_message(message: str, passphrase: str) -> str:
    """
    Encrypts a message using a key derived from the passphrase.
    Returns format: 'salt_b64:encrypted_token'
    """
    if not passphrase:
        raise ValueError("Passphrase is required for encryption.")
        
    salt = secrets.token_bytes(16)
    key = _derive_key(passphrase, salt)
    f = Fernet(key)
    
    if isinstance(message, str):
        message = message.encode('utf-8')
        
    token = f.encrypt(message)
    
    # Return salt and token separated by :
    salt_b64 = base64.urlsafe_b64encode(salt).decode('utf-8')
    token_str = token.decode('utf-8')
    
    return f"{salt_b64}:{token_str}"

def decrypt_message(encrypted_payload: str, passphrase: str) -> str:
    """
    Decrypts a payload using the provided passphrase.
    Expects format: 'salt_b64:encrypted_token'
    """
    if not passphrase:
        raise ValueError("Passphrase is required for decryption.")
        
    try:
        parts = encrypted_payload.split(':')
        if len(parts) != 2:
            return None # Invalid format
            
        salt_b64, token = parts
        salt = base64.urlsafe_b64decode(salt_b64)
        
        key = _derive_key(passphrase, salt)
        f = Fernet(key)
        
        decrypted_data = f.decrypt(token.encode('utf-8'))
        return decrypted_data.decode('utf-8')
    except Exception as e:
        print(f"Decryption failed: {e}")
        return None

def hide_data_in_image(image_path, secret_data):
    """Hides data in image. secret_data is already the encrypted string."""
    try:
        secret = lsb.hide(image_path, secret_data)
        return secret
    except Exception as e:
        print(f"Steganography error: {e}")
        return None

def reveal_data_from_image(image_path):
    """Reveals hidden data (the encrypted payload) from an image."""
    try:
        clear_message = lsb.reveal(image_path)
        return clear_message
    except Exception as e:
        print(f"Steganography reveal error: {e}")
        return None
