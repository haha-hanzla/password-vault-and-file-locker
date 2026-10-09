# password_manager.py
# Full CRUD operations for stored passwords
# Also keeps login history log
# Project: Secure Password Vault Pro
# Subject: Object Oriented Programming - 2nd Semester

import json
import os
from datetime import datetime
from password_entry import PasswordEntry
from encryption import Encryption


class PasswordManager:
    """Manages all password entries with add, get, update, delete, search."""

    def __init__(self, encryption, vault_file="vault_data.json", log_file="login_log.json"):
        self.encryption = encryption
        self.vault_file = vault_file
        self.log_file   = log_file
        self.entries    = []
        self._load_from_file()

    # ── file operations ──────────────────────────────────────────
    def _load_from_file(self):
        """Load entries from JSON file into memory."""
        if not os.path.exists(self.vault_file):
            self.entries = []
            return
        try:
            with open(self.vault_file, "r") as f:
                data = json.load(f)
            self.entries = [PasswordEntry.from_dict(item)
                            for item in data]
        except (json.JSONDecodeError, KeyError):
            self.entries = []
            
            """
            self.entries = []
            for item in data:
                entry = PasswordEntry.from_dict(item)
                self.entries.append(entry)"""

    def _save_to_file(self):
        """Save all entries to JSON file."""
        data = [entry.to_dict()
                for entry in self.entries]
        with open(self.vault_file, "w") as f:
            json.dump(data, f, indent=4)

    # ── private helper ───────────────────────────────────────────
    def _find_entry(self, site):
        """Find entry by site name (case-insensitive). Returns entry or None."""
        for entry in self.entries:
            if entry.site.lower() == site.lower():
                return entry
        return None

    def _today(self):
        """Return today's date as a readable string."""
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── CRUD operations ──────────────────────────────────────────
    def add_password(self, site, username, plain_password):
        """Add new password entry. Asks before overwriting existing one."""
        existing = self._find_entry(site)

        if existing is not None:
            print(f"\n  [!] Entry for '{site}' already exists.")
            choice = input("      Overwrite it? (y/n): ").strip().lower()
            if choice != 'y':
                print("  Cancelled.")
                return False
            self.entries.remove(existing)

        encrypted = self.encryption.encrypt(plain_password)
        new_entry = PasswordEntry(site, username, encrypted, self._today())
        self.entries.append(new_entry)
        self._save_to_file()
        return True

    def get_password(self, site):
        """Return decrypted password entry dict, or None if not found."""
        entry = self._find_entry(site)
        if entry is None:
            return None
        return {
            "site"    : entry.site,
            "username": entry.username,
            "password": self.encryption.decrypt(entry.encrypted_password),
            "added_on": entry.added_on
        }

    def update_password(self, site, new_plain_password):
        """Update password for existing site."""
        entry = self._find_entry(site)
        if entry is None:
            return False
        entry.encrypted_password = self.encryption.encrypt(new_plain_password)
        entry.added_on = self._today() + " (updated)"
        self._save_to_file()
        return True

    def update_username(self, site, new_username):
        """Update username for existing site."""
        entry = self._find_entry(site)
        if entry is None:
            return False
        entry.username = new_username
        self._save_to_file()
        return True

    def delete_password(self, site):
        """Delete entry by site name."""
        entry = self._find_entry(site)
        if entry is None:
            return False
        self.entries.remove(entry)
        self._save_to_file()
        return True

    def list_all(self):
        """Return all entries (passwords stay encrypted)."""
        return self.entries

    def search(self, keyword):
        """Search entries by partial site name."""
        kw = keyword.lower()
        return [e for e in self.entries if kw in e.site.lower()]

    def count(self):
        """Return total number of saved passwords."""
        return len(self.entries)

    def find_duplicates(self):
        """
        Find entries that share the same password.
        Returns list of groups of sites with duplicate passwords.
        Useful security feature - warns user about password reuse.
        """
        # decrypt all and group by password value
        password_map = {}  # plain_password -> list of sites
        for entry in self.entries:
            try:
                plain = self.encryption.decrypt(entry.encrypted_password)
                if plain not in password_map:
                    password_map[plain] = []
                password_map[plain].append(entry.site)
            except Exception:
                continue

        # only return groups where same password is used more than once
        duplicates = {pw: sites for pw, sites in password_map.items() if len(sites) > 1}
        return duplicates

    # ── login history log ────────────────────────────────────────
    def log_login(self, success):
        """Save login attempt to history log."""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    log = json.load(f)
            else:
                log = []

            log.append({
                "time"   : self._today(),
                "status" : "SUCCESS" if success else "FAILED"
            })

            # keep only last 20 entries
            if len(log) > 20:
                log = log[-20:]

            with open(self.log_file, "w") as f:
                json.dump(log, f, indent=4)

        except Exception:
            pass  # logging should never crash the main program

    def get_login_history(self):
        """Return list of recent login attempts."""
        try:
            with open(self.log_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
