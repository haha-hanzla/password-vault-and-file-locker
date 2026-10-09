      SECURE PASSWORD VAULT PRO  -  GUI Version

DESCRIPTION
-----------
A modern GUI-based secure password manager built using:
  - Tkinter     (Python's built-in GUI library)
  - CustomTkinter (modern dark-theme widgets)
  - All backend classes from terminal version (unchanged!)

HOW TO INSTALL & RUN
---------------------
  1. Make sure Python 3.8+ is installed
  2. Open terminal in this folder
  3. Install libraries:
       pip install customtkinter cryptography psutil
  4. Run:
       python main.py

PROJECT FILES
-------------
  main.py          -> Entry point (run this)
  gui_app.py       -> All GUI screens and widgets

  --- Backend (same as terminal version) ---
  master_lock.py       -> Login / PBKDF2 password hashing
  encryption.py        -> AES Fernet encryption
  password_entry.py    -> Data model for one password
  password_manager.py  -> Save/load/update/delete passwords
  password_tools.py    -> Generator + strength checker
  password_recovery.py -> Gmail OTP for forgot password
  file_locker.py       -> Encrypt/decrypt files
  app_locker.py        -> Lock apps behind password

GUI SCREENS
-----------
  Login Screen    -> Enter master password to unlock
  Setup Screen    -> First-time vault creation
  Dashboard       -> Sidebar navigation to all features
  Password Vault  -> View, add, edit, delete passwords
  File Locker     -> Lock/unlock files with encryption
  App Locker      -> Launch apps behind password
  Tools           -> Generate passwords, check strength
  Settings        -> Change password, email OTP config

OOP CONCEPTS DEMONSTRATED
--------------------------
  Encapsulation  -> Each class hides its internal logic
  Abstraction    -> GUI calls manager.add_password()
                    without knowing how encryption works
  Composition    -> PasswordVaultApp holds all backend objects
                    GUI frames receive 'app' object and use it
  Separation     -> Backend and frontend are completely separate
                    Swap terminal UI for GUI without touching logic
  Single Resp.   -> Each class/frame has one clear job

================================================================
