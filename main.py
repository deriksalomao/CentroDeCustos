# main.py
# Ponto de entrada principal da aplicação.

import tkinter as tk
# --- IMPORTS CORRIGIDOS ---
from app.ui.ui_login import TelaLogin
from app.ui.app_principal import AppPrincipal

def main():
    """Inicializa a aplicação, mostrando a tela de login primeiro."""
    root = tk.Tk()
    root.withdraw() 
    
    def iniciar_app_principal():
        # Quando o login for bem-sucedido, destrói a janela de login
        # e cria a janela principal.
        for widget in root.winfo_children():
            widget.destroy()
        
        # A instância AppPrincipal irá gerir a janela 'root' a partir de agora
        AppPrincipal(root)
        root.deiconify() 

    # Passa a função de callback para a tela de login
    TelaLogin(root, on_login_success=iniciar_app_principal)
    
    root.mainloop()

if __name__ == "__main__":
    main()