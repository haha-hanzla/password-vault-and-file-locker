# file_locker.py
# Locks (encrypts) and unlocks (decrypts) any file on disk
# A locked file gets the extension .vaultlocked and cannot be opened normally
# Unlocking restores the original file
#
# Uses the same Encryption class from our vault - good OOP composition!
#
# Project: Secure Password Vault Pro
# Subject: Object Oriented Programming - 2nd Semester

import os
import json
from encryption import Encryption


class FileLocker:
    """
    Locks and unlocks files using vault encryption.
    Locked files are stored as .vaultlocked files.
    A metadata file tracks which files are locked.
    """

    LOCK_EXTENSION   = ".vaultlocked"
    METADATA_FILE    = "locked_files.json"

    def __init__(self, encryption):
        self.encryption    = encryption   # Encryption object passed in (composition)
        self.locked_files  = self._load_metadata()

    # ── metadata (track which files are locked) ──────────────────
    def _load_metadata(self):
        """Load list of locked files from metadata file."""
        if os.path.exists(self.METADATA_FILE):
            try:
                with open(self.METADATA_FILE, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, KeyError):
                return {}
        return {}

    def _save_metadata(self):
        """Save locked files list to metadata file."""
        with open(self.METADATA_FILE, "w") as f:
            json.dump(self.locked_files, f, indent=4)

    # ── lock a file ──────────────────────────────────────────────
    def lock_file(self, file_path):
        """
        Encrypt a file and replace it with a .vaultlocked version.
        Original file is deleted after locking.
        """
        file_path = os.path.abspath(file_path)  # get full path

        # validations
        if not os.path.exists(file_path):
            print(f"  [!] File not found: {file_path}")
            return False

        if file_path.endswith(self.LOCK_EXTENSION):
            print("  [!] File is already locked.")
            return False

        if file_path in self.locked_files:
            print("  [!] This file is already tracked as locked.")
            return False

        # read original file as bytes
        try:
            with open(file_path, "rb") as f:
                original_bytes = f.read()
        except PermissionError:
            print("  [!] Permission denied. Cannot read file.")
            return False

        # encrypt the file bytes
        encrypted_bytes = self.encryption.encrypt_bytes(original_bytes)

        # save encrypted version as .vaultlocked file
        locked_path = file_path + self.LOCK_EXTENSION
        with open(locked_path, "wb") as f:
            f.write(encrypted_bytes)

        # delete the original file
        os.remove(file_path)

        # track it in metadata
        original_name = os.path.basename(file_path)
        file_size_kb  = round(len(original_bytes) / 1024, 2)

        self.locked_files[locked_path] = {
            "original_path"  : file_path,
            "original_name"  : original_name,
            "locked_path"    : locked_path,
            "size_kb"        : file_size_kb
        }
        self._save_metadata()

        print(f"  [OK] File locked: {original_name}")
        print(f"       Locked file: {os.path.basename(locked_path)}")
        return True

    # ── unlock a file ────────────────────────────────────────────
    def unlock_file(self, locked_path):
        """
        Decrypt a .vaultlocked file and restore the original.
        Locked file is deleted after unlocking.
        """
        locked_path = os.path.abspath(locked_path)

        if not os.path.exists(locked_path):
            print(f"  [!] Locked file not found: {locked_path}")
            return False

        if locked_path not in self.locked_files:
            print("  [!] This file was not locked by this vault.")
            return False

        # get original file path from metadata
        original_path = self.locked_files[locked_path]["original_path"]
        original_name = self.locked_files[locked_path]["original_name"]

        # read encrypted bytes
        try:
            with open(locked_path, "rb") as f:
                encrypted_bytes = f.read()
        except PermissionError:
            print("  [!] Permission denied. Cannot read locked file.")
            return False

        # decrypt
        try:
            decrypted_bytes = self.encryption.decrypt_bytes(encrypted_bytes)
        except Exception:
            print("  [X] Decryption failed. Wrong master password?")
            return False

        # write back the original file
        with open(original_path, "wb") as f:
            f.write(decrypted_bytes)

        # delete the locked file
        os.remove(locked_path)

        # remove from metadata
        del self.locked_files[locked_path]
        self._save_metadata()

        print(f"  [OK] File unlocked: {original_name}")
        print(f"       Restored to  : {original_path}")
        return True

    # ── list locked files ────────────────────────────────────────
    def list_locked_files(self):
        """Return list of currently locked files."""
        return list(self.locked_files.values())

    def count(self):
        """Return number of locked files."""
        return len(self.locked_files)
