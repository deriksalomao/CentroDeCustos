# app/core/constants.py
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_path, relative_path)

DATA_DIR = resource_path('data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DATABASE_FILE = os.path.join(DATA_DIR, 'transportadora.db')
CONFIG_FILE_PATH = os.path.join(DATA_DIR, 'config.json')