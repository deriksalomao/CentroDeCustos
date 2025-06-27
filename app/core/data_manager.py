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
            # Garante que a coluna de data seja do tipo datetime
            self.df_lancamentos['Data'] = pd.to_datetime(self.df_lancamentos['Data'], format='%Y-%m-%d')
        except FileNotFoundError:
            # Se o arquivo não existe, cria um DataFrame vazio
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
                # Se o arquivo não existe ou está vazio/corrompido, cria uma estrutura vazia
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
        
        # Define o índice como o índice original do DataFrame para manter a rastreabilidade
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
        # Converte o dicionário para um DataFrame de uma linha para concatenar
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
        # A 'tabela' aqui é a chave para o nosso dicionário de dados (ex: 'clientes', 'veiculos')
        if tabela not in self.data_lookups:
            return False, "Tipo de cadastro inválido."

        # Verifica se o item já existe para evitar duplicatas
        nome_item = dados.get('Nome')
        empresa_item = dados.get('Empresa') # Pode ser None para 'empresas'
        
        for item in self.data_lookups[tabela]:
            if item.get('Nome') == nome_item and item.get('Empresa') == empresa_item:
                 return False, f"Erro: Item '{nome_item}' já existe."

        self.data_lookups[tabela].append(dados)
        self.save_data(tabela)
        return True, f"{dados.get('Nome')} adicionado com sucesso."