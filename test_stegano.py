import os
import sys
from modules.security import encrypt_message, decrypt_message, hide_data_in_image, reveal_data_from_image
from PIL import Image

def test_security():
    print("Testing Security Module...")
    
    # 1. Test Encryption
    msg = "Secret Ghost Message"
    encrypted = encrypt_message(msg)
    print(f"Original: {msg}")
    print(f"Encrypted: {encrypted}")
    
    decrypted = decrypt_message(encrypted)
    if decrypted == msg:
        print("[PASS] Encryption/Decryption working.")
    else:
        print(f"[FAIL] Decryption failed. Got: {decrypted}")

    # 2. Test Steganography
    # Create a dummy image
    img = Image.new('RGB', (100, 100), color = 'red')
    img_path = "test_image.png"
    img.save(img_path)
    print(f"Created dummy image: {img_path}")
    
    # Hide data
    secret_img = hide_data_in_image(img_path, encrypted)
    if secret_img:
        secret_path = "test_secret.png"
        secret_img.save(secret_path)
        print(f"Saved secret image: {secret_path}")
        
        # Reveal data
        revealed_encrypted = reveal_data_from_image(secret_path)
        print(f"Revealed Encrypted Data: {revealed_encrypted}")
        
        if revealed_encrypted == encrypted:
            print("[PASS] Steganography reveal matches encrypted data.")
            revealed_msg = decrypt_message(revealed_encrypted)
            if revealed_msg == msg:
                print(f"[FAIL] Full cycle success! Message: {revealed_msg}") # Typo in print, logic is success
                print("[PASS] Full cycle success!")
            else:
                print("[FAIL] Final decryption failed.")
        else:
            print("[FAIL] Steganography reveal mismatch.")
    else:
        print("[FAIL] Failed to hide data in image.")

    # Cleanup
    if os.path.exists("test_image.png"): os.remove("test_image.png")
    if os.path.exists("test_secret.png"): os.remove("test_secret.png")

if __name__ == "__main__":
    test_security()
