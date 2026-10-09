# encryption.py
# Handles encrypting and decrypting data using Fernet (AES encryption)
# The encryption key is derived from the master password
# Without the master password, nothing can be decrypted
# Project: Secure Password Vault Pro
# Subject: Object Oriented Programming - 2nd Semester

import hashlib
import base64
from cryptography.fernet import Fernet


class Encryption:
    """Encrypts and decrypts text using a key derived from master password."""

    def __init__(self, master_password):
        # sha256 gives exactly 32 bytes, which Fernet requires
        raw_key      = hashlib.sha256(master_password.encode()).digest()
        encoded_key  = base64.urlsafe_b64encode(raw_key)
        self.cipher  = Fernet(encoded_key)

    def encrypt(self, plain_text):
        """Encrypt a plain text string. Returns encrypted string."""
        return self.cipher.encrypt(plain_text.encode()).decode()

    def decrypt(self, encrypted_text):
        """Decrypt an encrypted string. Returns original plain text."""
        return self.cipher.decrypt(encrypted_text.encode()).decode()

    def encrypt_bytes(self, data_bytes):
        """Encrypt raw bytes (used for file locking)."""
        return self.cipher.encrypt(data_bytes)

    def decrypt_bytes(self, encrypted_bytes):
        """Decrypt encrypted bytes (used for file unlocking)."""
        return self.cipher.decrypt(encrypted_bytes)
