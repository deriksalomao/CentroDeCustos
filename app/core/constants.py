# Conteúdo CORRETO para: app/core/constants.py
import os
from pathlib import Path

# Define o diretório base do projeto (a pasta 'CentroDeCustos')
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Constrói os caminhos usando o operador de barra (/)
CONFIG_FILE_PATH = BASE_DIR / "config.json"
DATA_DIR = BASE_DIR / "data"
LANCAMENTOS_FILE = DATA_DIR / "lancamentos.csv"
EMPRESAS_FILE = DATA_DIR / "empresas_data.json"
CATEGORIAS_FILE = DATA_DIR / "categorias.json"
RECORRENCIAS_FILE = DATA_DIR / "recorrencias.json"
# --- LINHA ADICIONADA ---
CENTRO_DE_CUSTO_FILE = DATA_DIR / "centro_de_custo.json"