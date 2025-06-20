# Conteúdo CORRETO para: app/core/data_manager.py
import os
import json
import pandas as pd
from datetime import datetime
from app.core.constants import (
    EMPRESAS_FILE, CATEGORIAS_FILE, LANCAMENTOS_FILE, RECORRENCIAS_FILE, 
    CONFIG_FILE_PATH, DATA_DIR
)

class DataManager:
    def __init__(self, app):
        self.app = app
        self.colunas = ["Data", "Empresa", "Centro de Custo", "Categoria", "Nome/Descrição", "Tipo", "Valor"]
        self.df_lancamentos = pd.DataFrame(columns=self.colunas)
        self.dados_empresas = {"Empresa Padrão": ["Geral"]}
        self.categorias = ["Geral"]
        self.recorrencias = []

    def load_all_data(self):
        # CORREÇÃO: Usando a variável EMPRESAS_FILE
        if os.path.exists(EMPRESAS_FILE):
            try:
                with open(EMPRESAS_FILE, 'r', encoding='utf-8') as f: self.dados_empresas = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError): pass
        
        if os.path.exists(CATEGORIAS_FILE):
            try:
                with open(CATEGORIAS_FILE, 'r', encoding='utf-8') as f: 
                    self.categorias = json.load(f)
                    if "Geral" not in self.categorias: self.categorias.insert(0, "Geral")
            except (json.JSONDecodeError, FileNotFoundError): pass

        if os.path.exists(LANCAMENTOS_FILE):
            try:
                self.df_lancamentos = pd.read_csv(LANCAMENTOS_FILE)
                if not self.df_lancamentos.empty: self.df_lancamentos['Data'] = pd.to_datetime(self.df_lancamentos['Data'])
            except Exception: self.df_lancamentos = pd.DataFrame(columns=self.colunas)
        
        if os.path.exists(RECORRENCIAS_FILE):
            try:
                with open(RECORRENCIAS_FILE, 'r', encoding='utf-8') as f: self.recorrencias = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError): pass

    def save_all_data(self):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            self.df_lancamentos.to_csv(LANCAMENTOS_FILE, index=False)
            # CORREÇÃO: Usando a variável EMPRESAS_FILE
            with open(EMPRESAS_FILE, 'w', encoding='utf-8') as f: json.dump(self.dados_empresas, f, indent=4, ensure_ascii=False)
            with open(CATEGORIAS_FILE, 'w', encoding='utf-8') as f: json.dump(self.categorias, f, indent=4, ensure_ascii=False)
            with open(RECORRENCIAS_FILE, 'w', encoding='utf-8') as f: json.dump(self.recorrencias, f, indent=4, ensure_ascii=False)
            self.app.set_status("Dados guardados com sucesso!")
        except Exception as e: self.app.set_status(f"Erro ao guardar dados: {e}")

    def save_config(self):
        try:
            configs = {'data_inicio': self.app.date_inicio.get_date().strftime('%Y-%m-%d'), 'data_fim': self.app.date_fim.get_date().strftime('%Y-%m-%d')}
            # CORREÇÃO: Usando a variável CONFIG_FILE_PATH
            with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f: json.dump(configs, f, indent=4)
        except Exception as e: print(f"Erro ao salvar configurações: {e}") 

    def load_config(self):
        # CORREÇÃO: Usando a variável CONFIG_FILE_PATH
        if os.path.exists(CONFIG_FILE_PATH):
            try:
                with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f: configs = json.load(f)
                if 'data_inicio' in configs: self.app.date_inicio.set_date(datetime.strptime(configs['data_inicio'], '%Y-%m-%d'))
                if 'data_fim' in configs: self.app.date_fim.set_date(datetime.strptime(configs['data_fim'], '%Y-%m-%d'))
                self.app.atualizar_relatorio()
            except Exception as e: print(f"Erro ao carregar configurações: {e}")