# main.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.ui.ui_login import TelaLogin
from app.ui.app_principal import AppPrincipal

def main():
    # --- ALTERAÇÃO AQUI ---
    # Trocando o tema para um com mais espaçamento.
    root = ttk.Window(themename="cosmo") 
    # ----------------------
    
    root.withdraw()

    def iniciar_app_principal():
        login_toplevel.destroy()
        AppPrincipal(root)
        root.deiconify()

    login_toplevel = ttk.Toplevel(title="Login")
    login_toplevel.geometry("300x150")
    login_toplevel.resizable(False, False)
    login_toplevel.place_window_center()

    def on_success():
        iniciar_app_principal()

    TelaLogin(login_toplevel, on_login_success=on_success)
    login_toplevel.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()

if __name__ == "__main__":
    main()

    