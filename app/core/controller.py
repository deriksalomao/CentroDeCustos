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
        if empresa_ativa:
            self.view.update_dropdown('cc', self.model.get_centros_de_custo(empresa_ativa))
            self.view.update_dropdown('veiculo', self.model.get_veiculos(empresa_ativa))
            self.view.update_dropdown('categoria', self.model.get_categorias(empresa_ativa))
            self.view.update_dropdown('cliente', self.model.get_clientes(empresa_ativa))
            self.view.update_dropdown('tipo', ["Receita", "Despesa"])
            self.view.update_dropdown('status', ["Pendente", "Pago", "Atrasado"])

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
            # Limpa a TreeView e o resumo se nenhuma empresa estiver selecionada
            self.view.update_lancamentos_treeview(pd.DataFrame())
            self.view.update_financial_summary(0, 0, 0)
            # Limpa também os gráficos
            self.view.painel_direito.graficos_view.atualizar_todos_os_graficos(pd.DataFrame())
            return

        filtros = self.view.get_filtros()
        self.full_filtered_df = self.model.get_filtered_data(empresa_ativa, filtros)
        
        total_items = len(self.full_filtered_df)
        total_pages = math.ceil(total_items / self.items_per_page) if total_items > 0 else 1
        
        self.view.update_page_info(self.current_page, total_pages)
        self.atualizar_treeview_lancamentos()
        self.atualizar_resumo_financeiro()
        
        # --- ALTERAÇÃO AQUI ---
        # Chame a atualização dos gráficos com os dados filtrados
        self.view.painel_direito.graficos_view.atualizar_todos_os_graficos(self.full_filtered_df)
        # ---------------------
    
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
            # Note que estamos passando um novo callback para o salvamento
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

        # Lógica corrigida: trata 'Empresa' como um caso especial
        if tipo_item == 'Empresa':
            success, message = self.model.adicionar_item_generico(tabela_map[tipo_item], {'Nome': valor_item})
            if success:
                # Após adicionar uma nova empresa, atualiza a lista principal de empresas
                empresas = self.model.get_empresas()
                self.view.update_empresa_dropdown(empresas)
                # Seleciona a empresa recém-criada
                self.view.set_empresa_ativa(valor_item)
                self.on_empresa_selecionada() # Força a atualização dos outros filtros
        else:
            # Para todos os outros tipos, exige uma empresa ativa
            empresa_ativa = self.view.get_empresa_ativa()
            if not empresa_ativa:
                message = "Selecione uma empresa antes de adicionar outros itens."
            else:
                dados = {'Nome': valor_item, 'Empresa': empresa_ativa}
                success, message = self.model.adicionar_item_generico(tabela_map[tipo_item], dados)

        # Se qualquer adição foi bem-sucedida (inclusive de empresa), atualiza os filtros
        if success:
            self.update_all_filters()
        
        self.view.set_status(message)

    def exportar_para_excel(self):
        if self.full_filtered_df.empty:
            self.view.set_status("Não há dados para exportar.")
            return
        
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                               filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if not filepath:
            return

        try:
            df_to_export = self.full_filtered_df.copy()
            if 'Data' in df_to_export.columns:
                # Formata a data para um formato amigável no Excel
                df_to_export['Data'] = pd.to_datetime(df_to_export['Data']).dt.strftime('%d/%m/%Y %H:%M:%S')
            
            # Resetar o índice para que o 'id' (se existir) vire uma coluna
            if df_to_export.index.name == 'id':
                df_to_export.reset_index(inplace=True)
            
            df_to_export.to_excel(filepath, index=False, engine='openpyxl')
            self.view.set_status(f"Dados exportados com sucesso para {filepath}")
        except Exception as e:
            self.view.set_status(f"Erro ao exportar: {e}")