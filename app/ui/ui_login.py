import tkinter as tk
from tkinter import messagebox
import hashlib

class TelaLogin:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success

        self.frame = tk.Frame(self.root, padx=10, pady=10)
        self.frame.pack(expand=True)

        self.label_user = tk.Label(self.frame, text="Usuário:")
        self.label_user.grid(row=0, column=0, sticky="w", pady=5)
        self.entry_user = tk.Entry(self.frame)
        self.entry_user.grid(row=0, column=1, sticky="ew")

        self.label_pwd = tk.Label(self.frame, text="Senha:")
        self.label_pwd.grid(row=1, column=0, sticky="w", pady=5)
        self.entry_pwd = tk.Entry(self.frame, show="*")
        self.entry_pwd.grid(row=1, column=1, sticky="ew")
        self.entry_pwd.bind("<Return>", self._login)

        self.login_button = tk.Button(self.frame, text="Login", command=self._login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.entry_user.focus_set()

    def _hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def _login(self, event=None):
        user = self.entry_user.get()
        pwd = self.entry_pwd.get()
        
        correct_hashed_pwd = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
        hashed_input_pwd = self._hash_password(pwd)

        if user == "admin" and hashed_input_pwd == correct_hashed_pwd:
            self.on_login_success()
        else:
            messagebox.showerror("Erro de Login", "Usuário ou senha inválidos.")
            self.entry_pwd.delete(0, 'end')