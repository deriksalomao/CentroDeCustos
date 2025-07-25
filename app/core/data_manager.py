# app/core/data_manager.py
import pandas as pd
import json
from .constants import (
    LANCAMENTOS_FILE, EMPRESAS_FILE, VEICULOS_FILE, CENTROS_DE_CUSTO_FILE,
    CATEGORIAS_FILE, CLIENTES_FILE
)

class DataManager:
    def __init__(self):
        self.file_map = {
            'empresas': EMPRESAS_FILE,
            'veiculos': VEICULOS_FILE,
            'centros_de_custo': CENTROS_DE_CUSTO_FILE,
            'categorias': CATEGORIAS_FILE,
            'clientes': CLIENTES_FILE
        }
        self.load_all_data()

    def load_all_data(self):
        """Carrega todos os arquivos de dados na memória."""
        try:
            self.df_lancamentos = pd.read_csv(LANCAMENTOS_FILE)
            self.df_lancamentos['Data'] = pd.to_datetime(self.df_lancamentos['Data'], format='%Y-%m-%d')
        except FileNotFoundError:
            self.df_lancamentos = pd.DataFrame(columns=[
                'Data', 'Empresa', 'Centro_de_Custo', 'Veículo', 'Categoria',
                'Descrição', 'Tipo', 'Valor', 'Cliente', 'Status'
            ])

        self.data_lookups = {}
        for name, path in self.file_map.items():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.data_lookups[name] = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                self.data_lookups[name] = []

    def save_data(self, data_key):
        """Salva um arquivo JSON específico."""
        if data_key in self.file_map:
            with open(self.file_map[data_key], 'w', encoding='utf-8') as f:
                json.dump(self.data_lookups[data_key], f, indent=4, ensure_ascii=False)

    def save_lancamentos(self):
        """Salva o DataFrame de lançamentos em CSV."""
        self.df_lancamentos.to_csv(LANCAMENTOS_FILE, index=False)

    def get_lookup_data(self, key, empresa=None):
        """Obtém dados de lookup (categorias, veículos, etc.), filtrando por empresa se aplicável."""
        items = self.data_lookups.get(key, [])
        if empresa:
            return [item['Nome'] for item in items if item.get('Empresa') == empresa]
        return [item['Nome'] for item in items]

    def get_empresas(self):
        return self.get_lookup_data('empresas')

    def get_centros_de_custo(self, empresa):
        return self.get_lookup_data('centros_de_custo', empresa)

    def get_veiculos(self, empresa):
        return self.get_lookup_data('veiculos', empresa)

    def get_categorias(self, empresa):
        return self.get_lookup_data('categorias', empresa)

    def get_clientes(self, empresa):
        return self.get_lookup_data('clientes', empresa)

    def get_filtered_data(self, empresa, filtros):
        df_filtered = self.df_lancamentos[self.df_lancamentos['Empresa'] == empresa].copy()

        if filtros.get('data_inicio') and filtros.get('data_fim'):
            start_date = pd.to_datetime(filtros['data_inicio'])
            end_date = pd.to_datetime(filtros['data_fim'])
            df_filtered = df_filtered[(df_filtered['Data'] >= start_date) & (df_filtered['Data'] <= end_date)]

        for col, filtro_key in [('Centro_de_Custo', 'cc'), ('Veículo', 'veiculo'), ('Categoria', 'categoria'), ('Tipo', 'tipo'), ('Cliente', 'cliente'), ('Status', 'status')]:
            if filtros.get(filtro_key) and filtros[filtro_key] != "Todos":
                df_filtered = df_filtered[df_filtered[col] == filtros[filtro_key]]
        
        df_filtered.index.name = 'id'
        return df_filtered.sort_values(by='Data', ascending=False)

    def get_resumo_financeiro(self, df):
        if df.empty:
            return {'receitas': 0, 'despesas': 0, 'saldo': 0}
        receitas = df[df['Tipo'] == 'Receita']['Valor'].sum()
        despesas = df[df['Tipo'] == 'Despesa']['Valor'].sum()
        saldo = receitas - despesas
        return {'receitas': receitas, 'despesas': despesas, 'saldo': saldo}

    def adicionar_lancamento(self, dados):

        novo_lancamento_df = pd.DataFrame([dados])
        self.df_lancamentos = pd.concat([self.df_lancamentos, novo_lancamento_df], ignore_index=True)
        self.save_lancamentos()
        return True, "Lançamento adicionado com sucesso."

    def excluir_lancamento(self, lancamento_id):
        if lancamento_id in self.df_lancamentos.index:
            self.df_lancamentos.drop(lancamento_id, inplace=True)
            self.save_lancamentos()
            return True, "Lançamento excluído com sucesso."
        return False, "Erro: Lançamento não encontrado."
    
    def adicionar_item_generico(self, tabela, dados):
        if tabela not in self.data_lookups:
            return False, "Tipo de cadastro inválido."

        nome_item = dados.get('Nome')
        empresa_item = dados.get('Empresa')
        
        for item in self.data_lookups[tabela]:
            if item.get('Nome') == nome_item and item.get('Empresa') == empresa_item:
                 return False, f"Erro: Item '{nome_item}' já existe."

        self.data_lookups[tabela].append(dados)
        self.save_data(tabela)
        return True, f"{dados.get('Nome')} adicionado com sucesso."

    def get_lancamento_by_id(self, lancamento_id):
        if lancamento_id in self.df_lancamentos.index:
            return self.df_lancamentos.loc[lancamento_id].to_dict()
        return None
    
    def get_lancamentos_para_relatorio_veiculo(self, empresa, placa, mes, ano):
        """
        Busca todos os lançamentos de um veículo específico em um determinado mês/ano.
        Retorna um DataFrame do Pandas com os dados relevantes.
        """
        try:
            df = self.get_table_as_df('lancamentos')
            if df.empty:
                return pd.DataFrame()

            df['Data'] = pd.to_datetime(df['Data'])

            df_filtrado = df[
                (df['Empresa'] == empresa) &
                (df['Veiculo'] == placa) &
                (df['Data'].dt.month == mes) &
                (df['Data'].dt.year == ano)
            ].copy()
            
            return df_filtrado
            
        except Exception as e:
            print(f"Erro ao buscar lançamentos para o relatório: {e}")
            return pd.DataFrame()

    def atualizar_lancamento(self, lancamento_id, dados):
        if lancamento_id in self.df_lancamentos.index:
            for chave, valor in dados.items():
                self.df_lancamentos.loc[lancamento_id, chave] = valor
            self.save_lancamentos()
            return True, "Lançamento atualizado com sucesso."
        return False, "Erro: Lançamento não encontrado."
    
    def excluir_item_generico(self, tabela, nome_item, empresa=None):
        if tabela not in self.data_lookups:
            return False, "Tipo de cadastro inválido."

        item_encontrado = False
        itens_originais = self.data_lookups[tabela]
        itens_filtrados = []
        for item in itens_originais:
            if item.get('Nome') != nome_item or (empresa and item.get('Empresa') != empresa):
                itens_filtrados.append(item)
            else:
                item_encontrado = True

        if not item_encontrado:
            return False, f"Erro: Item '{nome_item}' não encontrado para exclusão."

        self.data_lookups[tabela] = itens_filtrados
        self.save_data(tabela)
        return True, f"Item '{nome_item}' excluído com sucesso."