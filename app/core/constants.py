# app/core/constants.py
# Armazena os nomes de todos os ficheiros de configuração e dados.

import os

# Encontra o caminho absoluto para a pasta raiz do projeto
# __file__ -> .../app/core/constants.py
# dirname(__file__) -> .../app/core
# dirname(dirname(__file__)) -> .../app
# dirname(dirname(dirname(__file__))) -> /caminho/completo/para/CENTRODECUSTOS/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define o caminho para a pasta 'data' e para o arquivo de config na raiz
DATA_DIR = os.path.join(BASE_DIR, 'data')
CONFIG_FILE_PATH = os.path.join(BASE_DIR, 'config.json')

# Cria os caminhos completos para cada arquivo de dados
LANCAMENTOS_FILE = os.path.join(DATA_DIR, 'lancamentos.csv')
EMPRESAS_DATA_FILE = os.path.join(DATA_DIR, 'empresas_data.json')
CATEGORIAS_FILE = os.path.join(DATA_DIR, 'categorias.json')
RECORRENCIAS_FILE = os.path.join(DATA_DIR, 'recorrencias.json')

# Renomeado para evitar conflito de nomes e aponta para o caminho completo
CONFIG_FILE = CONFIG_FILE_PATH