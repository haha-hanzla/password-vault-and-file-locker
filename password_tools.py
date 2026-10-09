# password_tools.py
# Two classes for generating and checking passwords
# Project: Secure Password Vault Pro
# Subject: Object Oriented Programming - 2nd Semester

import secrets
import string
import re


class PasswordGenerator:
    """Generates strong random passwords."""

    LOWERCASE = string.ascii_lowercase
    UPPERCASE = string.ascii_uppercase
    DIGITS    = string.digits
    SYMBOLS   = "!@#$%^&*()-_=+[]{}|;:,."

    def generate(self, length=16, use_symbols=True, use_digits=True):
        """Generate a random password with required character types."""
        if length < 8:
            length = 8

        char_pool = self.LOWERCASE + self.UPPERCASE

        if use_digits:
            char_pool += self.DIGITS
        if use_symbols:
            char_pool += self.SYMBOLS

        # keep trying until all required types are present
        while True:
            password   = ''.join(secrets.choice(char_pool) for _ in range(length))

            has_lower  = any(c in self.LOWERCASE for c in password)
            has_upper  = any(c in self.UPPERCASE for c in password)
            has_digit  = any(c in self.DIGITS    for c in password) if use_digits  else True
            has_symbol = any(c in self.SYMBOLS   for c in password) if use_symbols else True

            if has_lower and has_upper and has_digit and has_symbol:
                return password

    def generate_memorable(self, num_words=4):
        """Generate a memorable passphrase: Word-Word-Word-1234."""
        words = [
            "apple", "tiger", "river", "cloud", "flame", "stone",
            "eagle", "frost", "bloom", "spark", "crane", "quest",
            "sword", "dusk",  "forge", "solar", "pixel", "amber"
        ]
        chosen = [secrets.choice(words).capitalize() for _ in range(num_words)]
        number = secrets.randbelow(9000) + 1000
        return "-".join(chosen) + "-" + str(number)


class PasswordChecker:
    """Checks password strength and gives improvement tips."""

    def check_strength(self, password):
        """
        Analyze password. Returns dict with score, label, and feedback.
        Max score is 6.
        """
        score    = 0
        feedback = []

        # rule 1: length
        if len(password) >= 16:
            score += 2
        elif len(password) >= 12:
            score += 1
        else:
            feedback.append("Use at least 12 characters")

        # rule 2: uppercase
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            feedback.append("Add uppercase letters (A-Z)")

        # rule 3: lowercase
        if re.search(r'[a-z]', password):
            score += 1
        else:
            feedback.append("Add lowercase letters (a-z)")

        # rule 4: digits
        if re.search(r'\d', password):
            score += 1
        else:
            feedback.append("Add numbers (0-9)")

        # rule 5: symbols
        if re.search(r'[!@#$%^&*()\-_=+\[\]{}|;:,.]', password):
            score += 1
        else:
            feedback.append("Add special characters (!@#$...)")
        # rule 6: no common patterns
        common = ["123456", "password", "qwerty", "abc123", "111111", "iloveyou"]
        for pattern in common:
            if pattern in password.lower():
                score -= 2
                feedback.append(f"Avoid common patterns like '{pattern}'")
                break
        score = max(0, min(score, 6))
        labels = {
            6: ("Very Strong", "+++"),
            5: ("Strong",      "++ "),
            4: ("Strong",      "++ "),
            3: ("Moderate",    "+  "),
            2: ("Weak",        "-  "),
            1: ("Very Weak",   "-- "),
            0: ("Very Weak",   "-- ")
        }
        label, symbol = labels[score]
        return {
            "score"    : score,
            "max_score": 6,
            "label"    : label,
            "symbol"   : symbol,
            "feedback" : feedback
        }
