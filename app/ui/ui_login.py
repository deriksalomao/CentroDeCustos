import ttkbootstrap as ttk
from tkinter import messagebox

class LoginWindow(ttk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master, padding=20)
        self.master = master
        self.pack(fill=ttk.BOTH, expand=True)
        self.on_login_success = on_success
        
        self.master.title("Login")
        
        # Centralizar a janela
        self.master.place_window_center()

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True)

        # Usuário
        user_frame = ttk.Frame(main_frame)
        user_frame.pack(pady=5)
        ttk.Label(user_frame, text="Usuário:", width=10).pack(side=ttk.LEFT)
        self.user_entry = ttk.Entry(user_frame, width=30)
        self.user_entry.pack(side=ttk.LEFT)
        self.user_entry.insert(0, "admin")

        # Senha
        pass_frame = ttk.Frame(main_frame)
        pass_frame.pack(pady=5)
        ttk.Label(pass_frame, text="Senha:", width=10).pack(side=ttk.LEFT)
        self.pass_entry = ttk.Entry(pass_frame, show="*", width=30)
        self.pass_entry.pack(side=ttk.LEFT)
        self.pass_entry.insert(0, "admin")
        self.pass_entry.bind("<Return>", self._login)

        # Botão
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        login_button = ttk.Button(button_frame, text="Login", command=self._login, bootstyle="success")
        login_button.pack()

    def _login(self, event=None):
        # Lógica de login simples para o exemplo
        if self.user_entry.get() == "admin" and self.pass_entry.get() == "admin":
            if self.on_login_success:
                self.on_login_success()
        else:
            messagebox.showerror("Erro de Login", "Usuário ou senha inválidos.")