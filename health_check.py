# health_check.py
import sys
import os
import pandas as pd

# Adiciona o diretório do projeto ao path do Python para encontrar os módulos da 'app'
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from app.core.data_manager import DataManager
    from app.core.constants import LANCAMENTOS_FILE, EMPRESAS_FILE, CATEGORIAS_FILE
except ImportError as e:
    print(f"\n[ERRO CRÍTICO] Não foi possível importar os módulos da aplicação: {e}")
    print("Verifique se a estrutura de pastas está correta e se você está executando o script da pasta raiz do projeto.")
    sys.exit(1)

# Classe para cores no terminal
class BColors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, success=True):
    """Imprime uma mensagem de status formatada."""
    status = f"{BColors.OKGREEN}[ OK ]{BColors.ENDC}" if success else f"{BColors.FAIL}[FALHA]{BColors.ENDC}"
    print(f"{status} {message}")

def run_test(title, test_function):
    """Executa uma função de teste e reporta o resultado."""
    print(f"\n--- {BColors.BOLD}{title}{BColors.ENDC} ---")
    try:
        success, details = test_function()
        print_status(details, success)
        return success
    except Exception as e:
        print_status(f"Ocorreu uma exceção inesperada: {e}", success=False)
        import traceback
        traceback.print_exc()
        return False

# --- DEFINIÇÃO DOS TESTES ---

def test_file_existence():
    """Verifica se os arquivos de dados essenciais existem."""
    files_to_check = [LANCAMENTOS_FILE, EMPRESAS_FILE, CATEGORIAS_FILE]
    missing_files = [str(f.name) for f in files_to_check if not f.exists()]
    if missing_files:
        return False, f"Arquivos de dados não encontrados: {', '.join(missing_files)}"
    return True, "Arquivos de dados essenciais encontrados."

def test_data_manager_loading():
    """Tenta instanciar o DataManager para verificar se os dados carregam sem erro."""
    dm = DataManager()
    if dm is None:
        return False, "Não foi possível instanciar o DataManager."
    if dm.df_lancamentos is None:
        return False, "O DataFrame de lançamentos não foi carregado corretamente."
    return True, "DataManager (Model) carregado com sucesso."

def test_dataframe_integrity():
    """Verifica as colunas e tipos de dados do DataFrame de lançamentos."""
    dm = DataManager()
    df = dm.df_lancamentos
    
    # Se o dataframe estiver vazio, o teste passa, pois não há o que verificar.
    if df.empty:
        return True, f"{BColors.WARNING}DataFrame de lançamentos está vazio. Teste de integridade pulado.{BColors.ENDC}"

    expected_cols = ["Data", "Empresa", "Centro de Custo", "Categoria", "Nome/Descrição", "Tipo", "Valor"]
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        return False, f"Colunas faltando no DataFrame: {', '.join(missing_cols)}"

    # Verifica os tipos de dados
    if not pd.api.types.is_datetime64_any_dtype(df['Data']):
        return False, "A coluna 'Data' não está no formato de data (datetime)."
    if not pd.api.types.is_numeric_dtype(df['Valor']):
        return False, "A coluna 'Valor' não é do tipo numérico."
            
    return True, "Estrutura do DataFrame (colunas e tipos) está correta."

def test_print_summary():
    """Imprime um resumo rápido dos dados carregados."""
    dm = DataManager()
    num_lanc = len(dm.df_lancamentos)
    num_emp = len(dm.dados_empresas)
    num_cat = len(dm.categorias)
    
    summary = (
        f"Sumário dos Dados:\n"
        f"      - Total de Lançamentos: {num_lanc}\n"
        f"      - Total de Empresas: {num_emp}\n"
        f"      - Total de Categorias: {num_cat}"
    )
    if num_lanc > 0:
        min_date = dm.df_lancamentos['Data'].min().strftime('%d/%m/%Y')
        max_date = dm.df_lancamentos['Data'].max().strftime('%d/%m/%Y')
        summary += f"\n      - Período dos Dados: {min_date} a {max_date}"
    
    return True, summary

# --- EXECUTOR PRINCIPAL ---

if __name__ == "__main__":
    print(f"{BColors.BOLD}=== INICIANDO FERRAMENTA DE DIAGNÓSTICO ==={BColors.ENDC}")
    
    tests = {
        "Verificação de Arquivos Essenciais": test_file_existence,
        "Carregamento do Model (DataManager)": test_data_manager_loading,
        "Integridade da Base de Lançamentos": test_dataframe_integrity,
        "Relatório Rápido": test_print_summary,
    }
    
    results = [run_test(title, func) for title, func in tests.items()]
    
    print("\n" + "="*50)
    if all(results):
        print(f"{BColors.OKGREEN}{BColors.BOLD}TODOS OS TESTES PASSARAM COM SUCESSO!{BColors.ENDC}")
        print("A lógica de dados da sua aplicação parece estar saudável.")
    else:
        print(f"{BColors.FAIL}{BColors.BOLD}UM OU MAIS TESTES FALHARAM.{BColors.ENDC}")
        print("Verifique as mensagens de [FALHA] acima para diagnosticar o problema.")
    print("="*50 + "\n")