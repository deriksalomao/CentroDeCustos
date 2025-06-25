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
        config = self.model.load_config()
        self.view.atualizar_empresas_combobox(list(self.model.dados_empresas.keys()))
        last_company = config.get('last_company', 'Empresa Padrão')
        if last_company in self.model.dados_empresas:
            self.view.set_empresa_ativa(last_company)
        else:
            empresas = list(self.model.dados_empresas.keys())
            if empresas: self.view.set_empresa_ativa(empresas[0])
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
        
        if self.current_page > total_pages: self.current_page = total_pages
            
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        df_paginado = self.full_filtered_df.iloc[start_index:end_index]
        
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
            self.view.mostrar_info("Não há dados para exportar com os filtros atuais.")
            return
        try:
            caminho_arquivo = filedialog.asksaveasfilename(title="Salvar Relatório como...", defaultextension=".xlsx", filetypes=[("Arquivos Excel", "*.xlsx"), ("Todos os ficheiros", "*.*")])
            if caminho_arquivo:
                df_para_exportar = self.full_filtered_df.copy()
                df_para_exportar['Data'] = pd.to_datetime(df_para_exportar['Data']).dt.strftime('%d/%m/%Y')
                df_para_exportar.to_excel(caminho_arquivo, index=False, engine='openpyxl')
                self.view.set_status(f"Relatório salvo com sucesso em: {caminho_arquivo}")
                self.view.mostrar_info("Relatório exportado com sucesso!")
        except Exception as e:
            self.view.mostrar_info(f"Ocorreu um erro ao exportar o ficheiro:\n{e}")
            self.view.set_status("Erro ao exportar relatório.")

    def adicionar_cliente(self, *args):
        novo_cliente = self.view.get_novo_cliente().strip().title()
        if not novo_cliente: return
        if novo_cliente in self.model.clientes:
            self.view.mostrar_info("Cliente já cadastrado."); return
        self.model.clientes.append(novo_cliente)
        self.on_empresa_selecionada()
        self.view.set_status(f"Cliente '{novo_cliente}' adicionado.")

    def adicionar_veiculo(self, *args):
        novo_veiculo = self.view.get_novo_veiculo().strip().upper()
        if not novo_veiculo: return
        if novo_veiculo in self.model.veiculos:
            self.view.mostrar_info("Veículo já cadastrado."); return
        self.model.veiculos.append(novo_veiculo)
        self.on_empresa_selecionada()
        self.view.set_status(f"Veículo '{novo_veiculo}' adicionado.")

    def adicionar_empresa(self, *args):
        nova_empresa = self.view.get_nova_empresa().strip().title()
        if not nova_empresa: return
        if nova_empresa in self.model.dados_empresas:
            self.view.mostrar_info("Empresa já existe."); return
        self.model.dados_empresas[nova_empresa] = ["Geral"]
        self.view.atualizar_empresas_combobox(list(self.model.dados_empresas.keys()))
        self.view.set_empresa_ativa(nova_empresa)
        self.on_empresa_selecionada()
        self.view.set_status(f"Empresa '{nova_empresa}' adicionada.")

    def adicionar_categoria(self, *args):
        nova_cat = self.view.get_nova_categoria().strip().title()
        if not nova_cat: return
        if nova_cat in self.model.categorias:
            self.view.mostrar_info("Categoria já existe."); return
        self.model.categorias.append(nova_cat)
        self.on_empresa_selecionada()
        self.view.set_status(f"Categoria '{nova_cat}' adicionada.")
        
    def adicionar_centro_custo(self, *args):
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
        veiculos = ["N/A"] + self.model.veiculos
        clientes = ["N/A"] + self.model.clientes
        categorias = self.model.categorias
        self.view.criar_janela_lancamento(
            titulo="Adicionar Novo Lançamento",
            centros_custo=centros_custo,
            veiculos=veiculos,
            clientes=clientes,
            categorias=categorias,
            callback_salvar=self.salvar_novo_lancamento
        )

    def salvar_novo_lancamento(self, dados_lancamento):
        dados_lancamento['Empresa'] = self.view.get_empresa_ativa()
        success, message = self.model.adicionar_lancamento(dados_lancamento)
        if success:
            self.aplicar_filtros_e_resetar_pagina()
            self.view.set_status(message)

    def abrir_janela_edicao(self, event):
        index = self.view.get_selected_lancamento_index()
        if index is None: return
        dados_atuais = self.model.get_lancamento_por_indice(index).to_dict()
        
        empresa = dados_atuais['Empresa']
        centros_custo = self.model.dados_empresas.get(empresa, [])
        veiculos = ["N/A"] + self.model.veiculos
        clientes = ["N/A"] + self.model.clientes
        categorias = self.model.categorias
        
        self.view.criar_janela_lancamento(
            titulo="Editar Lançamento",
            centros_custo=centros_custo,
            veiculos=veiculos,
            clientes=clientes,
            categorias=categorias,
            dados_edicao=dados_atuais,
            callback_salvar=lambda dados: self.salvar_edicao_lancamento(index, dados)
        )

    def salvar_edicao_lancamento(self, index, dados_atualizados):
        success, message = self.model.editar_lancamento(index, dados_atualizados)
        if success:
            self.aplicar_filtros_e_resetar_pagina()
            self.view.set_status(message)

    def excluir_lancamento_selecionado(self):
        index = self.view.get_selected_lancamento_index()
        if index is None: 
            self.view.mostrar_info("Nenhum lançamento selecionado."); return
        if self.view.confirmar_acao("Confirmar Exclusão", "Deseja excluir o lançamento selecionado?"):
            success, message = self.model.excluir_lancamento(index)
            if success:
                self.aplicar_filtros_e_resetar_pagina()
                self.view.set_status(message)
    
    def gerar_dados_teste(self):
        if self.view.confirmar_acao("Gerar Dados", "Isso irá apagar todos os dados atuais. Continuar?"):
            success, message = self.model.gerar_dados_teste()
            if success:
                self.model.load_all_data() # Recarrega os dados da memória
                empresas = list(self.model.dados_empresas.keys())
                self.view.atualizar_empresas_combobox(empresas)
                if empresas:
                    self.view.set_empresa_ativa(empresas[0]) # Seleciona a primeira empresa
                
                self.view.resetar_campos_de_filtro() # CORREÇÃO CRÍTICA: Reseta os filtros de data
                self.aplicar_filtros_e_resetar_pagina() # Atualiza a UI com os novos dados
                self.view.set_status(message)
            else:
                self.view.mostrar_info(f"Erro ao gerar dados: {message}")

    def ao_fechar(self):
        config = {'last_company': self.view.get_empresa_ativa()}
        self.model.save_config(config)
        self.model.save_all_data()
        self.view.destruir()