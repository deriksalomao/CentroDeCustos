# app/core/controller.py
from tkinter import messagebox, filedialog
import pandas as pd
from datetime import datetime
import math

class AppController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.current_page = 1
        self.items_per_page = 100
        self.full_filtered_df = pd.DataFrame()

    def iniciar_app(self):
        self.model.load_all_data_from_db()
        config = self.model.load_config()
        empresas = list(self.model.dados_empresas.keys())
        self.view.atualizar_empresas_combobox(empresas)
        last_company = config.get('last_company', '')
        if last_company in empresas:
            self.view.set_empresa_ativa(last_company)
        elif empresas:
            self.view.set_empresa_ativa(empresas[0])
        self.on_empresa_selecionada()

    def on_empresa_selecionada(self, event=None):
        self.aplicar_filtros_e_resetar_pagina()

    def aplicar_filtros_e_resetar_pagina(self):
        self.current_page = 1
        self.atualizar_relatorio_e_resumo()

    def atualizar_relatorio_e_resumo(self):
        empresa_ativa = self.view.get_empresa_ativa()
        if not empresa_ativa:
            self.view.set_status("Nenhuma empresa selecionada.")
            return

        filtros = self.view.get_filtros()
        self.full_filtered_df = self.model.get_filtered_data(empresa_ativa, filtros)
        total_items = len(self.full_filtered_df)
        total_pages = math.ceil(total_items / self.items_per_page) if total_items > 0 else 1
        
        if self.current_page > total_pages:
            self.current_page = total_pages
            
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        df_paginado = self.full_filtered_df.iloc[start_index:end_index]
        
        self.model.load_all_data_from_db()
        centros_custo = self.model.dados_empresas.get(empresa_ativa, [])
        self.view.atualizar_filtros_combobox(centros_custo, self.model.veiculos, self.model.clientes, self.model.categorias)
        
        self.view.atualizar_treeview_lancamentos(df_paginado)
        self.view.atualizar_resumo_financeiro(self.full_filtered_df)
        self.view.atualizar_graficos(self.full_filtered_df)
        self.view.update_pagination_controls(self.current_page, total_pages)
        self.view.set_status(f"A exibir {len(df_paginado)} de {total_items} registos.")

    def go_to_next_page(self):
        total_pages = math.ceil(len(self.full_filtered_df) / self.items_per_page) if len(self.full_filtered_df) > 0 else 1
        if self.current_page < total_pages:
            self.current_page += 1
            self.atualizar_relatorio_e_resumo()

    def go_to_previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.atualizar_relatorio_e_resumo()

    def change_items_per_page(self, event=None):
        self.items_per_page = int(self.view.combo_itens_por_pagina.get())
        self.aplicar_filtros_e_resetar_pagina()

    def limpar_filtros(self):
        self.view.resetar_campos_de_filtro()
        self.aplicar_filtros_e_resetar_pagina()
    
    def exportar_para_excel(self):
        if self.full_filtered_df.empty:
            self.view.mostrar_info("Não há dados para exportar.")
            return
        try:
            caminho_arquivo = filedialog.asksaveasfilename(title="Salvar Relatório", defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
            if caminho_arquivo:
                df_export = self.full_filtered_df.copy().rename(columns={"Centro_de_Custo": "Centro de Custo"})
                df_export['Data'] = pd.to_datetime(df_export['Data']).dt.strftime('%d/%m/%Y')
                df_export.to_excel(caminho_arquivo, index=False, engine='openpyxl')
                self.view.mostrar_info("Relatório exportado!")
        except Exception as e:
            self.view.mostrar_info(f"Erro ao exportar:\n{e}")

    def adicionar_entidade(self, nome_tabela, nome_coluna, valor):
        success, message = self.model.adicionar_entidade(nome_tabela, nome_coluna, valor)
        if success:
            self.atualizar_relatorio_e_resumo()
        self.view.set_status(message)
        return success, message

    def adicionar_cliente(self): self.adicionar_entidade("clientes", "nome", self.view.get_novo_cliente().strip().title())
    def adicionar_veiculo(self): self.adicionar_entidade("veiculos", "placa", self.view.get_novo_veiculo().strip().upper())
    def adicionar_categoria(self): self.adicionar_entidade("categorias", "nome", self.view.get_nova_categoria().strip().title())
    def adicionar_empresa(self): self.adicionar_entidade("empresas", "nome", self.view.get_nova_empresa().strip().title())
        
    def adicionar_centro_custo(self):
        empresa = self.view.get_empresa_ativa()
        novo_cc = self.view.get_novo_cc().strip().title()
        success, message = self.model.adicionar_centro_custo(empresa, novo_cc)
        if success:
            self.atualizar_relatorio_e_resumo()
        self.view.set_status(message)

    def abrir_janela_gerenciamento(self):
        self.view.abrir_janela_gerenciamento()

    def abrir_janela_gerenciar_clientes(self):
        self.view.abrir_janela_gerenciar_entidade(
            titulo="Gerenciar Clientes", lista_itens=self.model.clientes,
            callback_adicionar=lambda nome: self.adicionar_entidade("clientes", "nome", nome),
            callback_excluir=lambda nome: self.excluir_entidade_com_verificacao("clientes", nome)
        )
        
    def abrir_janela_gerenciar_veiculos(self):
        self.view.abrir_janela_gerenciar_entidade(
            titulo="Gerenciar Veículos", lista_itens=self.model.veiculos,
            callback_adicionar=lambda placa: self.adicionar_entidade("veiculos", "placa", placa.upper()),
            callback_excluir=lambda placa: self.excluir_entidade_com_verificacao("veiculos", placa)
        )

    def abrir_janela_gerenciar_categorias(self):
        self.view.abrir_janela_gerenciar_entidade(
            titulo="Gerenciar Categorias", lista_itens=self.model.categorias,
            callback_adicionar=lambda nome: self.adicionar_entidade("categorias", "nome", nome),
            callback_excluir=lambda nome: self.excluir_entidade_com_verificacao("categorias", nome)
        )

    def excluir_entidade_com_verificacao(self, tabela, valor):
        mapa_colunas = {"clientes": "Cliente", "veiculos": "Veículo", "categorias": "Categoria"}
        coluna_lancamentos = mapa_colunas.get(tabela)
        
        if self.model.verificar_uso_entidade(coluna_lancamentos, valor):
            return False, f"Não é possível excluir '{valor}', pois está a ser utilizado em lançamentos."
        
        coluna_tabela = "nome" if tabela != "veiculos" else "placa"
        success, message = self.model.excluir_entidade(tabela, coluna_tabela, valor)
        if success:
            self.atualizar_relatorio_e_resumo()
        return success, message
        
    def abrir_janela_novo_lancamento(self):
        empresa = self.view.get_empresa_ativa()
        self.view.criar_janela_lancamento(titulo="Adicionar Lançamento", centros_custo=self.model.dados_empresas.get(empresa, []), veiculos=self.model.veiculos, clientes=self.model.clientes, categorias=self.model.categorias, callback_salvar=self.salvar_novo_lancamento)

    def salvar_novo_lancamento(self, dados):
        dados['Empresa'] = self.view.get_empresa_ativa()
        if "Centro de Custo" in dados: dados["Centro_de_Custo"] = dados.pop("Centro de Custo")
        success, message = self.model.adicionar_lancamento(dados)
        if success:
            self.aplicar_filtros_e_resetar_pagina()
        self.view.set_status(message)

    def abrir_janela_edicao(self):
        selecionado = self.view.tree_relatorio.focus()
        if not selecionado: return
        index = int(selecionado)
        dados_atuais = self.model.get_lancamento_por_indice(index)
        if dados_atuais is None: return
        
        empresa = dados_atuais['Empresa']
        self.view.criar_janela_lancamento(titulo="Editar Lançamento", centros_custo=self.model.dados_empresas.get(empresa, []), veiculos=self.model.veiculos, clientes=self.model.clientes, categorias=self.model.categorias, dados_edicao=dados_atuais, callback_salvar=lambda dados: self.salvar_edicao_lancamento(index, dados))

    def salvar_edicao_lancamento(self, index, dados):
        if "Centro de Custo" in dados: dados["Centro_de_Custo"] = dados.pop("Centro de Custo")
        success, message = self.model.editar_lancamento(index, dados)
        if success:
            self.aplicar_filtros_e_resetar_pagina()
        self.view.set_status(message)

    def excluir_lancamento_selecionado(self):
        selecionado = self.view.tree_relatorio.focus()
        if not selecionado:
            self.view.mostrar_info("Nenhum lançamento selecionado.")
            return
        index = int(selecionado)
        if self.view.confirmar_acao("Confirmar Exclusão", "Deseja excluir o lançamento selecionado?"):
            success, message = self.model.excluir_lancamento(index)
            if success:
                self.aplicar_filtros_e_resetar_pagina()
                self.view.set_status(message)
    
    def ao_fechar(self):
        config = {'last_company': self.view.get_empresa_ativa()}
        self.model.save_config(config)
        self.view.destruir()