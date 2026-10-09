# password_entry.py
# Data model for a single password record
# Project: Secure Password Vault Pro
# Subject: Object Oriented Programming - 2nd Semester

class PasswordEntry:
    """Represents one saved password in the vault."""

    def __init__(self, site, username, encrypted_password, added_on=None):
        self.site               = site
        self.username           = username
        self.encrypted_password = encrypted_password
        self.added_on           = added_on  # date string when it was added

    def to_dict(self):
        """Convert to dictionary for JSON storage."""
        return {
            "site"     : self.site,
            "username" : self.username,
            "password" : self.encrypted_password,
            "added_on" : self.added_on
        }

    @classmethod
    def from_dict(cls, data):
        """Create PasswordEntry from a dictionary (loaded from JSON)."""
        return cls(
            data["site"],
            data["username"],
            data["password"],
            data.get("added_on", "Unknown")
        )

    def __str__(self):
        return f"  {self.site}  |  {self.username}  |  Added: {self.added_on}"
