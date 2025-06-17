# uploaded:CentroDeCustos/app/ui/ui_login.py
import tkinter as tk
from tkinter import messagebox, Toplevel
from app.ui.app_principal import AppPrincipal
import hashlib  

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Centro de Custos")
        self.root.geometry("300x150")
        self.root.resizable(False, False)

        # Centralizar a janela
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

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
        self.entry_pwd.bind("<Return>", self._login) # Adiciona bind para a tecla Enter

        self.login_button = tk.Button(self.frame, text="Login", command=self._login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Foco no campo de usuário ao iniciar
        self.entry_user.focus_set()
        
    def _hash_password(self, password):
        """Gera um hash SHA-256 para a senha fornecida.""" # <--- NOVO: Função para criar o hash
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def _login(self, event=None): # Adicionado event=None para o bind
        user = self.entry_user.get()
        pwd = self.entry_pwd.get()

        # Hash da senha "admin". Nunca armazene a senha em texto plano.
        # Você pode gerar este hash executando: print(self._hash_password('admin'))
        correct_hashed_pwd = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
        
        # Compara o hash da senha digitada com o hash correto
        hashed_input_pwd = self._hash_password(pwd)

        if user == "admin" and hashed_input_pwd == correct_hashed_pwd:
            self.root.destroy()
            root = tk.Tk()
            app = AppPrincipal(root)
            root.mainloop()
        else:
            messagebox.showerror("Erro de Login", "Usuário ou senha inválidos.")
            self.entry_pwd.delete(0, 'end') # Limpa o campo de senha