# app/core/controller.py
from tkinter import messagebox
import pandas as pd
from datetime import datetime

class AppController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def iniciar_app(self):
        config = self.model.load_config()
        self.view.atualizar_empresas_combobox(list(self.model.dados_empresas.keys()))
        last_company = config.get('last_company', 'Empresa Padrão')
        if last_company in self.model.dados_empresas:
            self.view.set_empresa_ativa(last_company)
        self.on_empresa_selecionada()

    def on_empresa_selecionada(self, event=None):
        empresa_ativa = self.view.get_empresa_ativa()
        if not empresa_ativa: return
        
        # Lógica para popular os filtros da View
        centros_custo = ["Todos"] + self.model.dados_empresas.get(empresa_ativa, [])
        categorias_filtro = ["Todos"] + self.model.categorias
        self.view.atualizar_filtros_combobox(centros_custo, categorias_filtro)
        
        self.atualizar_relatorio_e_resumo()

    def atualizar_relatorio_e_resumo(self):
        empresa_ativa = self.view.get_empresa_ativa()
        filtros = self.view.get_filtros()
        df_filtrado = self.model.get_filtered_data(empresa_ativa, filtros)
        
        self.view.atualizar_treeview_lancamentos(df_filtrado)
        self.view.atualizar_resumo_financeiro(df_filtrado)

    # --- NOVA FUNÇÃO ADICIONADA ---
    def limpar_filtros(self):
        """Orquestra a limpeza e atualização da tela."""
        self.view.resetar_campos_de_filtro()
        self.atualizar_relatorio_e_resumo()

    def adicionar_empresa(self):
        nova_empresa = self.view.get_nova_empresa().strip().title()
        if not nova_empresa: return
        if nova_empresa in self.model.dados_empresas:
            self.view.mostrar_info("Empresa já existe.")
            return
        
        self.model.dados_empresas[nova_empresa] = ["Geral"]
        self.view.atualizar_empresas_combobox(list(self.model.dados_empresas.keys()))
        self.view.set_empresa_ativa(nova_empresa)
        self.on_empresa_selecionada()
        self.view.set_status(f"Empresa '{nova_empresa}' adicionada.")

    def adicionar_categoria(self):
        nova_cat = self.view.get_nova_categoria().strip().title()
        if not nova_cat: return
        if nova_cat in self.model.categorias:
            self.view.mostrar_info("Categoria já existe."); return
        
        self.model.categorias.append(nova_cat)
        self.on_empresa_selecionada()
        self.view.set_status(f"Categoria '{nova_cat}' adicionada.")
        
    def adicionar_centro_custo(self):
        empresa = self.view.get_empresa_ativa()
        novo_cc = self.view.get_novo_cc().strip().title()
        if not novo_cc: return
        if novo_cc in self.model.dados_empresas[empresa]:
            self.view.mostrar_info("Centro de Custo já existe."); return
        
        self.model.dados_empresas[empresa].append(novo_cc)
        self.on_empresa_selecionada()
        self.view.set_status(f"Centro de Custo '{novo_cc}' adicionado.")

    def abrir_janela_novo_lancamento(self):
        empresa = self.view.get_empresa_ativa()
        centros_custo = self.model.dados_empresas.get(empresa, [])
        categorias = self.model.categorias
        self.view.criar_janela_lancamento(
            titulo="Adicionar Novo Lançamento",
            centros_custo=centros_custo,
            categorias=categorias,
            callback_salvar=self.salvar_novo_lancamento
        )

    def salvar_novo_lancamento(self, dados_lancamento):
        
        dados_lancamento['Empresa'] = self.view.get_empresa_ativa()
        
        success, message = self.model.adicionar_lancamento(dados_lancamento)
        if success:
            self.atualizar_relatorio_e_resumo()
            self.view.set_status(message)

    def abrir_janela_edicao(self, event):
        index = self.view.get_selected_lancamento_index()
        if index is None: return

        dados_atuais = self.model.get_lancamento_por_indice(index)
        empresa = dados_atuais['Empresa']
        centros_custo = self.model.dados_empresas.get(empresa, [])
        categorias = self.model.categorias

        self.view.criar_janela_lancamento(
            titulo="Editar Lançamento",
            centros_custo=centros_custo,
            categorias=categorias,
            dados_edicao=dados_atuais,
            callback_salvar=lambda dados: self.salvar_edicao_lancamento(index, dados)
        )

    def salvar_edicao_lancamento(self, index, dados_atualizados):
        success, message = self.model.editar_lancamento(index, dados_atualizados)
        if success:
            self.atualizar_relatorio_e_resumo()
            self.view.set_status(message)

    def excluir_lancamento_selecionado(self):
        index = self.view.get_selected_lancamento_index()
        if index is None: 
            self.view.mostrar_info("Nenhum lançamento selecionado."); return
        
        if self.view.confirmar_acao("Confirmar Exclusão", "Deseja excluir o lançamento selecionado?"):
            success, message = self.model.excluir_lancamento(index)
            if success:
                self.atualizar_relatorio_e_resumo()
                self.view.set_status(message)
    
    def gerar_dados_teste(self):
        if self.view.confirmar_acao("Gerar Dados", "Isso irá apagar todos os dados atuais. Continuar?"):
            success, message = self.model.gerar_dados_teste()
            if success:
                self.iniciar_app()
                self.view.set_status(message)

    def ao_fechar(self):
        config = {'last_company': self.view.get_empresa_ativa()}
        self.model.save_config(config)
        self.model.save_all_data()
        self.view.destruir()