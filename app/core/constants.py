import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE_PATH = BASE_DIR / "config.json"
DATA_DIR = BASE_DIR / "data"
LANCAMENTOS_FILE = DATA_DIR / "lancamentos.csv"
EMPRESAS_FILE = DATA_DIR / "empresas_data.json"
CATEGORIAS_FILE = DATA_DIR / "categorias.json"
RECORRENCIAS_FILE = DATA_DIR / "recorrencias.json"
CENTRO_DE_CUSTO_FILE = DATA_DIR / "centro_de_custo.json"
VEICULOS_FILE = os.path.join(DATA_DIR, 'veiculos.json') 