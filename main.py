# Conteúdo CORRETO para: main.py
import tkinter as tk
from app.ui.ui_login import TelaLogin
from app.ui.app_principal import AppPrincipal

def main():
    root = tk.Tk()
    root.withdraw()

    def iniciar_app_principal():
        AppPrincipal(root)
        root.deiconify()

    login_toplevel = tk.Toplevel(root)
    login_toplevel.title("Login")
    login_toplevel.geometry("300x150")
    login_toplevel.resizable(False, False)

    login_toplevel.update_idletasks()
    width = login_toplevel.winfo_width()
    height = login_toplevel.winfo_height()
    x = (login_toplevel.winfo_screenwidth() // 2) - (width // 2)
    y = (login_toplevel.winfo_screenheight() // 2) - (height // 2)
    login_toplevel.geometry(f'{width}x{height}+{x}+{y}')

    def on_success():
        login_toplevel.destroy()
        iniciar_app_principal()

    TelaLogin(login_toplevel, on_login_success=on_success)
    login_toplevel.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()

if __name__ == "__main__":
    main()