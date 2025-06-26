# main.py
import ttkbootstrap as ttk
from app.ui.app_principal import AppPrincipal
from app.ui.ui_login import LoginWindow

def iniciar_app_principal(login_window=None):
    """Fecha a janela de login (se existir) e inicia a aplicação principal."""
    if login_window:
        login_window.destroy()
    root = ttk.Window(themename="litera")
    AppPrincipal(root)
    root.mainloop()

def on_login_success(login_window):
    """Callback chamado quando o login é bem-sucedido."""
    iniciar_app_principal(login_window)

if __name__ == "__main__":
    # Para desenvolvimento, pode querer saltar o login.
    # Se quiser ativar o login, comente a linha abaixo e descomente as duas seguintes.
    iniciar_app_principal()

    # login_root = ttk.Window(themename="litera")
    # LoginWindow(login_root, on_success=lambda: on_login_success(login_root))
    # login_root.mainloop()