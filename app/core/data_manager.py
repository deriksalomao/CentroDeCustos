# app/core/data_manager.py
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import random
# Adicionamos o VEICULOS_FILE
from .constants import LANCAMENTOS_FILE, EMPRESAS_FILE, CATEGORIAS_FILE, CONFIG_FILE_PATH, VEICULOS_FILE

class DataManager:
    def __init__(self):
        # ADICIONAMOS A COLUNA "Veículo"
        self.colunas = ["Data", "Empresa", "Centro de Custo", "Veículo", "Categoria", "Descrição", "Tipo", "Valor"]
        
        self.df_lancamentos = pd.DataFrame(columns=self.colunas)
        self.dados_empresas = {}
        self.categorias = []
        self.veiculos = [] # Nova lista para os veículos
        self.config = {}
        self.load_all_data()

    def load_all_data(self):
        if os.path.exists(LANCAMENTOS_FILE) and os.path.getsize(LANCAMENTOS_FILE) > 0:
            df = pd.read_csv(LANCAMENTOS_FILE, parse_dates=["Data"])
            # Adiciona a coluna 'Veículo' se ela não existir nos dados antigos
            if 'Veículo' not in df.columns:
                df['Veículo'] = 'N/A'
            self.df_lancamentos = df
        
        try:
            with open(EMPRESAS_FILE, 'r', encoding='utf-8') as f: self.dados_empresas = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): self.dados_empresas = {"Sua Transportadora": ["Administrativo", "Operacional"]}
        
        try:
            with open(CATEGORIAS_FILE, 'r', encoding='utf-8') as f: self.categorias = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): self.categorias = ["Combustível", "Manutenção", "Pneus", "Salários", "Frete"]

        # Carrega os veículos do novo arquivo
        try:
            with open(VEICULOS_FILE, 'r', encoding='utf-8') as f: self.veiculos = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): self.veiculos = ["AAA-1111", "BBB-2222"]

    def save_all_data(self):
        self.df_lancamentos.to_csv(LANCAMENTOS_FILE, index=False)
        with open(EMPRESAS_FILE, 'w', encoding='utf-8') as f: json.dump(self.dados_empresas, f, ensure_ascii=False, indent=4)
        with open(CATEGORIAS_FILE, 'w', encoding='utf-8') as f: json.dump(self.categorias, f, ensure_ascii=False, indent=4)
        # Salva os veículos no novo arquivo
        with open(VEICULOS_FILE, 'w', encoding='utf-8') as f: json.dump(self.veiculos, f, ensure_ascii=False, indent=4)

    def adicionar_lancamento(self, dados):
        try:
            novo_lanc_df = pd.DataFrame([dados])
            novo_lanc_df['Data'] = pd.to_datetime(novo_lanc_df['Data'])
            novo_lanc_df['Valor'] = pd.to_numeric(novo_lanc_df['Valor'])
            self.df_lancamentos = pd.concat([self.df_lancamentos, novo_lanc_df], ignore_index=True)
            self.save_all_data()
            return True, "Lançamento adicionado com sucesso."
        except Exception as e:
            return False, f"Erro ao processar dados no DataManager: {e}"

    def editar_lancamento(self, index, dados_atualizados):
        for coluna, valor in dados_atualizados.items():
            self.df_lancamentos.loc[index, coluna] = valor
        self.save_all_data()
        return True, "Lançamento editado."
        
    def excluir_lancamento(self, index):
        self.df_lancamentos.drop(index, inplace=True)
        self.df_lancamentos.reset_index(drop=True, inplace=True)
        self.save_all_data()
        return True, "Lançamento excluído."
        
    def load_config(self):
        try:
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f: self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): self.config = {'last_company': 'Sua Transportadora'}
        return self.config
        
    def save_config(self, config_data):
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f: json.dump(config_data, f, ensure_ascii=False, indent=4)
        
    def get_lancamento_por_indice(self, index):
        return self.df_lancamentos.loc[index]
        
    def get_filtered_data(self, empresa, filtros):
        if not empresa or self.df_lancamentos.empty: return pd.DataFrame(columns=self.colunas)
        df = self.df_lancamentos[self.df_lancamentos['Empresa'] == empresa].copy()
        if not df.empty:
            df['Data'] = pd.to_datetime(df['Data'])
            start_date = pd.to_datetime(filtros['data_inicio'], dayfirst=True)
            end_date = pd.to_datetime(filtros['data_fim'], dayfirst=True).replace(hour=23, minute=59, second=59)
            df = df[(df['Data'] >= start_date) & (df['Data'] <= end_date)]
            
            # Adicionamos o filtro para Veículo
            if filtros['veiculo'] != "Todos": df = df[df['Veículo'] == filtros['veiculo']]
            if filtros['cc'] != "Todos": df = df[df['Centro de Custo'] == filtros['cc']]
            if filtros['categoria'] != "Todos": df = df[df['Categoria'] == filtros['categoria']]
            if filtros['tipo'] != "Todos": df = df[df['Tipo'] == filtros['tipo']]
        return df.sort_values(by="Data", ascending=False)
        
    def gerar_dados_teste(self):
        self.df_lancamentos = pd.DataFrame(columns=self.colunas)
        
        num_lancamentos = 150
        empresas = list(self.dados_empresas.keys())
        
        dados_teste = []
        start_date = datetime.now() - timedelta(days=365)
        
        for _ in range(num_lancamentos):
            empresa = random.choice(empresas)
            centro_custo = random.choice(self.dados_empresas[empresa])
            veiculo = random.choice(self.veiculos) # Usa a nova lista de veículos
            categoria = random.choice(self.categorias)
            tipo = random.choice(['Receita', 'Despesa'])
            data = start_date + timedelta(days=random.randint(0, 365), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            if tipo == 'Receita':
                descricao = f"Frete para Cliente X"
                valor = round(random.uniform(1000, 15000), 2)
            else:
                descricao = f"Abastecimento Posto Y"
                valor = round(random.uniform(50, 7500), 2)

            dados_teste.append([data, empresa, centro_custo, veiculo, categoria, descricao, tipo, valor])
            
        novos_lancamentos = pd.DataFrame(dados_teste, columns=self.colunas)
        self.df_lancamentos = pd.concat([self.df_lancamentos, novos_lancamentos], ignore_index=True)
        
        self.save_all_data()
        return True, "Dados de teste gerados com sucesso."