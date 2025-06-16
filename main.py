# main.py
# Ponto de entrada principal da aplicação.

import tkinter as tk
from ui_login import TelaLogin
from app_principal import AppPrincipal

def main():
    """Inicializa a aplicação, mostrando a tela de login primeiro."""
    root = tk.Tk()
    
    # Esconde a janela principal temporariamente para a tela de login aparecer primeiro
    root.withdraw() 
    
    # Função que será chamada quando o login for bem-sucedido
    def iniciar_app_principal():
        # A tela de login já limpou a janela. Agora criamos a principal.
        AppPrincipal(root)
        # Traz a janela de volta à vida, agora com o app principal
        root.deiconify() 

    # Inicia o fluxo com a tela de login
    TelaLogin(root, on_login_success=iniciar_app_principal)
    
    root.mainloop()

if __name__ == "__main__":
    main()
