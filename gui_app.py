# gui_app.py
# Simple GUI for Password Vault - plain Tkinter only
# No customtkinter, no colors, no styling - just basic windows and buttons
#
# Screens:
#   LoginWindow    -> master password login
#   SetupWindow    -> first time setup
#   DashboardWindow-> main menu (buttons to open other windows)
#   VaultWindow    -> view / add / edit / delete passwords
#   ToolsWindow    -> generate password / check strength
#
# Project  : Secure Password Vault - Simple GUI Version
# Subject  : Object Oriented Programming - 2nd Semester

import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

from master_lock import MasterLock
from encryption import Encryption
from password_manager import PasswordManager
from password_tools import PasswordGenerator, PasswordChecker
from file_locker import FileLocker


# ══════════════════════════════════════════════════════════════
#   MAIN APP CONTROLLER
# ══════════════════════════════════════════════════════════════

class PasswordVaultApp:
    """Main app controller. Creates the root window and switches screens."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Password Vault")
        self.root.geometry("400x300")

        # backend objects
        self.lock = MasterLock()
        self.generator = PasswordGenerator()
        self.checker = PasswordChecker()

        # set after login
        self.manager = None
        self.locker = None

        if self.lock.is_setup():
            self.show_login()
        else:
            self.show_setup()

    def run(self):
        self.root.mainloop()

    def _clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_setup(self):
        self._clear()
        self.root.geometry("400x300")
        SetupWindow(self.root, self)

    def show_login(self):
        self._clear()
        self.root.geometry("400x250")
        LoginWindow(self.root, self)

    def show_dashboard(self):
        self._clear()
        self.root.geometry("400x300")
        DashboardWindow(self.root, self)

    def login_success(self, master_password):
        enc = Encryption(master_password)
        self.manager = PasswordManager(enc)
        self.locker = FileLocker(enc)
        self.manager.log_login(True)
        self.show_dashboard()


# ══════════════════════════════════════════════════════════════
#   SETUP WINDOW (first time)
# ══════════════════════════════════════════════════════════════

class SetupWindow:
    """First-time setup screen - create master password."""

    def __init__(self, root, app):
        self.root = root
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self.root, text="Create Your Vault", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Master Password:").pack()
        self.pw_entry = tk.Entry(self.root, show="*")
        self.pw_entry.pack()

        tk.Label(self.root, text="Confirm Password:").pack()
        self.confirm_entry = tk.Entry(self.root, show="*")
        self.confirm_entry.pack()

        tk.Label(self.root, text="Recovery Email (optional):").pack()
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()

        tk.Button(self.root, text="Create Vault", command=self._create).pack(pady=10)

        self.msg_label = tk.Label(self.root, text="", fg="red")
        self.msg_label.pack()

    def _create(self):
        pw = self.pw_entry.get().strip()
        confirm = self.confirm_entry.get().strip()
        email = self.email_entry.get().strip()

        if len(pw) < 6:
            self.msg_label.config(text="Password must be at least 6 characters.")
            return
        if pw != confirm:
            self.msg_label.config(text="Passwords do not match.")
            return
        if not email:
            email = "not_set"

        self.app.lock.setup_master(pw, email)
        messagebox.showinfo("Vault Created", "Your vault has been created!\nPlease login to continue.")
        self.app.show_login()


# ══════════════════════════════════════════════════════════════
#   LOGIN WINDOW
# ══════════════════════════════════════════════════════════════

class LoginWindow:
    """Login screen with master password."""

    MAX_ATTEMPTS = 3

    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.attempts = 0
        self._build()

    def _build(self):
        tk.Label(self.root, text="Password Vault", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Enter Master Password:").pack()

        self.pw_entry = tk.Entry(self.root, show="*")
        self.pw_entry.pack()
        self.pw_entry.bind("<Return>", lambda e: self._login())

        tk.Button(self.root, text="Unlock Vault", command=self._login).pack(pady=10)

        self.msg_label = tk.Label(self.root, text="", fg="red")
        self.msg_label.pack()

    def _login(self):
        pw = self.pw_entry.get().strip()
        if not pw:
            self.msg_label.config(text="Please enter your password.")
            return

        if self.app.lock.verify_master(pw):
            self.app.login_success(pw)
        else:
            self.attempts += 1
            remaining = self.MAX_ATTEMPTS - self.attempts
            if remaining <= 0:
                messagebox.showerror("Vault Locked", "Too many wrong attempts!\nRestart the program.")
                self.root.quit()
            else:
                self.msg_label.config(text=f"Wrong password. {remaining} attempt(s) left.")
                self.pw_entry.delete(0, "end")


# ══════════════════════════════════════════════════════════════
#   DASHBOARD WINDOW (main menu after login)
# ══════════════════════════════════════════════════════════════

class DashboardWindow:
    """Main menu - buttons to open Vault and Tools windows."""

    def __init__(self, root, app):
        self.root = root
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self.root, text="Dashboard", font=("Arial", 14)).pack(pady=10)

        tk.Button(self.root, text="Password Vault", width=25,
                   command=self._open_vault).pack(pady=5)
        tk.Button(self.root, text="Password Tools", width=25,
                   command=self._open_tools).pack(pady=5)
        tk.Button(self.root, text="File Locker", width=25,
                   command=self._open_locker).pack(pady=5)
        tk.Button(self.root, text="Logout", width=25,
                   command=self._logout).pack(pady=20)

    def _open_vault(self):
        win = tk.Toplevel(self.root)
        win.title("Password Vault")
        win.geometry("500x400")
        VaultWindow(win, self.app)

    def _open_tools(self):
        win = tk.Toplevel(self.root)
        win.title("Password Tools")
        win.geometry("400x400")
        ToolsWindow(win, self.app)

    def _open_locker(self):
        win = tk.Toplevel(self.root)
        win.title("File Locker")
        win.geometry("500x400")
        FileLockerWindow(win, self.app)

    def _logout(self):
        if messagebox.askyesno("Logout", "Lock the vault and logout?"):
            self.app.manager = None
            self.app.locker = None
            self.app.show_login()


# ══════════════════════════════════════════════════════════════
#   VAULT WINDOW (password manager)
# ══════════════════════════════════════════════════════════════

class VaultWindow:
    """Password manager window - add, view, edit, delete passwords."""

    def __init__(self, win, app):
        self.win = win
        self.app = app
        self._build()
        self._refresh_list()

    def _build(self):
        top_frame = tk.Frame(self.win)
        top_frame.pack(pady=10)

        tk.Button(top_frame, text="Add New", command=self._open_add_dialog).pack(side="left", padx=5)
        tk.Button(top_frame, text="View", command=self._view_selected).pack(side="left", padx=5)
        tk.Button(top_frame, text="Edit", command=self._edit_selected).pack(side="left", padx=5)
        tk.Button(top_frame, text="Delete", command=self._delete_selected).pack(side="left", padx=5)
        tk.Button(top_frame, text="Refresh", command=self._refresh_list).pack(side="left", padx=5)

        search_frame = tk.Frame(self.win)
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Search:").pack(side="left")
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side="left", padx=5)
        tk.Button(search_frame, text="Go", command=self._refresh_list).pack(side="left")

        list_frame = tk.Frame(self.win)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        self.count_label = tk.Label(self.win, text="")
        self.count_label.pack()

    def _refresh_list(self):
        self.listbox.delete(0, "end")
        keyword = self.search_entry.get().strip().lower()
        entries = self.app.manager.search(keyword) if keyword else self.app.manager.list_all()

        self.count_label.config(text=f"{len(entries)} entry(s)")

        for entry in entries:
            self.listbox.insert("end", f"{entry.site}   |   {entry.username}")

    def _get_selected_site(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an entry from the list.")
            return None
        text = self.listbox.get(selection[0])
        site = text.split("   |   ")[0]
        return site

    def _view_selected(self):
        site = self._get_selected_site()
        if not site:
            return
        result = self.app.manager.get_password(site)
        if result:
            msg = (f"Site: {result['site']}\n"
                   f"Username: {result['username']}\n"
                   f"Password: {result['password']}\n"
                   f"Added On: {result.get('added_on', 'Unknown')}")
            messagebox.showinfo("Password Details", msg)

    def _delete_selected(self):
        site = self._get_selected_site()
        if not site:
            return
        if messagebox.askyesno("Delete", f"Delete password for '{site}'?"):
            self.app.manager.delete_password(site)
            self._refresh_list()

    def _open_add_dialog(self):
        AddPasswordDialog(self.win, self.app, self._refresh_list)

    def _edit_selected(self):
        site = self._get_selected_site()
        if not site:
            return
        EditPasswordDialog(self.win, self.app, site, self._refresh_list)


class AddPasswordDialog:
    def __init__(self, parent, app, refresh_callback):
        self.app = app
        self.callback = refresh_callback
        self.win = tk.Toplevel(parent)
        self.win.title("Add Password")
        self.win.geometry("300x250")
        self._build()

    def _build(self):
        tk.Label(self.win, text="Site / App:").pack(pady=(10, 0))
        self.site_e = tk.Entry(self.win)
        self.site_e.pack()

        tk.Label(self.win, text="Username:").pack(pady=(10, 0))
        self.user_e = tk.Entry(self.win)
        self.user_e.pack()

        tk.Label(self.win, text="Password (blank = auto generate):").pack(pady=(10, 0))
        self.pass_e = tk.Entry(self.win, show="*")
        self.pass_e.pack()

        tk.Button(self.win, text="Generate", command=self._generate).pack(pady=5)
        tk.Button(self.win, text="Save", command=self._save).pack(pady=5)

        self.msg = tk.Label(self.win, text="", fg="red")
        self.msg.pack()

    def _generate(self):
        pw = self.app.generator.generate()
        self.pass_e.delete(0, "end")
        self.pass_e.config(show="")
        self.pass_e.insert(0, pw)

    def _save(self):
        site = self.site_e.get().strip()
        user = self.user_e.get().strip()
        pw = self.pass_e.get().strip()

        if not site or not user:
            self.msg.config(text="Site and username are required.")
            return
        if not pw:
            pw = self.app.generator.generate()

        self.app.manager.add_password(site, user, pw)
        self.callback()
        self.win.destroy()
        messagebox.showinfo("Saved", f"Password for '{site}' saved!")


class EditPasswordDialog:
    def __init__(self, parent, app, site, refresh_callback):
        self.app = app
        self.site = site
        self.callback = refresh_callback
        self.win = tk.Toplevel(parent)
        self.win.title("Edit Password")
        self.win.geometry("300x250")
        self._build()

    def _build(self):
        current = self.app.manager.get_password(self.site)

        tk.Label(self.win, text=f"Editing: {self.site}").pack(pady=(10, 0))

        tk.Label(self.win, text="New Username (blank = keep current):").pack(pady=(10, 0))
        self.user_e = tk.Entry(self.win)
        self.user_e.insert(0, current["username"])
        self.user_e.pack()

        tk.Label(self.win, text="New Password (blank = keep current):").pack(pady=(10, 0))
        self.pass_e = tk.Entry(self.win, show="*")
        self.pass_e.pack()

        tk.Button(self.win, text="Generate", command=self._generate).pack(pady=5)
        tk.Button(self.win, text="Update", command=self._update).pack(pady=5)

        self.msg = tk.Label(self.win, text="", fg="red")
        self.msg.pack()

    def _generate(self):
        pw = self.app.generator.generate()
        self.pass_e.delete(0, "end")
        self.pass_e.config(show="")
        self.pass_e.insert(0, pw)

    def _update(self):
        new_user = self.user_e.get().strip()
        new_pass = self.pass_e.get().strip()
        if new_user:
            self.app.manager.update_username(self.site, new_user)
        if new_pass:
            self.app.manager.update_password(self.site, new_pass)
        self.callback()
        self.win.destroy()
        messagebox.showinfo("Updated", f"'{self.site}' updated!")


# ══════════════════════════════════════════════════════════════
#   TOOLS WINDOW
# ══════════════════════════════════════════════════════════════

class ToolsWindow:
    """Password generator and strength checker."""

    def __init__(self, win, app):
        self.win = win
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self.win, text="Generate Password", font=("Arial", 12)).pack(pady=(15, 5))

        gen_frame = tk.Frame(self.win)
        gen_frame.pack(pady=5)

        tk.Label(gen_frame, text="Length:").pack(side="left")
        self.length_entry = tk.Entry(gen_frame, width=5)
        self.length_entry.insert(0, "16")
        self.length_entry.pack(side="left", padx=5)

        self.sym_var = tk.BooleanVar(value=True)
        self.dig_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.win, text="Include Symbols", variable=self.sym_var).pack()
        tk.Checkbutton(self.win, text="Include Numbers", variable=self.dig_var).pack()

        tk.Button(self.win, text="Generate", command=self._generate).pack(pady=5)
        tk.Button(self.win, text="Generate Memorable Passphrase",
                   command=self._generate_memorable).pack(pady=5)

        self.gen_result = tk.Entry(self.win, width=35)
        self.gen_result.pack(pady=5)

        tk.Button(self.win, text="Copy", command=self._copy_generated).pack(pady=5)

        tk.Label(self.win, text="").pack()  # spacer
        tk.Label(self.win, text="Check Password Strength", font=("Arial", 12)).pack(pady=(10, 5))

        self.chk_entry = tk.Entry(self.win, show="*", width=30)
        self.chk_entry.pack(pady=5)

        tk.Button(self.win, text="Check Strength", command=self._check).pack(pady=5)

        self.score_label = tk.Label(self.win, text="Score: - / 6")
        self.score_label.pack()

        self.tips_label = tk.Label(self.win, text="", justify="left")
        self.tips_label.pack(pady=5)

    def _generate(self):
        try:
            length = int(self.length_entry.get())
        except ValueError:
            length = 16
        pw = self.app.generator.generate(length, self.sym_var.get(), self.dig_var.get())
        self.gen_result.delete(0, "end")
        self.gen_result.insert(0, pw)

    def _generate_memorable(self):
        pw = self.app.generator.generate_memorable()
        self.gen_result.delete(0, "end")
        self.gen_result.insert(0, pw)

    def _copy_generated(self):
        pw = self.gen_result.get()
        if pw:
            self.win.clipboard_clear()
            self.win.clipboard_append(pw)

    def _check(self):
        pw = self.chk_entry.get()
        if not pw:
            return
        result = self.app.checker.check_strength(pw)
        self.score_label.config(text=f"Score: {result['score']} / {result['max_score']}  ({result['label']})")

        if result["feedback"]:
            tips_text = "\n".join(f"- {tip}" for tip in result["feedback"])
        else:
            tips_text = "Great password!"
        self.tips_label.config(text=tips_text)


# ══════════════════════════════════════════════════════════════
#   FILE LOCKER WINDOW
# ══════════════════════════════════════════════════════════════

class FileLockerWindow:
    """Lock and unlock files - simple list with lock/unlock buttons."""

    def __init__(self, win, app):
        self.win = win
        self.app = app
        self._build()
        self._refresh_list()

    def _build(self):
        tk.Label(self.win, text="File Locker", font=("Arial", 14)).pack(pady=10)

        top_frame = tk.Frame(self.win)
        top_frame.pack(pady=5)

        tk.Button(top_frame, text="Lock a File", command=self._lock_file).pack(side="left", padx=5)
        tk.Button(top_frame, text="Unlock Selected", command=self._unlock_selected).pack(side="left", padx=5)
        tk.Button(top_frame, text="Refresh", command=self._refresh_list).pack(side="left", padx=5)

        list_frame = tk.Frame(self.win)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        self.count_label = tk.Label(self.win, text="")
        self.count_label.pack()

    def _refresh_list(self):
        self.listbox.delete(0, "end")
        locked = self.app.locker.list_locked_files()

        self.count_label.config(text=f"{len(locked)} file(s) locked")

        for item in locked:
            self.listbox.insert("end", f"{item['original_name']}   |   {item['size_kb']} KB")

    def _lock_file(self):
        file_path = filedialog.askopenfilename(title="Choose a file to lock")
        if not file_path:
            return
        ok = self.app.locker.lock_file(file_path)
        if ok:
            messagebox.showinfo("Locked", "File locked successfully!")
        else:
            messagebox.showerror("Error", "Could not lock this file.")
        self._refresh_list()

    def _unlock_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file from the list.")
            return

        locked_items = self.app.locker.list_locked_files()
        chosen = locked_items[selection[0]]
        locked_path = chosen["locked_path"]

        ok = self.app.locker.unlock_file(locked_path)
        if ok:
            messagebox.showinfo("Unlocked", "File unlocked and restored!")
        else:
            messagebox.showerror("Error", "Could not unlock this file.")
        self._refresh_list()