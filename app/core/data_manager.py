# app/core/data_manager.py
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import random
from .constants import LANCAMENTOS_FILE, EMPRESAS_FILE, CATEGORIAS_FILE, CONFIG_FILE_PATH, VEICULOS_FILE, CLIENTES_FILE

class DataManager:
    def __init__(self):
        self.colunas = ["Data", "Empresa", "Centro de Custo", "Veículo", "Categoria", "Descrição", "Tipo", "Valor", "Cliente", "Status", "Litros", "Preco_Litro", "KM_Odometro"]
        
        self.df_lancamentos = pd.DataFrame(columns=self.colunas)
        self.dados_empresas = {}
        self.categorias = []
        self.veiculos = []
        self.clientes = []
        self.config = {}
        self.load_all_data()

    def load_all_data(self):
        if os.path.exists(LANCAMENTOS_FILE) and os.path.getsize(LANCAMENTOS_FILE) > 0:
            df = pd.read_csv(LANCAMENTOS_FILE, parse_dates=["Data"], keep_default_na=False, na_values=[''])
            for col in ['Veículo', 'Cliente', 'Status', 'Litros', 'Preco_Litro', 'KM_Odometro']:
                if col not in df.columns:
                    df[col] = 'N/A'
            self.df_lancamentos = df
        
        try:
            with open(EMPRESAS_FILE, 'r', encoding='utf-8') as f: self.dados_empresas = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): self.dados_empresas = {"Sua Transportadora": ["Administrativo", "Operacional"]}
        
        try:
            with open(CATEGORIAS_FILE, 'r', encoding='utf-8') as f: self.categorias = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): self.categorias = ["Combustível", "Manutenção", "Pneus", "Salários", "Frete"]

        try:
            with open(VEICULOS_FILE, 'r', encoding='utf-8') as f: self.veiculos = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): self.veiculos = ["AAA-1111", "BBB-2222"]

        try:
            with open(CLIENTES_FILE, 'r', encoding='utf-8') as f: self.clientes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): self.clientes = ["Cliente Exemplo A", "Cliente Exemplo B"]

    def save_all_data(self):
        self.df_lancamentos.to_csv(LANCAMENTOS_FILE, index=False)
        with open(EMPRESAS_FILE, 'w', encoding='utf-8') as f: json.dump(self.dados_empresas, f, ensure_ascii=False, indent=4)
        with open(CATEGORIAS_FILE, 'w', encoding='utf-8') as f: json.dump(self.categorias, f, ensure_ascii=False, indent=4)
        with open(VEICULOS_FILE, 'w', encoding='utf-8') as f: json.dump(self.veiculos, f, ensure_ascii=False, indent=4)
        with open(CLIENTES_FILE, 'w', encoding='utf-8') as f: json.dump(self.clientes, f, ensure_ascii=False, indent=4)

    def adicionar_lancamento(self, dados):
        try:
            for col in ['Cliente', 'Status', 'Litros', 'Preco_Litro', 'KM_Odometro']:
                dados.setdefault(col, 'N/A')
            
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
            
            if filtros.get('veiculo') != "Todos": df = df[df['Veículo'] == filtros['veiculo']]
            if filtros.get('cc') != "Todos": df = df[df['Centro de Custo'] == filtros['cc']]
            if filtros.get('categoria') != "Todos": df = df[df['Categoria'] == filtros['categoria']]
            if filtros.get('tipo') != "Todos": df = df[df['Tipo'] == filtros['tipo']]
            if filtros.get('cliente') and filtros['cliente'] != "Todos": df = df[df['Cliente'] == filtros['cliente']]
            if filtros.get('status') and filtros['status'] != "Todos": df = df[df['Status'] == filtros['status']]
            
        return df.sort_values(by="Data", ascending=False)
        
    def gerar_dados_teste(self):
        num_lancamentos = 150
        empresas = list(self.dados_empresas.keys())
        dados_teste = []
        start_date = datetime.now() - timedelta(days=365)
        
        if not all([empresas, self.categorias, self.veiculos, self.clientes]):
             return False, "É necessário cadastrar ao menos uma Empresa, Categoria, Veículo e Cliente para gerar dados de teste."

        for _ in range(num_lancamentos):
            empresa = random.choice(empresas)
            centro_custo = random.choice(self.dados_empresas[empresa])
            veiculo = random.choice(self.veiculos)
            categoria = random.choice(self.categorias)
            tipo = random.choice(['Receita', 'Despesa'])
            data = start_date + timedelta(days=random.randint(0, 365), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            cliente, status, litros, preco_litro, km = 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'
            
            if tipo == 'Receita':
                descricao = f"Frete #{random.randint(100, 999)}"
                valor = round(random.uniform(1000, 15000), 2)
                cliente = random.choice(self.clientes)
                status = random.choice(['Pago', 'Pendente'])
            else:
                descricao = f"Despesa Geral"
                valor = round(random.uniform(50, 500), 2)
                if categoria == "Combustível":
                    descricao = "Abastecimento"
                    litros = round(random.uniform(30, 100), 2)
                    preco_litro = round(random.uniform(5.0, 6.5), 2)
                    valor = round(litros * preco_litro, 2)
                    km = random.randint(100000, 500000)

            dados_teste.append([data, empresa, centro_custo, veiculo, categoria, descricao, tipo, valor, cliente, status, litros, preco_litro, km])
            
        self.df_lancamentos = pd.DataFrame(dados_teste, columns=self.colunas)
        self.save_all_data()
        return True, "Dados de teste gerados com sucesso."