import tkinter as tk
import ttkbootstrap as ttk
from app.ui.app_principal import AppPrincipal
from app.core.data_manager import DataManager
from app.core.controller import AppController
from app.ui.ui_login import LoginWindow


def iniciar_app_principal():
# Garante quue a janela de login seja fechada
    for widget in root.winfo_children():
        widget.destroy()

# Configura o estilo da janela principal
    style = ttk.Style()
    style.configure('TLabel', font=('Segoe UI', 11, 'bold'))
    style.configure('TButton', font=('Segoe UI', 11, 'bold'))
    style.configure('TEntry', font=('Segoe UI', 11))
    style.configure('TCombobox', font=('Segoe UI', 11))
    style.configure('Treeview.Heading', font=('Segoe UI', 11, 'bold'))
    style.configure('Treeview', font=('Segoe UI', 10), rowheight=25)

# Instâncias as classes necessárias
    model = DataManager()
    view = AppPrincipal(root)
    controller = AppController(model, view)

if __name__ == "__main__":
    root = ttk.Window(themename="litera")
# Inicia a janela de login primeiro, passando a função de sucesso
# que será chamada quando o login for bem-sucedido
    login_view = LoginWindow(master=root, on_success=iniciar_app_principal)
    root.mainloop() 