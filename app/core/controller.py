import math
import pandas as pd
from tkinter import filedialog
from .data_manager import DataManager
import typing
from app.ui.ui_cadastros import CadastrosManager
from app.ui.ui_relatorio_veiculo import RelatorioVeiculo

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
        """
        Ao selecionar uma nova empresa, agora apenas atualizamos as opções de filtro.
        A aplicação dos filtros e atualização da tela só ocorrerá quando o usuário
        clicar em 'Aplicar Filtros'.
        """
        self.view.set_status("Empresa alterada. Aplique os filtros para ver os resultados.")
        self.update_all_filters()

    def update_all_filters(self):
        empresa_ativa = self.view.get_empresa_ativa()
        
        self.view.update_dropdown('tipo', ["Receita", "Despesa"])
        self.view.update_dropdown('status', ["Pendente", "Pago", "Atrasado"])
        
        if empresa_ativa:
            centros_custo = self.model.get_centros_de_custo(empresa_ativa)
            veiculos = self.model.get_veiculos(empresa_ativa)
            categorias = self.model.get_categorias(empresa_ativa)
            clientes = self.model.get_clientes(empresa_ativa)
            
            self.view.update_dropdown('cc', centros_custo)
            self.view.update_dropdown('veiculo', veiculos)
            self.view.update_dropdown('categoria', categorias)
            self.view.update_dropdown('cliente', clientes)

            self.view.update_cadastro_dropdown('Centro de Custo', centros_custo)
            self.view.update_cadastro_dropdown('Veículo', veiculos)
            self.view.update_cadastro_dropdown('Categoria', categorias)
            self.view.update_cadastro_dropdown('Cliente', clientes)
        else:
            for item in ['cc', 'veiculo', 'categoria', 'cliente']:
                self.view.update_dropdown(item, [])
            for item in ['Centro de Custo', 'Veículo', 'Categoria', 'Cliente']:
                self.view.update_cadastro_dropdown(item, [])

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

        self.view.set_status("Atualizando dados...")
        filtros = self.view.get_filtros()
        self.full_filtered_df = self.model.get_filtered_data(empresa_ativa, filtros)
        
        total_items = len(self.full_filtered_df)
        total_pages = math.ceil(total_items / self.items_per_page) if total_items > 0 else 1
        
        self.view.update_page_info(self.current_page, total_pages)
        self.atualizar_treeview_lancamentos()
        self.atualizar_resumo_financeiro()
        self.view.painel_direito.graficos_view.atualizar_todos_os_graficos(self.full_filtered_df)
        self.view.set_status("Pronto")
    
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
                lambda d: self.salvar_lancamento_editado(selected_id_int, d),
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
        if not valor_item or not valor_item.strip():
            self.view.set_status(f"O nome para '{tipo_item}' não pode estar vazio.")
            return
        valor_item = valor_item.strip()
        if tipo_item == 'Empresa':
            success, message = self.model.adicionar_item_generico(tabela_map[tipo_item], {'Nome': valor_item})
            if success:
                empresas = self.model.get_empresas()
                self.view.update_empresa_dropdown(empresas)
                self.view.set_empresa_ativa(valor_item)
                self.on_empresa_selecionada(None)
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
        if not filepath: return
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
                self.on_empresa_selecionada(None)
            else:
                self.update_all_filters()
                self.aplicar_filtros_e_resetar_pagina()
        self.view.set_status(message)

    def abrir_janela_gestao_cadastros(self):
        """Abre a janela de gestão de cadastros."""
        if not self.view.get_empresa_ativa():
            self.view.set_status("Por favor, selecione uma empresa primeiro.")
            return
        
        CadastrosManager(master=self.view.master, controller=self)
    
    def abrir_janela_relatorio_veiculo(self):
        """Abre a janela do relatório de custo de veículo."""
        if not self.view.get_empresa_ativa():
            from tkinter import messagebox
            messagebox.showwarning("Nenhuma Empresa Selecionada", 
                                 "Por favor, selecione uma empresa ativa antes de gerar relatórios.")
            return
        
        RelatorioVeiculo(master=self.view.master, controller=self)

    def processar_relatorio_veiculo(self, placa, mes_ano_str):
        """
        Busca, calcula e retorna os dados formatados para o relatório de veículo.
        """
        self.view.set_status(f"Processando relatório para {placa} em {mes_ano_str}...")

        try:
            mes, ano = map(int, mes_ano_str.split('/'))
        except ValueError:
            from tkinter import messagebox
            messagebox.showerror("Formato Inválido", "Por favor, use o formato MM/AAAA para o período.", parent=self.view.master)
            return [], {}

        empresa = self.view.get_empresa_ativa()
        df = self.model.get_lancamentos_para_relatorio_veiculo(empresa, placa, mes, ano)

        if df.empty:
            self.view.set_status(f"Nenhum lançamento encontrado para {placa} em {mes_ano_str}.")
            return [], {"total_despesas": 0, "total_frete": 0, "saldo_final": 0, "indice_medio": 0}

        colunas_custo = ['PNEU', 'PECAS', 'BORRACHARIA', 'MECANICO', 'COMBUSTIVEL', 'AJUDANTE', 'MOTORISTA', 'VR DESPESAS', 'ICMS']

        colunas_receita = ['FRETE VAS', 'AGREGADO']
        
        df_pivot = df.pivot_table(
            index=df['Data'].dt.date, 
            columns='Categoria', 
            values='Valor', 
            aggfunc='sum'
        ).fillna(0)
        
        for col in colunas_custo + colunas_receita:
            if col not in df_pivot.columns:
                df_pivot[col] = 0

        df_pivot['TOTAL'] = df_pivot[colunas_custo].sum(axis=1)
        df_pivot['SALDO'] = df_pivot['FRETE VAS'] - df_pivot['TOTAL']
        df_pivot['INDICE'] = (df_pivot['SALDO'] / df_pivot['FRETE VAS'].replace(0, 1)) * 100

        dados_para_tabela = []
        df_pivot = df_pivot.reset_index()
        df_pivot = df_pivot.rename(columns={'index': 'DATA'})
        df_pivot['DATA'] = pd.to_datetime(df_pivot['DATA']).dt.strftime('%d/%m/%Y')

        ordem_colunas = ['DATA'] + colunas_custo[:8] + ['AGREGADO', 'FRETE VAS', 'ICMS'] + ['TOTAL', 'SALDO', 'INDICE']
        df_final = df_pivot[ordem_colunas]

        for col in df_final.columns:
            if col not in ['DATA', 'INDICE']:
                df_final[col] = df_final[col].apply(lambda x: f"{x:,.2f}")
        df_final['INDICE'] = df_final['INDICE'].apply(lambda x: f"{x:.2f}%")

        dados_para_tabela = df_final.values.tolist()

        total_despesas = df_pivot['TOTAL'].sum()
        total_frete = df_pivot['FRETE VAS'].sum()
        saldo_final = total_frete - total_despesas
        indice_medio = (saldo_final / total_frete if total_frete else 0) * 100

        totais = {
            "total_despesas": total_despesas,
            "total_frete": total_frete,
            "saldo_final": saldo_final,
            "indice_medio": indice_medio
        }

        self.view.set_status("Relatório gerado com sucesso.")
        return dados_para_tabela, totais
    
    def exportar_relatorio_veiculo(self, dados_relatorio):
        """Exporta os dados do relatório de veículo para um arquivo Excel."""
        from tkinter import messagebox
        if not dados_relatorio:
            messagebox.showinfo("Nenhum Dado", "Não há dados na tabela para exportar.", parent=self.view.master)
            return
            
        messagebox.showinfo("Em Desenvolvimento", "A exportação para Excel será implementada em breve!", parent=self.view.master)