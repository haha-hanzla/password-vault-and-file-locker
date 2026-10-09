# main.py
# Entry point for Password Vault GUI
# Run this file to open the application window
#
# Project  : Secure Password Vault Pro - GUI Version
# Subject  : Object Oriented Programming - 2nd Semester
# GUI Lib  : Tkinter (built into Python, no install needed)
#            + customtkinter for modern look
#
# Install  : pip install customtkinter cryptography psutil
# Run      : python main.py

from gui_app import PasswordVaultApp

if __name__ == "__main__":
    app = PasswordVaultApp()
    app.run()
