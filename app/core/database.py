import sqlite3
import os

DB_PATH = os.path.join("data", "centro_custos.db")

def get_connection():
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            empresa TEXT NOT NULL,
            centro_de_custo TEXT,
            veiculo TEXT,
            categoria TEXT,
            descricao TEXT,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            cliente TEXT,
            status TEXT
        )
    ''')
    tabelas_auxiliares = ['empresas', 'centros_de_custo', 'veiculos', 'categorias', 'clientes']
    
    for tabela in tabelas_auxiliares:
        if tabela == 'empresas':
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {tabela} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE
                )
            ''')
        else:
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {tabela} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    empresa TEXT NOT NULL
                )
            ''')
    conn.commit()
    conn.close()
setup_database()