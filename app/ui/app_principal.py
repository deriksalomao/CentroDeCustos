# app/ui/app_principal.py
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
        
        self.paned_window = ttk.PanedWindow(master, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.paned_window, width=250)
        self.paned_window.add(self.left_frame, weight=1)

        self.right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_frame, weight=4)

        # Instancie o PainelEsquerdo
        self.painel_esquerdo = PainelEsquerdo(self.left_frame, controller=self.controller) 
        self.painel_esquerdo.pack(fill=tk.BOTH, expand=True) 
        
        # Instancie o PainelDireito
        self.painel_direito = PainelDireito(self.right_frame, controlador=self.controller)
        self.painel_direito.pack(fill=tk.BOTH, expand=True)

        # A criação do status bar continua aqui
        self.create_status_bar()

    def set_controller(self, controller):
        self.controller = controller
        # Passe o controller para os painéis modularizados
        self.painel_esquerdo.controller = controller
        self.painel_direito.controlador = controller 

        # Configuração dos comandos dos botões do PainelDireito
        self.painel_direito.btn_aplicar_filtros.config(command=self.controller.aplicar_filtros_e_resetar_pagina)
        self.painel_direito.btn_limpar_filtros.config(command=self.controller.limpar_filtros)
        self.painel_direito.btn_exportar_excel.config(command=self.controller.exportar_para_excel)
        self.painel_direito.btn_pagina_anterior.config(command=lambda: self.controller.change_page(-1))
        self.painel_direito.btn_proxima_pagina.config(command=lambda: self.controller.change_page(1))
        self.painel_direito.btn_excluir_lancamento.config(command=self.controller.excluir_lancamento_selecionado)
        self.painel_direito.btn_editar_lancamento.config(command=self.controller.editar_lancamento_selecionado) # Adicionado
        self.painel_direito.btn_novo_lancamento.config(command=self.painel_direito._abrir_janela_novo_lancamento)

        # Comandos do PainelEsquerdo
        self.painel_esquerdo.combo_empresa_ativa.bind("<<ComboboxSelected>>", self.controller.on_empresa_selecionada)
        self.painel_esquerdo.btn_add_cliente.config(command=lambda: self.controller.adicionar_item_rapido('Cliente', self.painel_esquerdo.get_add_cliente_value()))
        self.painel_esquerdo.btn_add_veiculo.config(command=lambda: self.controller.adicionar_item_rapido('Veículo', self.painel_esquerdo.get_add_veiculo_value()))
        self.painel_esquerdo.btn_add_cc.config(command=lambda: self.controller.adicionar_item_rapido('Centro de Custo', self.painel_esquerdo.get_add_cc_value()))
        self.painel_esquerdo.btn_add_categoria.config(command=lambda: self.controller.adicionar_item_rapido('Categoria', self.painel_esquerdo.get_add_categoria_value()))
        self.painel_esquerdo.btn_add_empresa.config(command=lambda: self.controller.adicionar_item_rapido('Empresa', self.painel_esquerdo.get_add_empresa_value()))

    # Os métodos create_painel_esquerdo e create_right_panel foram removidos daqui,
    # pois a lógica de criação agora está dentro das classes PainelEsquerdo e PainelDireito.
    # Outros métodos relacionados a esses painéis foram movidos para as respectivas classes.

    def create_status_bar(self):
        self.status_bar = ttk.Label(self.master, text="Pronto", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def set_status(self, message):
        self.status_bar.config(text=message)

    # Métodos que agora chamam os métodos nos painéis modularizados
    def get_filtros(self):
        return self.painel_direito.obter_filtros()

    def update_dropdown(self, dropdown_name, values):
        # Para dropdowns que são controlados por PainelDireito (filtros)
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

    # Este método agora está no PainelEsquerdo
    def update_financial_summary(self, receitas, despesas, saldo):
        self.painel_esquerdo.update_financial_summary(receitas, despesas, saldo)

    def get_selected_lancamento_id(self):
        return self.painel_direito.obter_id_lancamento_selecionado()

    def ask_yes_no(self, message):
        return messagebox.askyesno("Confirmação", message)
        
    # Este método agora chama o método interno do PainelDireito
    def abrir_janela_novo_lancamento(self):
        # A chamada ao método de criação da janela de lançamento
        # é feita diretamente pelo botão "Adicionar Novo Lançamento" no PainelDireito.
        # Se você ainda precisar chamá-la de um menu no AppPrincipal, faria:
        # self.painel_direito._abrir_janela_novo_lancamento()
        # Mas como a funcionalidade já está no PainelDireito, esta função pode ser vazia ou removida
        pass 

    def reset_filters(self):
        self.painel_direito.resetar_filtros()

    # O método 'criar_janela_lancamento' foi movido para dentro de 'PainelDireito' como '_criar_janela_lancamento'
    # Ele não está mais aqui em AppPrincipal