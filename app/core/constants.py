# app/core/constants.py
import os

# Define o diretório de dados na raiz do projeto
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Arquivos de dados baseados em JSON e CSV
LANCAMENTOS_FILE = os.path.join(DATA_DIR, 'lancamentos.csv')
EMPRESAS_FILE = os.path.join(DATA_DIR, 'empresas.json')
VEICULOS_FILE = os.path.join(DATA_DIR, 'veiculos.json')
CENTROS_DE_CUSTO_FILE = os.path.join(DATA_DIR, 'centros_de_custo.json')
CATEGORIAS_FILE = os.path.join(DATA_DIR, 'categorias.json')
CLIENTES_FILE = os.path.join(DATA_DIR, 'clientes.json')

# Configurações do aplicativo
CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config.json')