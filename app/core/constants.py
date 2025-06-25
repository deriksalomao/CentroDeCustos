import os
import sys

def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funciona para dev e para o PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

LANCAMENTOS_FILE = resource_path(os.path.join(DATA_DIR, 'lancamentos.csv'))
EMPRESAS_FILE = resource_path(os.path.join(DATA_DIR, 'empresas_e_cc.json'))
CATEGORIAS_FILE = resource_path(os.path.join(DATA_DIR, 'categorias.json'))
VEICULOS_FILE = resource_path(os.path.join(DATA_DIR, 'veiculos.json'))
CLIENTES_FILE = resource_path(os.path.join(DATA_DIR, 'clientes.json'))
CONFIG_FILE_PATH = resource_path(os.path.join(DATA_DIR, 'config.json'))