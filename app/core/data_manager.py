# app/core/data_manager.py
import sqlite3
import pandas as pd
import json
from .constants import DATABASE_FILE, CONFIG_FILE_PATH

class DataManager:
    def __init__(self):
        self.db_path = DATABASE_FILE
        self._criar_tabelas_se_nao_existir()
        self.dados_empresas = {}
        self.categorias = []
        self.veiculos = []
        self.clientes = []

    def _get_conexao(self):
        return sqlite3.connect(self.db_path)

    def _criar_tabelas_se_nao_existir(self):
        with self._get_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lancamentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Data TEXT NOT NULL, Empresa TEXT, Centro_de_Custo TEXT, Veículo TEXT,
                    Categoria TEXT, Descrição TEXT, Tipo TEXT, Valor REAL,
                    Cliente TEXT, Status TEXT, Litros REAL, Preco_Litro REAL, KM_Odometro INTEGER
                )
            ''')
            cursor.execute('CREATE TABLE IF NOT EXISTS empresas (nome TEXT PRIMARY KEY)')
            cursor.execute('CREATE TABLE IF NOT EXISTS centros_custo (nome TEXT, empresa_nome TEXT, PRIMARY KEY(nome, empresa_nome), FOREIGN KEY(empresa_nome) REFERENCES empresas(nome))')
            cursor.execute('CREATE TABLE IF NOT EXISTS categorias (nome TEXT PRIMARY KEY)')
            cursor.execute('CREATE TABLE IF NOT EXISTS veiculos (placa TEXT PRIMARY KEY)')
            cursor.execute('CREATE TABLE IF NOT EXISTS clientes (nome TEXT PRIMARY KEY)')
            conn.commit()

    def load_all_data_from_db(self):
        with self._get_conexao() as conn:
            cursor = conn.cursor()
            self.categorias = [row[0] for row in cursor.execute('SELECT nome FROM categorias ORDER BY nome').fetchall()]
            self.veiculos = [row[0] for row in cursor.execute('SELECT placa FROM veiculos ORDER BY placa').fetchall()]
            self.clientes = [row[0] for row in cursor.execute('SELECT nome FROM clientes ORDER BY nome').fetchall()]
            empresas_db = cursor.execute('SELECT nome FROM empresas ORDER BY nome').fetchall()
            self.dados_empresas = {}
            for (nome_empresa,) in empresas_db:
                ccs = [row[0] for row in cursor.execute('SELECT nome FROM centros_custo WHERE empresa_nome = ? ORDER BY nome', (nome_empresa,)).fetchall()]
                self.dados_empresas[nome_empresa] = ccs

    def get_filtered_data(self, empresa, filtros):
        query = "SELECT id, Data, Empresa, Centro_de_Custo, Veículo, Categoria, Descrição, Tipo, Valor, Cliente, Status FROM lancamentos WHERE Empresa = ?"
        params = [empresa]
        if filtros:
            try:
                start_date = pd.to_datetime(filtros['data_inicio'], dayfirst=True).strftime('%Y-%m-%d 00:00:00')
                end_date = pd.to_datetime(filtros['data_fim'], dayfirst=True).strftime('%Y-%m-%d 23:59:59')
                query += " AND Data BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            except (ValueError, TypeError): pass
            
            if filtros.get('cc') and filtros['cc'] != "Todos": query += " AND Centro_de_Custo = ?"; params.append(filtros['cc'])
            if filtros.get('veiculo') and filtros['veiculo'] != "Todos": query += " AND Veículo = ?"; params.append(filtros['veiculo'])
            if filtros.get('categoria') and filtros['categoria'] != "Todos": query += " AND Categoria = ?"; params.append(filtros['categoria'])
            if filtros.get('tipo') and filtros['tipo'] != "Todos": query += " AND Tipo = ?"; params.append(filtros['tipo'])
            if filtros.get('cliente') and filtros['cliente'] != "Todos": query += " AND Cliente = ?"; params.append(filtros['cliente'])
            if filtros.get('status') and filtros['status'] != "Todos": query += " AND Status = ?"; params.append(filtros['status'])
        query += " ORDER BY Data DESC"
        
        with self._get_conexao() as conn:
            df = pd.read_sql_query(query, conn, params=params)
            if not df.empty: df['Data'] = pd.to_datetime(df['Data'])
            df.set_index('id', inplace=True)
        return df

    def adicionar_entidade(self, nome_tabela, nome_coluna, valor):
        if not valor or not valor.strip(): return False, "O nome não pode estar em branco."
        try:
            with self._get_conexao() as conn: conn.execute(f"INSERT INTO {nome_tabela} ({nome_coluna}) VALUES (?)", (valor,))
            self.load_all_data_from_db()
            return True, f"{valor} adicionado com sucesso."
        except sqlite3.IntegrityError: return False, f"O item '{valor}' já existe."
    
    def adicionar_centro_custo(self, nome_empresa, nome_cc):
        if not nome_cc or not nome_cc.strip(): return False, "O nome não pode estar em branco."
        try:
            with self._get_conexao() as conn: conn.execute("INSERT INTO centros_custo (nome, empresa_nome) VALUES (?, ?)", (nome_cc, nome_empresa))
            self.load_all_data_from_db()
            return True, f"Centro de custo '{nome_cc}' adicionado."
        except sqlite3.IntegrityError: return False, "Este centro de custo já existe para esta empresa."

    def adicionar_lancamento(self, dados):
        for col in ['Cliente', 'Status', 'Litros', 'Preco_Litro', 'KM_Odometro']: dados.setdefault(col, None)
        dados['Data'] = dados['Data'].isoformat()
        query = '''
            INSERT INTO lancamentos (Data, Empresa, Centro_de_Custo, Veículo, Categoria, Descrição, Tipo, Valor, Cliente, Status, Litros, Preco_Litro, KM_Odometro)
            VALUES (:Data, :Empresa, :Centro_de_Custo, :Veículo, :Categoria, :Descrição, :Tipo, :Valor, :Cliente, :Status, :Litros, :Preco_Litro, :KM_Odometro)
        '''
        try:
            with self._get_conexao() as conn: conn.execute(query, dados)
            return True, "Lançamento adicionado com sucesso."
        except Exception as e: return False, f"Erro ao adicionar na base de dados: {e}"

    def get_lancamento_por_indice(self, index):
        with self._get_conexao() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM lancamentos WHERE id = ?", (index,)).fetchone()
        return dict(row) if row else None

    def editar_lancamento(self, index, dados_atualizados):
        if 'Data' in dados_atualizados: dados_atualizados['Data'] = dados_atualizados['Data'].isoformat()
        set_clause = ", ".join([f"{k} = :{k}" for k in dados_atualizados.keys()])
        query = f"UPDATE lancamentos SET {set_clause} WHERE id = :id"
        dados_atualizados['id'] = index
        try:
            with self._get_conexao() as conn: conn.execute(query, dados_atualizados)
            return True, "Lançamento editado com sucesso."
        except Exception as e: return False, f"Erro ao editar na base de dados: {e}"

    def excluir_lancamento(self, index):
        try:
            with self._get_conexao() as conn: conn.execute("DELETE FROM lancamentos WHERE id = ?", (index,))
            return True, "Lançamento excluído com sucesso."
        except Exception as e: return False, f"Erro ao excluir da base de dados: {e}"

    def verificar_uso_entidade(self, coluna_lancamentos, valor):
        with self._get_conexao() as conn:
            cursor = conn.cursor()
            if not coluna_lancamentos: return False
            query = f'SELECT COUNT(id) FROM lancamentos WHERE "{coluna_lancamentos}" = ?'
            cursor.execute(query, (valor,))
            count = cursor.fetchone()[0]
        return count > 0

    def excluir_entidade(self, tabela, coluna, valor):
        try:
            with self._get_conexao() as conn: conn.execute(f"DELETE FROM {tabela} WHERE {coluna} = ?", (valor,))
            self.load_all_data_from_db()
            return True, f"Item '{valor}' excluído com sucesso."
        except Exception as e: return False, f"Erro ao excluir item: {e}"

    def load_config(self):
        try:
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): return {'last_company': ''}
        
    def save_config(self, config_data):
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f: json.dump(config_data, f, ensure_ascii=False, indent=4)