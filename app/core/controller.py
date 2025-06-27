# app/core/controller.py
import math
import pandas as pd
from tkinter import filedialog
from .data_manager import DataManager
import typing

if typing.TYPE_CHECKING:
    from app.ui.app_principal import AppPrincipal

class AppController:
    def __init__(self, model: DataManager, view: 'AppPrincipal'):
        self.model = model
        self.view = view
        self.items_per_page = 100
        self.current_page = 1
        self.full_filtered_df = pd.DataFrame()
        self.view.set_controller(self)
        self.initialize_app()

    def initialize_app(self):
        empresas = self.model.get_empresas()
        if empresas:
            self.view.update_empresa_dropdown(empresas, set_default=True)
            self.update_all_filters()
            self.aplicar_filtros_e_resetar_pagina()
        else:
            self.view.set_status("Nenhuma empresa encontrada. Adicione uma empresa para começar.")
    
    def on_empresa_selecionada(self, event=None):
        self.update_all_filters()
        self.aplicar_filtros_e_resetar_pagina()

    def update_all_filters(self):
        empresa_ativa = self.view.get_empresa_ativa()
        
        # Atualiza os dropdowns de filtro na VIEW PRINCIPAL
        self.view.update_dropdown('tipo', ["Receita", "Despesa"])
        self.view.update_dropdown('status', ["Pendente", "Pago", "Atrasado"])
        
        # Atualiza os dropdowns de CADASTRO e FILTRO que dependem da empresa
        if empresa_ativa:
            centros_custo = self.model.get_centros_de_custo(empresa_ativa)
            veiculos = self.model.get_veiculos(empresa_ativa)
            categorias = self.model.get_categorias(empresa_ativa)
            clientes = self.model.get_clientes(empresa_ativa)
            
            # Atualiza filtros na aba de registros
            self.view.update_dropdown('cc', centros_custo)
            self.view.update_dropdown('veiculo', veiculos)
            self.view.update_dropdown('categoria', categorias)
            self.view.update_dropdown('cliente', clientes)

            # ATUALIZA OS NOVOS COMBOBOXES DE EXCLUSÃO NO PAINEL ESQUERDO
            self.view.update_cadastro_dropdown('Centro de Custo', centros_custo)
            self.view.update_cadastro_dropdown('Veículo', veiculos)
            self.view.update_cadastro_dropdown('Categoria', categorias)
            self.view.update_cadastro_dropdown('Cliente', clientes)
        else:
            # Limpa os dropdowns se nenhuma empresa for selecionada
            for item in ['cc', 'veiculo', 'categoria', 'cliente']:
                self.view.update_dropdown(item, [])
            for item in ['Centro de Custo', 'Veículo', 'Categoria', 'Cliente']:
                self.view.update_cadastro_dropdown(item, [])

        # Dropdown de empresas é sempre atualizado independentemente da seleção
        empresas = self.model.get_empresas()
        self.view.update_cadastro_dropdown('Empresa', empresas)


    def aplicar_filtros_e_resetar_pagina(self):
        self.current_page = 1
        self.atualizar_relatorio_e_resumo()

    def limpar_filtros(self):
        self.view.reset_filters()
        self.aplicar_filtros_e_resetar_pagina()

    def atualizar_relatorio_e_resumo(self):
        empresa_ativa = self.view.get_empresa_ativa()
        if not empresa_ativa:
            self.view.set_status("Nenhuma empresa selecionada.")
            self.view.update_lancamentos_treeview(pd.DataFrame())
            self.view.update_financial_summary(0, 0, 0)
            self.view.painel_direito.graficos_view.atualizar_todos_os_graficos(pd.DataFrame())
            return

        filtros = self.view.get_filtros()
        self.full_filtered_df = self.model.get_filtered_data(empresa_ativa, filtros)
        
        total_items = len(self.full_filtered_df)
        total_pages = math.ceil(total_items / self.items_per_page) if total_items > 0 else 1
        
        self.view.update_page_info(self.current_page, total_pages)
        self.atualizar_treeview_lancamentos()
        self.atualizar_resumo_financeiro()
        self.view.painel_direito.graficos_view.atualizar_todos_os_graficos(self.full_filtered_df)
    
    def atualizar_treeview_lancamentos(self):
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        page_df = self.full_filtered_df.iloc[start_index:end_index]
        self.view.update_lancamentos_treeview(page_df)

    def atualizar_resumo_financeiro(self):
        resumo = self.model.get_resumo_financeiro(self.full_filtered_df)
        self.view.update_financial_summary(resumo['receitas'], resumo['despesas'], resumo['saldo'])
    
    def change_page(self, direction):
        total_items = len(self.full_filtered_df)
        total_pages = math.ceil(total_items / self.items_per_page) if total_items > 0 else 1
        
        new_page = self.current_page + direction
        if 1 <= new_page <= total_pages:
            self.current_page = new_page
            self.view.update_page_info(self.current_page, total_pages)
            self.atualizar_treeview_lancamentos()
    
    def excluir_lancamento_selecionado(self):
        selected_id_str = self.view.get_selected_lancamento_id()
        if selected_id_str is None:
            self.view.set_status("Nenhum lançamento selecionado para excluir.")
            return
        try:
            selected_id_int = int(selected_id_str)

        except (ValueError, TypeError):
            self.view.set_status("Erro: ID de lançamento inválido.")
            return
        
        if self.view.ask_yes_no("Tem certeza que deseja excluir o lançamento selecionado?"):
            success, message = self.model.excluir_lancamento(selected_id_int)
            if success:
                self.aplicar_filtros_e_resetar_pagina()
            self.view.set_status(message)

    def salvar_novo_lancamento(self, dados):
        dados['Empresa'] = self.view.get_empresa_ativa()
        if not dados['Empresa']:
            self.view.set_status("Erro: Nenhuma empresa está ativa para associar o lançamento.")
            return

        success, message = self.model.adicionar_lancamento(dados)
        if success:
            self.aplicar_filtros_e_resetar_pagina()
        self.view.set_status(message)

    def editar_lancamento_selecionado(self):
        selected_id_str = self.view.get_selected_lancamento_id()
        if selected_id_str is None:
            self.view.set_status("Nenhum lançamento selecionado para editar.")
            return
        
        selected_id_int = int(selected_id_str)
        dados_lancamento = self.model.get_lancamento_by_id(selected_id_int)

        if dados_lancamento:
            self.view.painel_direito._criar_janela_lancamento(
                "Editar Lançamento", 
                lambda dados: self.salvar_lancamento_editado(selected_id_int, dados),
                dados_edicao=dados_lancamento
            )

    def salvar_lancamento_editado(self, lancamento_id, dados):
        success, message = self.model.atualizar_lancamento(lancamento_id, dados)
        if success:
            self.aplicar_filtros_e_resetar_pagina()
        self.view.set_status(message)

    def adicionar_item_rapido(self, tipo_item, valor_item):
        tabela_map = {
            'Cliente': 'clientes', 'Veículo': 'veiculos', 'Centro de Custo': 'centros_de_custo',
            'Categoria': 'categorias', 'Empresa': 'empresas'
        }
        
        success, message = False, "Ocorreu um erro desconhecido."

        if not valor_item or not valor_item.strip():
            message = f"O nome para '{tipo_item}' não pode estar vazio."
            self.view.set_status(message)
            return

        valor_item = valor_item.strip()

        if tipo_item == 'Empresa':
            success, message = self.model.adicionar_item_generico(tabela_map[tipo_item], {'Nome': valor_item})
            if success:
                empresas = self.model.get_empresas()
                self.view.update_empresa_dropdown(empresas)
                self.view.set_empresa_ativa(valor_item)
                self.on_empresa_selecionada()
        else:
            empresa_ativa = self.view.get_empresa_ativa()
            if not empresa_ativa:
                message = "Selecione uma empresa antes de adicionar outros itens."
            else:
                dados = {'Nome': valor_item, 'Empresa': empresa_ativa}
                success, message = self.model.adicionar_item_generico(tabela_map[tipo_item], dados)

        if success:
            self.update_all_filters()
        
        self.view.set_status(message)

    def exportar_para_excel(self):
        if self.full_filtered_df.empty:
            self.view.set_status("Não há dados para exportar.")
            return
        
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if not filepath:
            return

        try:
            df_to_export = self.full_filtered_df.copy()
            if 'Data' in df_to_export.columns:
                df_to_export['Data'] = pd.to_datetime(df_to_export['Data']).dt.strftime('%d/%m/%Y %H:%M:%S')
            if df_to_export.index.name == 'id':
                df_to_export.reset_index(inplace=True)
            
            df_to_export.to_excel(filepath, index=False, engine='openpyxl')
            self.view.set_status(f"Dados exportados com sucesso para {filepath}")
        except Exception as e:
            self.view.set_status(f"Erro ao exportar: {e}")
            
    def excluir_item_rapido(self, tipo_item, valor_item):
        if not valor_item:
            self.view.set_status(f"Nenhum item do tipo '{tipo_item}' selecionado para exclusão.")
            return

        tabela_map = {
            'Cliente': 'clientes', 'Veículo': 'veiculos', 
            'Centro de Custo': 'centros_de_custo',
            'Categoria': 'categorias', 'Empresa': 'empresas'
        }
        
        empresa_ativa = self.view.get_empresa_ativa()
        if tipo_item != 'Empresa' and not empresa_ativa:
            self.view.set_status("Selecione uma empresa antes de excluir um item.")
            return

        if not self.view.ask_yes_no(f"Tem certeza que deseja excluir '{valor_item}'?"):
            return

        success, message = self.model.excluir_item_generico(
            tabela_map[tipo_item], 
            valor_item, 
            empresa_ativa if tipo_item != 'Empresa' else None
        )

        if success:
            if tipo_item == 'Empresa':
                 empresas = self.model.get_empresas()
                 self.view.update_empresa_dropdown(empresas, set_default=True)
            self.update_all_filters()
            self.aplicar_filtros_e_resetar_pagina()

        self.view.set_status(message)