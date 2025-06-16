# ui_login.py
# Contém a classe e a interface da tela de login.

import tkinter as tk
from tkinter import ttk

class TelaLogin:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.root.title("Login - Sistema de Gestão Financeira")
        self.root.geometry("400x300")
        
        self.root.deiconify()
        self.root.eval('tk::PlaceWindow . center')

        self.frame = ttk.Frame(self.root, padding="30 30 30 30")
        self.frame.pack(fill='both', expand=True)

        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 11, "bold"))
        style.configure("TEntry", font=("Segoe UI", 11))
        
        ttk.Label(self.frame, text="Login do Sistema", font=("Segoe UI", 16, "bold")).pack(pady=(0, 20))

        ttk.Label(self.frame, text="Usuário:").pack(anchor='w')
        self.user_entry = ttk.Entry(self.frame, width=30)
        self.user_entry.pack(pady=5)
        self.user_entry.focus()

        ttk.Label(self.frame, text="Senha:").pack(anchor='w')
        self.pass_entry = ttk.Entry(self.frame, show="*", width=30)
        self.pass_entry.pack(pady=5)
        self.pass_entry.bind("<Return>", self.verificar_login)

        self.status_label = ttk.Label(self.frame, text="", foreground="red")
        self.status_label.pack(pady=(10, 0))

        btn_login = ttk.Button(self.frame, text="Entrar", command=self.verificar_login)
        btn_login.pack(pady=20, ipady=5, fill='x')

    def verificar_login(self, event=None):
        usuario = self.user_entry.get()
        senha = self.pass_entry.get()

        if usuario == "admin" and senha == "admin":
            for widget in self.frame.winfo_children():
                widget.destroy()
            self.frame.destroy()
            self.on_login_success()
        else:
            self.status_label.config(text="Usuário ou senha inválidos.")
