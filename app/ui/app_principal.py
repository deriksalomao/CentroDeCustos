import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import pandas as pd
from ttkbootstrap.widgets import DateEntry
from app.ui.paineis.painel_esquerdo import PainelEsquerdo
from app.ui.paineis.painel_direito import PainelDireito

class AppPrincipal:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.controller = None 
        self.master.title("Controle de Centro de Custos")
        self.master.state('zoomed')
        
        self.criar_menu_principal()
        
        self.paned_window = tk.PanedWindow(
            master, 
            orient=tk.HORIZONTAL, 
            sashrelief=tk.RAISED, 
            bg="white", 
            bd=0
        )
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.paned_window, width=250)
        self.paned_window.add(self.left_frame)

        self.right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_frame)

        self.painel_esquerdo = PainelEsquerdo(self.left_frame, controller=self.controller) 
        self.painel_esquerdo.pack(fill=tk.BOTH, expand=True) 
        
        self.painel_direito = PainelDireito(self.right_frame, controlador=self.controller)
        self.painel_direito.pack(fill=tk.BOTH, expand=True)

        self.create_status_bar()

    def criar_menu_principal(self):
        """Cria a barra de menu principal da aplicação."""
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        menu_sistema = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Sistema", menu=menu_sistema)
        menu_relatorios = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Relatórios", menu=menu_relatorios)
        menu_relatorios.add_command(
            label="Custo por Veículo",
            command=lambda: self.controller.abrir_janela_relatorio_veiculo() if self.controller else None
        )

    def set_controller(self, controller):
        self.controller = controller
        self.painel_esquerdo.controller = controller
        self.painel_direito.controlador = controller 

        self.painel_direito.btn_aplicar_filtros.config(command=self.controller.aplicar_filtros_e_resetar_pagina)
        self.painel_direito.btn_limpar_filtros.config(command=self.controller.limpar_filtros)
        self.painel_direito.btn_exportar_excel.config(command=self.controller.exportar_para_excel)
        self.painel_direito.btn_pagina_anterior.config(command=lambda: self.controller.change_page(-1))
        self.painel_direito.btn_proxima_pagina.config(command=lambda: self.controller.change_page(1))
        self.painel_direito.btn_excluir_lancamento.config(command=self.controller.excluir_lancamento_selecionado)
        self.painel_direito.btn_editar_lancamento.config(command=self.controller.editar_lancamento_selecionado)
        self.painel_direito.btn_novo_lancamento.config(command=self.painel_direito._abrir_janela_novo_lancamento)

        self.painel_esquerdo.combo_empresa_ativa.bind("<<ComboboxSelected>>", self.controller.on_empresa_selecionada)

    def create_status_bar(self):
        self.status_bar = ttk.Label(self.master, text="Pronto", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def set_status(self, message):
        self.status_bar.config(text=message)

    def get_filtros(self):
        return self.painel_direito.obter_filtros()

    def update_dropdown(self, dropdown_name, values):
        self.painel_direito.atualizar_dropdown(dropdown_name, values)
    
    def set_empresa_ativa(self, nome_empresa):
        self.painel_esquerdo.set_empresa_ativa(nome_empresa)

    def get_empresa_ativa(self):
        return self.painel_esquerdo.get_empresa_ativa()

    def update_empresa_dropdown(self, empresas, set_default=False):
        self.painel_esquerdo.update_empresa_dropdown(empresas, set_default)

    def update_page_info(self, current, total):
        self.painel_direito.atualizar_info_pagina(current, total)

    def update_lancamentos_treeview(self, dataframe):
        self.painel_direito.atualizar_arvore_lancamentos(dataframe)

    def update_financial_summary(self, receitas, despesas, saldo):
        self.painel_esquerdo.update_financial_summary(receitas, despesas, saldo)

    def get_selected_lancamento_id(self):
        return self.painel_direito.obter_id_lancamento_selecionado()

    def ask_yes_no(self, message):
        return messagebox.askyesno("Confirmação", message)
        
    def abrir_janela_novo_lancamento(self):
        pass 

    def reset_filters(self):
        self.painel_direito.resetar_filtros()

    def update_cadastro_dropdown(self, tipo_item, valores):
        """Repassa a chamada para o painel esquerdo, onde a função realmente existe."""
        self.painel_esquerdo.update_cadastro_dropdown(tipo_item, valores)