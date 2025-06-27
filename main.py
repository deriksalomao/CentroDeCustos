# main.py
import tkinter as tk
import ttkbootstrap as ttk
from app.ui.app_principal import AppPrincipal
from app.core.data_manager import DataManager
from app.core.controller import AppController

def iniciar_app_principal():
    # Usar a janela do ttkbootstrap
    root = ttk.Window(themename="litera")

    style = ttk.Style()
    # Define uma fonte maior para os Labels, Buttons, Entries e Comboboxes
    style.configure('TLabel', font=('Segoe UI', 11, 'bold'))
    style.configure('TButton', font=('Segoe UI', 11, 'bold'))
    style.configure('TEntry', font=('Segoe UI', 11))
    style.configure('TCombobox', font=('Segoe UI', 11))
    # Para as colunas da Treeview
    style.configure('Treeview.Heading', font=('Segoe UI', 11, 'bold'))
    style.configure('Treeview', font=('Segoe UI', 10), rowheight=25)

    # Criar as instâncias
    model = DataManager()
    view = AppPrincipal(root)
    # O controller agora é criado aqui, e ele mesmo se conecta à view
    controller = AppController(model, view)
    
    root.mainloop()

if __name__ == "__main__":
    iniciar_app_principal()