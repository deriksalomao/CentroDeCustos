import pandas as pd
import sqlite3
from .database import get_connection

class DataManager:
    def __init__(self):
        pass

    def get_lookup_data(self, tabela, empresa=None):
        """Obtém dados de categorias, veículos, etc., filtrando por empresa se aplicável."""
        conn = get_connection()
        cursor = conn.cursor()
        if empresa:
            cursor.execute(f"SELECT nome FROM {tabela} WHERE empresa = ?", (empresa,))
        else:
            cursor.execute(f"SELECT nome FROM {tabela}")
        
        resultados = [row['nome'] for row in cursor.fetchall()]
        conn.close()
        return resultados

    def get_empresas(self):
        return self.get_lookup_data('empresas')

    def get_centros_de_custo(self, empresa):
        return self.get_lookup_data('centros_de_custo', empresa)

    def get_veiculos(self, empresa):
        return self.get_lookup_data('veiculos', empresa)

    def get_categorias(self, empresa):
        return self.get_lookup_data('categorias', empresa)

    def get_clientes(self, empresa):
        return self.get_lookup_data('clientes', empresa)

    def get_filtered_data(self, empresa, filtros):
        conn = get_connection()
        query = "SELECT * FROM lancamentos WHERE empresa = ?"
        params = [empresa]

        if filtros.get('data_inicio') and filtros.get('data_fim'):
            query += " AND data >= ? AND data <= ?"
            params.extend([filtros['data_inicio'], filtros['data_fim']])

        filtro_map = {
            'Centro_de_Custo': 'cc', 'Veículo': 'veiculo', 
            'Categoria': 'categoria', 'Tipo': 'tipo', 
            'Cliente': 'cliente', 'Status': 'status'
        }

        for col_db, filtro_key in filtro_map.items():
            if filtros.get(filtro_key) and filtros[filtro_key] != "Todos":
                col_lower = col_db.lower()
                if col_db == 'Centro_de_Custo': col_lower = 'centro_de_custo'
                if col_db == 'Veículo': col_lower = 'veiculo'
                
                query += f" AND {col_lower} = ?"
                params.append(filtros[filtro_key])

        query += " ORDER BY data DESC"

        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        df.rename(columns={
            'id': 'id', 'data': 'Data', 'empresa': 'Empresa',
            'centro_de_custo': 'Centro_de_Custo', 'veiculo': 'Veículo',
            'categoria': 'Categoria', 'descricao': 'Descrição',
            'tipo': 'Tipo', 'valor': 'Valor', 'cliente': 'Cliente', 'status': 'Status'
        }, inplace=True)
        
        if not df.empty:
            df['Data'] = pd.to_datetime(df['Data'])
            df.set_index('id', inplace=True)
        else:
            df = df.set_index('id') if 'id' in df.columns else df
            
        return df

    def get_resumo_financeiro(self, df):
        if df.empty:
            return {'receitas': 0, 'despesas': 0, 'saldo': 0}
        receitas = df[df['Tipo'] == 'Receita']['Valor'].sum()
        despesas = df[df['Tipo'] == 'Despesa']['Valor'].sum()
        saldo = receitas - despesas
        return {'receitas': receitas, 'despesas': despesas, 'saldo': saldo}

    def adicionar_lancamento(self, dados):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO lancamentos (data, empresa, centro_de_custo, veiculo, categoria, descricao, tipo, valor, cliente, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados.get('Data'), dados.get('Empresa'), dados.get('Centro_de_Custo'),
                dados.get('Veículo'), dados.get('Categoria'), dados.get('Descrição'),
                dados.get('Tipo'), dados.get('Valor'), dados.get('Cliente'), dados.get('Status')
            ))
            conn.commit()
            return True, "Lançamento adicionado com sucesso."
        except Exception as e:
            return False, f"Erro ao adicionar: {e}"
        finally:
            conn.close()

    def excluir_lancamento(self, lancamento_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM lancamentos WHERE id = ?", (lancamento_id,))
            conn.commit()
            return True, "Lançamento excluído com sucesso."
        except Exception as e:
            return False, f"Erro ao excluir: {e}"
        finally:
            conn.close()

    def adicionar_item_generico(self, tabela, dados):
        conn = get_connection()
        cursor = conn.cursor()
        nome = dados.get('Nome')
        empresa = dados.get('Empresa')
        
        try:
            if tabela == 'empresas':
                cursor.execute("SELECT id FROM empresas WHERE nome = ?", (nome,))
                if cursor.fetchone():
                    return False, f"Erro: Empresa '{nome}' já existe."
                cursor.execute("INSERT INTO empresas (nome) VALUES (?)", (nome,))
            else:
                cursor.execute(f"SELECT id FROM {tabela} WHERE nome = ? AND empresa = ?", (nome, empresa))
                if cursor.fetchone():
                    return False, f"Erro: Item '{nome}' já existe."
                cursor.execute(f"INSERT INTO {tabela} (nome, empresa) VALUES (?, ?)", (nome, empresa))
            conn.commit()
            return True, f"{nome} adicionado com sucesso."
        except Exception as e:
            return False, f"Erro ao adicionar: {e}"
        finally:
            conn.close()

    def get_lancamento_by_id(self, lancamento_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lancamentos WHERE id = ?", (lancamento_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'Data': row['data'], 'Empresa': row['empresa'], 
                'Centro_de_Custo': row['centro_de_custo'], 'Veículo': row['veiculo'],
                'Categoria': row['categoria'], 'Descrição': row['descricao'],
                'Tipo': row['tipo'], 'Valor': row['valor'], 
                'Cliente': row['cliente'], 'Status': row['status']
            }
        return None

    def atualizar_lancamento(self, lancamento_id, dados):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            set_clause = []
            params = []
            col_map = {
                'Data': 'data', 'Empresa': 'empresa', 'Centro_de_Custo': 'centro_de_custo',
                'Veículo': 'veiculo', 'Categoria': 'categoria', 'Descrição': 'descricao',
                'Tipo': 'tipo', 'Valor': 'valor', 'Cliente': 'cliente', 'Status': 'status'
            }
            for key, val in dados.items():
                if key in col_map:
                    set_clause.append(f"{col_map[key]} = ?")
                    params.append(val)
            
            params.append(lancamento_id)
            query = f"UPDATE lancamentos SET {', '.join(set_clause)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            return True, "Lançamento atualizado com sucesso."
        except Exception as e:
            return False, f"Erro ao atualizar: {e}"
        finally:
            conn.close()

    def excluir_item_generico(self, tabela, nome_item, empresa=None):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            if tabela == 'empresas':
                cursor.execute("DELETE FROM empresas WHERE nome = ?", (nome_item,))
            else:
                cursor.execute(f"DELETE FROM {tabela} WHERE nome = ? AND empresa = ?", (nome_item, empresa))
            conn.commit()
            return True, f"Item '{nome_item}' excluído com sucesso."
        except Exception as e:
            return False, f"Erro ao excluir: {e}"
        finally:
            conn.close()

    def get_lancamentos_para_relatorio_veiculo(self, empresa, placa, mes, ano):
        conn = get_connection()
        mes_str = f"{mes:02d}"
        
        query = """
            SELECT * FROM lancamentos 
            WHERE empresa = ? 
            AND veiculo = ? 
            AND strftime('%m', data) = ? 
            AND strftime('%Y', data) = ?
        """
        params = [empresa, placa, mes_str, str(ano)]
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if df.empty:
            return pd.DataFrame()

        df.rename(columns={
            'id': 'id', 'data': 'Data', 'empresa': 'Empresa',
            'centro_de_custo': 'Centro_de_Custo', 'veiculo': 'Veiculo',
            'categoria': 'Categoria', 'descricao': 'Descrição',
            'tipo': 'Tipo', 'valor': 'Valor', 'cliente': 'Cliente', 'status': 'Status'
        }, inplace=True)
        
        df['Data'] = pd.to_datetime(df['Data'])
        return df