# master_lock.py
# Handles master password setup, verification, and account recovery info
# Uses PBKDF2 hashing with salt - industry standard for password storage
# Project: Secure Password Vault Pro
# Subject: Object Oriented Programming - 2nd Semester

import hashlib
import os
import json


class MasterLock:
    """
    Manages the master password.
    Stores: hashed password + salt + recovery email
    Never stores the actual master password.
    """

    HASH_ITERATIONS = 100000  # higher = slower brute force attacks

    def __init__(self, lock_file="master_key.json"):
        self.lock_file = lock_file

    # ── private helper ──────────────────────────────────────────
    def _hash_password(self, password, salt):
        """Hash password with salt using PBKDF2-SHA256."""
        hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, self.HASH_ITERATIONS)
        return hashed.hex()

    # ── public methods ──────────────────────────────────────────
    def setup_master(self, master_password, recovery_email):
        """
        First-time setup.
        Saves hashed password + salt + recovery email.
        """
        salt   = os.urandom(16)
        hashed = self._hash_password(master_password, salt)

        data = {
            "salt"           : salt.hex(),
            "hash"           : hashed,
            "recovery_email" : recovery_email   # stored in plain text (not sensitive)
        }

        with open(self.lock_file, "w") as f:
            json.dump(data, f, indent=4)

    def verify_master(self, master_password):
        """Return True if the entered password matches saved hash."""
        try:
            with open(self.lock_file, "r") as f :
                data = json.load(f)

            salt         = bytes.fromhex(data["salt"])
            entered_hash = self._hash_password(master_password, salt)
            return entered_hash == data["hash"]

        except FileNotFoundError:
            return False

    def is_setup(self):
        """Return True if master password has been set."""
        return os.path.exists(self.lock_file)
