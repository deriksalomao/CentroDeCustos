import os
from app.core.utils import resource_path

# Define o diretório de dados na raiz do projeto
DATA_DIR = resource_path("data")

# Arquivos de dados baseados em JSON e CSV
LANCAMENTOS_FILE = f"{DATA_DIR}/lancamentos.csv"
CLIENTES_FILE = f"{DATA_DIR}/clientes.json"
VEICULOS_FILE = f"{DATA_DIR}/veiculos.json"
CENTROS_DE_CUSTO_FILE = f"{DATA_DIR}/centros_de_custo.json"
CATEGORIAS_FILE = f"{DATA_DIR}/categorias.json"
EMPRESAS_FILE = f"{DATA_DIR}/empresas.json"
RECORRENCIAS_FILE = f"{DATA_DIR}/recorrencias.json"
USERS_FILE = f"{DATA_DIR}/users.json"

# Configurações do aplicativo
CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config.json')