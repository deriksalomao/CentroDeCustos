# app/core/utils.py
import sys
import os

def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, funciona para dev e para PyInstaller """
    try:
        # PyInstaller cria uma pasta temp e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Se não estiver rodando via PyInstaller, o caminho base é a pasta do script principal
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)