# uploaded:CentroDeCustos/app/core/constants.py
import os
from pathlib import Path

# --- ABORDAGEM MODERNA COM PATHLIB ---
# Define o diretório base do projeto (a pasta 'CentroDeCustos')
# Path(__file__) -> o arquivo atual (constants.py)
# .resolve() -> obtém o caminho absoluto
# .parent -> sobe um nível (para a pasta 'core')
# .parent -> sobe mais um nível (para a pasta 'app')
# .parent -> sobe mais um nível (para a raiz do projeto 'CentroDeCustos')
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Constrói os caminhos usando o operador de barra (/), que funciona em todos os SO
CONFIG_FILE_PATH = BASE_DIR / "config.json"
DATA_DIR = BASE_DIR / "data"
LANCAMENTOS_FILE = DATA_DIR / "lancamentos.csv"
EMPRESAS_FILE = DATA_DIR / "empresas_data.json"
CATEGORIAS_FILE = DATA_DIR / "categorias.json"
RECORRENCIAS_FILE = DATA_DIR / "recorrencias.json"

# --- CÓDIGO ANTIGO (COMENTADO PARA REFERÊNCIA) ---
# # Define o diretório base do projeto.
# # __file__ é o caminho para o arquivo atual (constants.py).
# # os.path.dirname() obtém o diretório desse arquivo.
# # Repetimos para subir na hierarquia de pastas até a raiz do projeto.
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # Caminhos para arquivos de configuração e dados
# CONFIG_FILE_PATH = os.path.join(BASE_DIR, 'config.json')
# CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')  # Redundante, pode ser removido
# DATA_DIR = os.path.join(BASE_DIR, 'data')
# LANCAMENTOS_FILE = os.path.join(DATA_DIR, 'lancamentos.csv')
# EMPRESAS_FILE = os.path.join(DATA_DIR, 'empresas_data.json')
# CATEGORIAS_FILE = os.path.join(DATA_DIR, 'categorias.json')
# RECORRENCIAS_FILE = os.path.join(DATA_DIR, 'recorrencias.json')