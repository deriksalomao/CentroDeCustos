# Controle de Centro de Custos

## Descrição do Projeto

O "Controle de Centro de Custos" é uma aplicação de desktop desenvolvida em Python com `tkinter` e `ttkbootstrap` para auxiliar no gerenciamento financeiro, permitindo o registro, filtragem e visualização de receitas e despesas.

## Funcionalidades

* **Registro de Lançamentos:** Adicione novas receitas e despesas com detalhes como data, empresa, centro de custo, veículo, categoria, descrição, tipo e valor.
* **Filtros Avançados:** Filtre lançamentos por período (data de início e fim), centro de custo, veículo, categoria, tipo, cliente e status.
* **Exportação de Dados:** Exporte os lançamentos filtrados para um arquivo Excel.
* **Resumo Financeiro:** Visualize um resumo rápido de receitas, despesas e o saldo total, com cores indicativas (verde para saldo positivo/receita, vermelho para despesa/saldo negativo).
* **Cadastros Rápidos:** Adicione rapidamente novos clientes, veículos, centros de custo, categorias e empresas.
* **Gestão de Lançamentos Recorrentes:** Administre entradas e saídas que se repetem periodicamente.
* **Gráficos Visuais:** Visualize a evolução mensal de receitas vs. despesas e a distribuição de despesas por categoria através de gráficos.
* **Sistema de Login:** Acesso inicial seguro com um login simples (credenciais padrão: usuário `admin`, senha `admin`).

## Pré-requisitos

Certifique-se de ter o Python instalado em sua máquina (versão 3.x recomendada).

## Configuração e Instalação

Siga os passos abaixo para configurar e rodar o projeto localmente:

1.  **Clone o repositório (ou baixe os arquivos):**
    Se você estiver usando Git:
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd ControleDeCustos
    ```
    Caso contrário, baixe e extraia os arquivos para uma pasta.

2.  **Crie um Ambiente Virtual (Recomendado):**
    ```bash
    python -m venv .venv
    ```

3.  **Ative o Ambiente Virtual:**
    * **Windows:**
        ```bash
        .venv\Scripts\activate
        ```
    * **macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```

4.  **Instale as Dependências:**
    Com o ambiente virtual ativado, instale as bibliotecas necessárias:
    ```bash
    pip install -r requirements.txt
    ```
    O arquivo `requirements.txt` deve conter:
    ```
    ttkbootstrap
    pandas
    matplotlib
    ```

## Como Rodar a Aplicação

Após seguir os passos de configuração e instalação:

1.  **Ative seu ambiente virtual** (se ainda não estiver ativo).
2.  **Navegue até a pasta raiz do projeto** (onde o `main.py` está localizado).
3.  **Execute o arquivo principal:**
    ```bash
    python main.py
    ```
    Uma janela de login será exibida. Use `admin` como usuário e `admin` como senha para acessar.

## Estrutura de Dados

Os dados da aplicação são armazenados em arquivos locais para simplicidade:

* `data/lancamentos.csv`: Contém todos os registros de receitas e despesas.
* `data/*.json`: Arquivos JSON (`empresas.json`, `categorias.json`, etc.) armazenam os dados de lookup para os campos de seleção.

## Personalização (Opcional)

* **Alterar o Tema:** No arquivo `main.py`, você pode mudar o tema da aplicação alterando o parâmetro `themename` na linha `root = ttk.Window(themename="litera")`. Explore os temas disponíveis no `ttkbootstrap` (ex: "darkly", "superhero").
* **Ajustar Fontes:** No `main.py`, logo abaixo da definição do tema, você pode configurar o tamanho e estilo das fontes para os widgets usando `ttk.Style().configure()`. Por exemplo:
    ```python
    style = ttk.Style()
    style.configure('TLabel', font=('Segoe UI', 11, 'bold'))
    style.configure('TButton', font=('Segoe UI', 11, 'bold'))
    # ... e outros widgets
    ```
* **Cores do Resumo Financeiro:** As cores verde e vermelha para receitas, despesas e saldo são configuradas em `app/ui/app_principal.py` dentro do método `update_financial_summary`.

## Solução de Problemas Comuns

* **Erro de Formato de Data ao Iniciar (`ValueError: time data "XX/XX/XXXX" doesn't match format "%m/%d/%Y"`)**:
    Este erro ocorre quando o arquivo `lancamentos.csv` tem datas no formato `DD/MM/YYYY` e o `pandas` espera `MM/DD/YYYY`.
    **Solução:** No arquivo `app/core/data_manager.py`, na função `load_all_data`, altere a linha que converte a coluna 'Data' para datetime, adicionando `dayfirst=True`:
    ```python
    self.df_lancamentos['Data'] = pd.to_datetime(self.df_lancamentos['Data'], dayfirst=True)
    ```

* **Erro `AttributeError: 'AppPrincipal' object has no attribute 'reset_filters'`**:
    Isso indica que o método `reset_filters` está faltando na classe `AppPrincipal`.
    **Solução:** Adicione o método `reset_filters` à classe `AppPrincipal` em `app/ui/app_principal.py`, conforme as instruções fornecidas anteriormente.

* **Erro `AttributeError: 'DateEntry' object has no attribute 'set_date'`**:
    Este erro ocorre porque o `DateEntry` do `ttkbootstrap` não usa `set_date`.
    **Solução:** Em `app/ui/app_principal.py`, no método `reset_filters`, altere a forma como as datas são definidas para:
    ```python
    self.date_inicio.entry.delete(0, tk.END)
    self.date_inicio.entry.insert(0, data_inicio_str)
    # Faça o mesmo para self.date_fim
    ```