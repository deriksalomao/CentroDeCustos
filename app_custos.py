import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import pandas as pd
from datetime import datetime, timedelta
import os
import json
import random

# Tenta importar o matplotlib. Se não existir, informa o utilizador.
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_DISPONIVEL = True
except ImportError:
    MATPLOTLIB_DISPONIVEL = False

# Constantes para os nomes dos ficheiros de dados
LANCAMENTOS_FILE = 'lancamentos.csv'
EMPRESAS_DATA_FILE = 'empresas_data.json'
CATEGORIAS_FILE = 'categorias.json'
CONFIG_FILE = 'config.json' # Ficheiro para guardar as configurações da UI

class CentroCustoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão Financeira Multi-Empresa")
        self.root.geometry("1400x800")

        # --- Estrutura de Dados ---
        self.colunas = ["Data", "Empresa", "Centro de Custo", "Categoria", "Nome/Descrição", "Tipo", "Valor"]
        self.df_lancamentos = pd.DataFrame(columns=self.colunas)
        self.dados_empresas = {"Empresa Padrão": ["Geral"]}
        self.categorias = ["Geral"]

        # --- Variáveis de Estado da UI ---
        self.total_receitas_var = tk.StringVar(value="R$ 0.00")
        self.total_despesas_var = tk.StringVar(value="R$ 0.00")
        self.saldo_final_var = tk.StringVar(value="R$ 0.00")
        self.status_var = tk.StringVar(value="Pronto.")
        self.margem_lucro_var = tk.StringVar(value="0.00%")


        self.setup_styles()
        self.carregar_dados()
        self.criar_widgets()
        self.carregar_configuracoes() # Carrega as configs depois dos widgets serem criados
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar)

    def setup_styles(self):
        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", font=("Segoe UI", 10))
        style.configure("TCombobox", font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Danger.TButton", foreground="red", font=("Segoe UI", 10, "bold"))
        style.configure("Warning.TButton", foreground="#e67e22", font=("Segoe UI", 10, "bold"))
        style.configure("Success.TButton", foreground="green", font=("Segoe UI", 12, "bold"))
        style.configure("Info.TButton", foreground="blue", font=("Segoe UI", 12, "bold"))
        style.configure("Success.TLabel", font=("Segoe UI", 12, "bold"), foreground="green")
        style.configure("Error.TLabel", font=("Segoe UI", 12, "bold"), foreground="red")
        style.configure("Neutral.TLabel", font=("Segoe UI", 12, "bold"), foreground="black")
        style.configure("Status.TLabel", font=("Segoe UI", 9))

    def carregar_dados(self):
        # Carregar dados de empresas e centros de custo
        if os.path.exists(EMPRESAS_DATA_FILE):
            try:
                with open(EMPRESAS_DATA_FILE, 'r') as f:
                    self.dados_empresas = json.load(f)
                    if not self.dados_empresas:
                        self.dados_empresas = {"Empresa Padrão": ["Geral"]}
            except (json.JSONDecodeError, FileNotFoundError):
                self.dados_empresas = {"Empresa Padrão": ["Geral"]}
        
        # Carregar categorias
        if os.path.exists(CATEGORIAS_FILE):
            try:
                with open(CATEGORIAS_FILE, 'r') as f: 
                    self.categorias = json.load(f)
                    if not self.categorias: self.categorias = ["Geral"]
                    if "Geral" not in self.categorias: self.categorias.insert(0, "Geral")
            except (json.JSONDecodeError, FileNotFoundError):
                self.categorias = ["Geral"]

        # Carregar o DataFrame de lançamentos
        if os.path.exists(LANCAMENTOS_FILE):
            try:
                df_temp = pd.read_csv(LANCAMENTOS_FILE)
                if all(coluna in df_temp.columns for coluna in self.colunas):
                    self.df_lancamentos = df_temp
                    self.df_lancamentos['Data'] = pd.to_datetime(self.df_lancamentos['Data'])
                else:
                    messagebox.showwarning("Ficheiro Antigo Detetado", "Ficheiro 'lancamentos.csv' incompatível.\nUm novo ficheiro será criado.")
                    self.df_lancamentos = pd.DataFrame(columns=self.colunas)
            except Exception as e:
                messagebox.showerror("Erro ao Carregar Lançamentos", f"Não foi possível carregar: {e}")
                self.df_lancamentos = pd.DataFrame(columns=self.colunas)
    
    def salvar_dados(self):
        """Salva apenas os dados financeiros (lançamentos, empresas, categorias)."""
        try:
            self.df_lancamentos.to_csv(LANCAMENTOS_FILE, index=False)
            with open(EMPRESAS_DATA_FILE, 'w') as f: json.dump(self.dados_empresas, f, indent=4)
            with open(CATEGORIAS_FILE, 'w') as f: json.dump(self.categorias, f, indent=4)
            self.set_status("Dados guardados com sucesso!")
        except Exception as e:
            self.set_status(f"Erro ao guardar dados: {e}")
            messagebox.showerror("Erro ao Guardar", f"Não foi possível guardar os dados no ficheiro.\nErro: {e}")

    def salvar_configuracoes(self):
        """Salva as configurações da interface (ex: filtros de data)."""
        try:
            configs = {
                'data_inicio': self.date_inicio.get_date().strftime('%Y-%m-%d'),
                'data_fim': self.date_fim.get_date().strftime('%Y-%m-%d'),
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(configs, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}") 

    def carregar_configuracoes(self):
        """Carrega e aplica as configurações da interface."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    configs = json.load(f)
                
                if 'data_inicio' in configs:
                    self.date_inicio.set_date(datetime.strptime(configs['data_inicio'], '%Y-%m-%d'))
                if 'data_fim' in configs:
                    self.date_fim.set_date(datetime.strptime(configs['data_fim'], '%Y-%m-%d'))

                self.atualizar_relatorio()
            except Exception as e:
                print(f"Erro ao carregar configurações: {e}")

    def ao_fechar(self):
        """Salva tudo (dados e configurações) antes de fechar."""
        self.salvar_dados()
        self.salvar_configuracoes()
        self.root.destroy()

    def set_status(self, message):
        self.status_var.set(message)
        self.root.after(5000, lambda: self.status_var.set("Pronto."))

    def criar_widgets(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        left_panel = ttk.Frame(main_container, width=450)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        left_panel.pack_propagate(False)
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, style="Status.TLabel")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.criar_painel_esquerdo(left_panel)
        self.criar_painel_direito(right_panel)
        self.atualizar_contexto_empresa()

    def criar_painel_esquerdo(self, parent):
        frame_acoes_principais = ttk.Frame(parent)
        frame_acoes_principais.pack(fill='x', padx=5, pady=(0, 10))
        frame_acoes_principais.columnconfigure(0, weight=1)
        frame_acoes_principais.columnconfigure(1, weight=1)
        btn_abrir_graficos = ttk.Button(frame_acoes_principais, text="Análise Gráfica", command=self.abrir_janela_graficos, style="Info.TButton")
        btn_abrir_graficos.grid(row=0, column=0, columnspan=2, sticky='ew')

        frame_empresas = ttk.LabelFrame(parent, text="Gestão de Empresas", padding=(10, 5))
        frame_empresas.pack(fill="x", padx=5, pady=5, side=tk.TOP)
        frame_empresas.columnconfigure(1, weight=1)
        ttk.Label(frame_empresas, text="Empresa Ativa:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_empresa_ativa = ttk.Combobox(frame_empresas, values=list(self.dados_empresas.keys()), state="readonly")
        self.combo_empresa_ativa.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.combo_empresa_ativa.set(list(self.dados_empresas.keys())[0])
        self.combo_empresa_ativa.bind("<<ComboboxSelected>>", self.atualizar_contexto_empresa)
        self.btn_excluir_empresa = ttk.Button(frame_empresas, text="Excluir", command=self.excluir_empresa_ativa, style="Danger.TButton", width=8)
        self.btn_excluir_empresa.grid(row=0, column=2, padx=(5,0))
        ttk.Label(frame_empresas, text="Nova Empresa:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_nova_empresa = ttk.Entry(frame_empresas)
        self.entry_nova_empresa.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        btn_add_empresa = ttk.Button(frame_empresas, text="Adicionar", command=self.adicionar_empresa, width=8)
        btn_add_empresa.grid(row=1, column=2, padx=5, pady=5)

        frame_categorias = ttk.LabelFrame(parent, text="Gestão de Categorias", padding=(10, 5))
        frame_categorias.pack(fill="x", padx=5, pady=5, side=tk.TOP)
        frame_categorias.columnconfigure(1, weight=1)
        ttk.Label(frame_categorias, text="Selecionar Categoria:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_excluir_categoria = ttk.Combobox(frame_categorias, state="readonly")
        self.combo_excluir_categoria.grid(row=0, column=1, sticky="ew", padx=5)
        self.btn_excluir_categoria = ttk.Button(frame_categorias, text="Excluir", command=self.excluir_categoria, style="Danger.TButton", width=8)
        self.btn_excluir_categoria.grid(row=0, column=2, padx=5)
        ttk.Label(frame_categorias, text="Nova Categoria:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_nova_categoria = ttk.Entry(frame_categorias)
        self.entry_nova_categoria.grid(row=1, column=1, sticky="ew", padx=5)
        btn_add_categoria = ttk.Button(frame_categorias, text="Adicionar", command=self.adicionar_categoria, width=8)
        btn_add_categoria.grid(row=1, column=2, padx=5)

        frame_add_cc = ttk.LabelFrame(parent, text="Gestão de Centros de Custo", padding=(10, 5))
        frame_add_cc.pack(fill="x", padx=5, pady=5, side=tk.TOP)
        frame_add_cc.columnconfigure(1, weight=1)
        ttk.Label(frame_add_cc, text="Novo Centro de Custo:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_novo_cc = ttk.Entry(frame_add_cc)
        self.entry_novo_cc.grid(row=0, column=1, sticky="ew", padx=5)
        btn_add_cc = ttk.Button(frame_add_cc, text="Adicionar", command=self.adicionar_centro_custo, width=8)
        btn_add_cc.grid(row=0, column=2, padx=5)

        btn_abrir_popup_lancamento = ttk.Button(parent, text="Adicionar Novo Lançamento", 
                                                command=self.abrir_janela_novo_lancamento, style="Success.TButton")
        btn_abrir_popup_lancamento.pack(fill='x', padx=5, pady=20, ipady=10, side=tk.TOP)

        frame_acoes_globais = ttk.Frame(parent)
        frame_acoes_globais.pack(fill='x', padx=5, pady=(10, 5), side=tk.BOTTOM)
        btn_salvar = ttk.Button(frame_acoes_globais, text="Salvar Alterações", command=self.salvar_dados)
        btn_salvar.pack(fill='x')
        
        frame_resumo = ttk.LabelFrame(parent, text="Resumo Financeiro (Filtro Aplicado)", padding=(10, 10))
        frame_resumo.pack(fill="x", padx=5, pady=5, side=tk.BOTTOM)
        ttk.Label(frame_resumo, text="Total de Receitas:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5)
        ttk.Label(frame_resumo, textvariable=self.total_receitas_var, font=("Segoe UI", 10), foreground="blue").grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(frame_resumo, text="Total de Despesas:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", padx=5)
        ttk.Label(frame_resumo, textvariable=self.total_despesas_var, font=("Segoe UI", 10), foreground="orange").grid(row=1, column=1, sticky="w", padx=5)
        ttk.Label(frame_resumo, text="Saldo Final:", font=("Segoe UI", 12, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=(10,0))
        self.label_saldo = ttk.Label(frame_resumo, textvariable=self.saldo_final_var)
        self.label_saldo.grid(row=2, column=1, sticky="w", padx=5, pady=(10,0))
        ttk.Label(frame_resumo, text="Margem de Lucro:", font=("Segoe UI", 12, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=(5,0))
        self.label_margem = ttk.Label(frame_resumo, textvariable=self.margem_lucro_var)
        self.label_margem.grid(row=3, column=1, sticky="w", padx=5, pady=(5,0))
        
        frame_ferramentas = ttk.LabelFrame(parent, text="Ferramentas de Teste", padding=(10, 5))
        frame_ferramentas.pack(fill="x", padx=5, pady=15, side=tk.BOTTOM)
        btn_gerar_dados = ttk.Button(frame_ferramentas, text="Gerar Dados de Teste", command=self.gerar_dados_teste)
        btn_gerar_dados.pack(fill='x')

        self.atualizar_combobox_categorias()
        
    def criar_painel_direito(self, parent):
        frame_relatorio = ttk.LabelFrame(parent, text="Registro de Lançamentos", padding=(10, 5))
        frame_relatorio.pack(fill="both", expand=True)

        frame_filtros_container = ttk.Frame(frame_relatorio, padding=(0, 5))
        frame_filtros_container.pack(fill='x')

        frame_filtros_linha1 = ttk.Frame(frame_filtros_container)
        frame_filtros_linha1.pack(fill='x', pady=(0, 5))
        ttk.Label(frame_filtros_linha1, text="De:").pack(side='left', padx=(0, 5))
        self.date_inicio = DateEntry(frame_filtros_linha1, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.date_inicio.pack(side='left')
        ttk.Label(frame_filtros_linha1, text="Até:").pack(side='left', padx=(10, 5))
        self.date_fim = DateEntry(frame_filtros_linha1, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.date_fim.pack(side='left')
        ttk.Label(frame_filtros_linha1, text="Pesquisar Descrição:").pack(side='left', padx=(10, 5))
        self.entry_pesquisa = ttk.Entry(frame_filtros_linha1)
        self.entry_pesquisa.pack(side='left', fill='x', expand=True, padx=5)
        self.entry_pesquisa.bind("<KeyRelease>", lambda e: self.atualizar_relatorio())

        frame_filtros_linha2 = ttk.Frame(frame_filtros_container)
        frame_filtros_linha2.pack(fill='x')
        
        ttk.Label(frame_filtros_linha2, text="Centro de Custo:").pack(side='left', padx=(0, 5))
        self.combo_filtro_cc = ttk.Combobox(frame_filtros_linha2, state="readonly")
        self.combo_filtro_cc.pack(side='left', padx=(0,10), fill='x', expand=True)
        self.combo_filtro_cc.bind("<<ComboboxSelected>>", lambda e: self.atualizar_relatorio())

        ttk.Label(frame_filtros_linha2, text="Categoria:").pack(side='left', padx=(0, 5))
        self.combo_filtro_categoria = ttk.Combobox(frame_filtros_linha2, state="readonly")
        self.combo_filtro_categoria.pack(side='left', padx=(0,10), fill='x', expand=True)
        self.combo_filtro_categoria.bind("<<ComboboxSelected>>", lambda e: self.atualizar_relatorio())

        ttk.Label(frame_filtros_linha2, text="Tipo:").pack(side='left', padx=(0, 5))
        self.combo_filtro_tipo = ttk.Combobox(frame_filtros_linha2, values=["Todos", "Receita", "Despesa"], state="readonly")
        self.combo_filtro_tipo.pack(side='left', padx=(0,10))
        self.combo_filtro_tipo.set("Todos")
        self.combo_filtro_tipo.bind("<<ComboboxSelected>>", lambda e: self.atualizar_relatorio())

        btn_filtrar = ttk.Button(frame_filtros_linha2, text="Filtrar", command=self.atualizar_relatorio, width=8)
        btn_filtrar.pack(side='left', padx=5)

        tree_container = ttk.Frame(frame_relatorio)
        tree_container.pack(fill='both', expand=True, pady=(5,0))
        colunas_relatorio = ("data", "empresa", "centro_custo", "categoria", "descricao", "tipo", "valor")
        self.tree_relatorio = ttk.Treeview(tree_container, columns=colunas_relatorio, show="headings")
        self.tree_relatorio.bind("<Double-1>", self.abrir_janela_edicao)
        scrollbar_y = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree_relatorio.yview)
        scrollbar_x = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree_relatorio.xview)
        self.tree_relatorio.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_relatorio.pack(side=tk.LEFT, fill="both", expand=True)
        self.tree_relatorio.heading("data", text="Data")
        self.tree_relatorio.heading("empresa", text="Empresa")
        self.tree_relatorio.heading("centro_custo", text="Centro de Custo")
        self.tree_relatorio.heading("categoria", text="Categoria")
        self.tree_relatorio.heading("descricao", text="Nome/Descrição")
        self.tree_relatorio.heading("tipo", text="Tipo")
        self.tree_relatorio.heading("valor", text="Valor (R$)")
        self.tree_relatorio.column("data", width=130, anchor="w")
        self.tree_relatorio.column("empresa", width=120, anchor="w")
        self.tree_relatorio.column("centro_custo", width=150, anchor="w")
        self.tree_relatorio.column("categoria", width=120, anchor="w")
        self.tree_relatorio.column("descricao", width=250, anchor="w")
        self.tree_relatorio.column("tipo", width=80, anchor="center")
        self.tree_relatorio.column("valor", width=100, anchor="e")
        frame_botoes = ttk.Frame(frame_relatorio)
        frame_botoes.pack(side="bottom", pady=5, fill="x")
        btn_exportar = ttk.Button(frame_botoes, text="Exportar para Excel", command=self.exportar_para_excel)
        btn_exportar.pack(side="left", padx=5)
        
        btn_limpar_empresa = ttk.Button(frame_botoes, text="Limpar Lançamentos da Empresa", command=self.limpar_lancamentos_empresa, style="Danger.TButton")
        btn_limpar_empresa.pack(side="right", padx=5)
        
        btn_excluir_cc = ttk.Button(frame_botoes, text="Excluir Lançamento", command=self.excluir_lancamento_selecionado, style="Danger.TButton")
        btn_excluir_cc.pack(side="right", padx=5)
        
    def atualizar_contexto_empresa(self, event=None):
        empresa_ativa = self.combo_empresa_ativa.get()
        if empresa_ativa:
            if empresa_ativa == "Empresa Padrão":
                self.btn_excluir_empresa.configure(state=tk.DISABLED)
            else:
                self.btn_excluir_empresa.configure(state=tk.NORMAL)
            
            centros_custo_empresa = ["Todos"] + self.dados_empresas.get(empresa_ativa, [])
            self.combo_filtro_cc['values'] = centros_custo_empresa
            self.combo_filtro_cc.set("Todos")

            categorias_disponiveis = ["Todos"] + self.categorias
            self.combo_filtro_categoria['values'] = categorias_disponiveis
            self.combo_filtro_categoria.set("Todos")

            self.atualizar_relatorio()

    def adicionar_empresa(self):
        nova_empresa = self.entry_nova_empresa.get().strip().title()
        if not nova_empresa: return
        if nova_empresa in self.dados_empresas: messagebox.showinfo("Informação", f"A empresa '{nova_empresa}' já existe.")
        else:
            self.dados_empresas[nova_empresa] = ["Geral"]
            self.combo_empresa_ativa['values'] = list(self.dados_empresas.keys())
            self.combo_empresa_ativa.set(nova_empresa)
            self.entry_nova_empresa.delete(0, tk.END)
            self.atualizar_contexto_empresa()
            self.set_status(f"Empresa '{nova_empresa}' adicionada.")

    def excluir_empresa_ativa(self):
        empresa_a_excluir = self.combo_empresa_ativa.get()
        if empresa_a_excluir == "Empresa Padrão":
            return

        if messagebox.askyesno("Confirmar Exclusão", f"Excluir a empresa '{empresa_a_excluir}' e TODOS os seus dados?"):
            del self.dados_empresas[empresa_a_excluir]
            self.df_lancamentos = self.df_lancamentos[self.df_lancamentos['Empresa'] != empresa_a_excluir].reset_index(drop=True)
            self.combo_empresa_ativa['values'] = list(self.dados_empresas.keys())
            self.combo_empresa_ativa.set("Empresa Padrão")
            self.atualizar_contexto_empresa()
            self.set_status(f"Empresa '{empresa_a_excluir}' excluída.")

    def adicionar_centro_custo(self):
        empresa_ativa = self.combo_empresa_ativa.get()
        if not empresa_ativa: return
        novo_cc = self.entry_novo_cc.get().strip().title()
        if not novo_cc: return
        if novo_cc in self.dados_empresas[empresa_ativa]: messagebox.showinfo("Informação", "Centro de custo já existe.")
        else:
            self.dados_empresas[empresa_ativa].append(novo_cc)
            self.atualizar_contexto_empresa()
            self.set_status(f"Centro de custo '{novo_cc}' adicionado.")

    def adicionar_categoria(self):
        nova_categoria = self.entry_nova_categoria.get().strip().title()
        if not nova_categoria: return
        if nova_categoria in self.categorias: messagebox.showinfo("Informação", "Categoria já existe.")
        else:
            self.categorias.append(nova_categoria)
            self.atualizar_combobox_categorias()
            categorias_disponiveis = ["Todos"] + self.categorias
            self.combo_filtro_categoria['values'] = categorias_disponiveis
            self.set_status(f"Categoria '{nova_categoria}' adicionada.")

    def excluir_categoria(self):
        categoria_a_excluir = self.combo_excluir_categoria.get()
        if not categoria_a_excluir:
            messagebox.showwarning("Atenção", "Nenhuma categoria selecionada para exclusão.")
            return
        if categoria_a_excluir == "Geral":
            messagebox.showerror("Ação Proibida", "A categoria 'Geral' não pode ser excluída.")
            return
        if messagebox.askyesno("Confirmar Exclusão", f"Excluir a categoria '{categoria_a_excluir}'?\nLançamentos com esta categoria serão movidos para 'Geral'."):
            self.df_lancamentos.loc[self.df_lancamentos['Categoria'] == categoria_a_excluir, 'Categoria'] = 'Geral'
            self.categorias.remove(categoria_a_excluir)
            self.atualizar_combobox_categorias()
            categorias_disponiveis = ["Todos"] + self.categorias
            self.combo_filtro_categoria['values'] = categorias_disponiveis
            self.combo_filtro_categoria.set("Todos")
            self.atualizar_relatorio()
            self.set_status(f"Categoria '{categoria_a_excluir}' excluída.")

    def atualizar_combobox_categorias(self):
        categorias_excluiveis = [cat for cat in self.categorias if cat != "Geral"]
        self.combo_excluir_categoria['values'] = categorias_excluiveis
        if categorias_excluiveis:
            self.combo_excluir_categoria.set(categorias_excluiveis[0])
        else:
            self.combo_excluir_categoria.set('')

    def _adicionar_lancamento_logica(self, empresa, cc, categoria, descricao, tipo, valor):
        novo_lancamento = pd.DataFrame([[datetime.now(), empresa, cc, categoria, descricao, tipo, valor]], columns=self.colunas)
        self.df_lancamentos = pd.concat([self.df_lancamentos, novo_lancamento], ignore_index=True)
        self.atualizar_relatorio()
        self.set_status("Lançamento adicionado com sucesso.")

    def abrir_janela_novo_lancamento(self):
        empresa_ativa = self.combo_empresa_ativa.get()
        if not empresa_ativa:
            messagebox.showwarning("Atenção", "Selecione uma empresa ativa para fazer um lançamento.")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Adicionar Novo Lançamento")
        popup_width, popup_height = 450, 250
        pos_x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup_width // 2)
        pos_y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup_height // 2)
        popup.geometry(f"{popup_width}x{popup_height}+{pos_x}+{pos_y}")
        popup.transient(self.root)
        popup.grab_set()

        frame = ttk.Frame(popup, padding=15)
        frame.pack(fill='both', expand=True)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Centro de Custo:").grid(row=0, column=0, sticky='w', pady=5)
        combo_cc_popup = ttk.Combobox(frame, values=self.dados_empresas[empresa_ativa], state='readonly')
        combo_cc_popup.grid(row=0, column=1, sticky='ew', pady=5)
        if self.dados_empresas[empresa_ativa]: combo_cc_popup.set(self.dados_empresas[empresa_ativa][0])
        ttk.Label(frame, text="Categoria:").grid(row=1, column=0, sticky='w', pady=5)
        combo_cat_popup = ttk.Combobox(frame, values=self.categorias, state='readonly')
        combo_cat_popup.grid(row=1, column=1, sticky='ew', pady=5)
        combo_cat_popup.set("Geral")
        ttk.Label(frame, text="Nome/Descrição:").grid(row=2, column=0, sticky='w', pady=5)
        entry_desc_popup = ttk.Entry(frame)
        entry_desc_popup.grid(row=2, column=1, sticky='ew', pady=5)
        entry_desc_popup.focus_set()
        ttk.Label(frame, text="Tipo:").grid(row=3, column=0, sticky='w', pady=5)
        combo_tipo_popup = ttk.Combobox(frame, values=["Receita", "Despesa"], state='readonly')
        combo_tipo_popup.grid(row=3, column=1, sticky='ew', pady=5)
        combo_tipo_popup.set("Despesa")
        ttk.Label(frame, text="Valor (R$):").grid(row=4, column=0, sticky='w', pady=5)
        entry_valor_popup = ttk.Entry(frame)
        entry_valor_popup.grid(row=4, column=1, sticky='ew', pady=5)

        def salvar_novo_lancamento():
            try:
                valor = float(entry_valor_popup.get().strip().replace(",", "."))
                if valor <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Erro de Validação", "O valor deve ser um número positivo.", parent=popup)
                return
            
            self._adicionar_lancamento_logica(empresa_ativa, combo_cc_popup.get(), combo_cat_popup.get(), entry_desc_popup.get().strip(), combo_tipo_popup.get(), valor)
            popup.destroy()

        btn_salvar_popup = ttk.Button(frame, text="Adicionar Lançamento", command=salvar_novo_lancamento)
        btn_salvar_popup.grid(row=5, column=0, columnspan=2, pady=15)

    def excluir_lancamento_selecionado(self):
        if not self.tree_relatorio.focus(): messagebox.showwarning("Atenção", "Nenhum lançamento selecionado.")
        elif messagebox.askyesno("Confirmar", "Excluir o lançamento selecionado?"):
            index_para_excluir = int(self.tree_relatorio.focus())
            self.df_lancamentos.drop(index_para_excluir, inplace=True)
            self.df_lancamentos.reset_index(drop=True, inplace=True)
            self.atualizar_relatorio()
            self.set_status("Lançamento excluído.")

    def limpar_lancamentos_empresa(self):
        """Apaga todos os lançamentos APENAS da empresa ativa no momento."""
        empresa_ativa = self.combo_empresa_ativa.get()
        if not empresa_ativa:
            messagebox.showwarning("Ação Inválida", "Nenhuma empresa selecionada.", parent=self.root)
            return

        if messagebox.askyesno(
            "Confirmar Limpeza de Lançamentos", 
            f"Tem a certeza de que deseja apagar TODOS os lançamentos da empresa '{empresa_ativa}'?\n\nEsta ação não pode ser desfeita.",
            parent=self.root
        ):
            self.df_lancamentos = self.df_lancamentos[self.df_lancamentos['Empresa'] != empresa_ativa].reset_index(drop=True)
            self.atualizar_relatorio()
            self.set_status(f"Lançamentos da empresa '{empresa_ativa}' foram apagados.")
    
    def _get_filtered_data(self):
        empresa_ativa = self.combo_empresa_ativa.get()
        if not empresa_ativa or self.df_lancamentos.empty:
            return pd.DataFrame(columns=self.colunas)
        
        df_filtrado = self.df_lancamentos[self.df_lancamentos['Empresa'] == empresa_ativa].copy()
        
        start_date = pd.to_datetime(self.date_inicio.get_date())
        end_date = pd.to_datetime(self.date_fim.get_date()).replace(hour=23, minute=59, second=59)
        df_filtrado = df_filtrado[(df_filtrado['Data'] >= start_date) & (df_filtrado['Data'] <= end_date)]
        
        termo_pesquisa = self.entry_pesquisa.get().strip().lower()
        if termo_pesquisa:
            df_filtrado = df_filtrado[df_filtrado['Nome/Descrição'].str.lower().str.contains(termo_pesquisa)]
        
        filtro_cc = self.combo_filtro_cc.get()
        if filtro_cc and filtro_cc != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Centro de Custo'] == filtro_cc]

        filtro_cat = self.combo_filtro_categoria.get()
        if filtro_cat and filtro_cat != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Categoria'] == filtro_cat]

        filtro_tipo = self.combo_filtro_tipo.get()
        if filtro_tipo and filtro_tipo != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Tipo'] == filtro_tipo]

        return df_filtrado

    def atualizar_relatorio(self):
        for i in self.tree_relatorio.get_children(): self.tree_relatorio.delete(i)
        df_filtrado = self._get_filtered_data()
        if df_filtrado.empty and not self.combo_empresa_ativa.get():
             self.atualizar_resumo(pd.DataFrame())
             return
        df_ordenado = df_filtrado.sort_values(by="Data", ascending=False)
        for index, row in df_ordenado.iterrows():
            self.tree_relatorio.insert("", "end", iid=index, values=(
                row["Data"].strftime("%Y-%m-%d %H:%M"), row["Empresa"], row["Centro de Custo"], row["Categoria"],
                row["Nome/Descrição"], row["Tipo"], f"{row['Valor']:.2f}"
            ))
        self.atualizar_resumo(df_filtrado)

    def atualizar_resumo(self, df):
        if df.empty:
            total_receitas, total_despesas, saldo_final, margem_lucro = 0, 0, 0, 0
        else:
            total_receitas = df[df['Tipo'] == 'Receita']['Valor'].sum()
            total_despesas = df[df['Tipo'] == 'Despesa']['Valor'].sum()
            saldo_final = total_receitas - total_despesas
            margem_lucro = (saldo_final / total_receitas) * 100 if total_receitas > 0 else 0
        
        self.total_receitas_var.set(f"R$ {total_receitas:,.2f}")
        self.total_despesas_var.set(f"R$ {total_despesas:,.2f}")
        self.saldo_final_var.set(f"R$ {saldo_final:,.2f}")
        self.margem_lucro_var.set(f"{margem_lucro:.2f}%")
        
        if saldo_final > 0:
            self.label_saldo.configure(style="Success.TLabel")
            self.label_margem.configure(style="Success.TLabel")
        elif saldo_final < 0:
            self.label_saldo.configure(style="Error.TLabel")
            self.label_margem.configure(style="Error.TLabel")
        else:
            self.label_saldo.configure(style="Neutral.TLabel")
            self.label_margem.configure(style="Neutral.TLabel")

    def abrir_janela_edicao(self, event):
        if not self.tree_relatorio.focus(): return
        index_edicao = int(self.tree_relatorio.focus())
        dados_lancamento = self.df_lancamentos.loc[index_edicao]
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Lançamento")
        popup_width, popup_height = 400, 300
        pos_x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup_width // 2)
        pos_y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup_height // 2)
        edit_window.geometry(f"{popup_width}x{popup_height}+{pos_x}+{pos_y}")
        edit_window.transient(self.root)
        edit_window.grab_set()

        frame = ttk.Frame(edit_window, padding=10)
        frame.pack(fill='both', expand=True)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Centro de Custo:").grid(row=0, column=0, sticky='w', pady=5)
        combo_cc_edit = ttk.Combobox(frame, values=self.dados_empresas[dados_lancamento['Empresa']], state='readonly')
        combo_cc_edit.set(dados_lancamento['Centro de Custo'])
        combo_cc_edit.grid(row=0, column=1, sticky='ew', pady=5)
        ttk.Label(frame, text="Categoria:").grid(row=1, column=0, sticky='w', pady=5)
        combo_cat_edit = ttk.Combobox(frame, values=self.categorias, state='readonly')
        combo_cat_edit.set(dados_lancamento['Categoria'])
        combo_cat_edit.grid(row=1, column=1, sticky='ew', pady=5)
        ttk.Label(frame, text="Nome/Descrição:").grid(row=2, column=0, sticky='w', pady=5)
        entry_desc_edit = ttk.Entry(frame)
        entry_desc_edit.insert(0, dados_lancamento['Nome/Descrição'])
        entry_desc_edit.grid(row=2, column=1, sticky='ew', pady=5)
        ttk.Label(frame, text="Tipo:").grid(row=3, column=0, sticky='w', pady=5)
        combo_tipo_edit = ttk.Combobox(frame, values=["Receita", "Despesa"], state='readonly')
        combo_tipo_edit.set(dados_lancamento['Tipo'])
        combo_tipo_edit.grid(row=3, column=1, sticky='ew', pady=5)
        ttk.Label(frame, text="Valor (R$):").grid(row=4, column=0, sticky='w', pady=5)
        entry_valor_edit = ttk.Entry(frame)
        entry_valor_edit.insert(0, f"{dados_lancamento['Valor']:.2f}")
        entry_valor_edit.grid(row=4, column=1, sticky='ew', pady=5)

        def salvar_edicao():
            try:
                novo_valor = float(entry_valor_edit.get().replace(",", "."))
                if novo_valor <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido.", parent=edit_window)
                return
            self.df_lancamentos.loc[index_edicao, 'Centro de Custo'] = combo_cc_edit.get()
            self.df_lancamentos.loc[index_edicao, 'Categoria'] = combo_cat_edit.get()
            self.df_lancamentos.loc[index_edicao, 'Nome/Descrição'] = entry_desc_edit.get()
            self.df_lancamentos.loc[index_edicao, 'Tipo'] = combo_tipo_edit.get()
            self.df_lancamentos.loc[index_edicao, 'Valor'] = novo_valor
            self.atualizar_relatorio()
            self.set_status("Lançamento editado com sucesso.")
            edit_window.destroy()

        btn_salvar = ttk.Button(frame, text="Salvar Alterações", command=salvar_edicao)
        btn_salvar.grid(row=5, column=0, columnspan=2, pady=10)

    def exportar_para_excel(self):
        df_filtrado = self._get_filtered_data()
        if df_filtrado.empty:
            messagebox.showinfo("Informação", "Não há dados (com os filtros atuais) para exportar.")
            return
        caminho_ficheiro = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Ficheiros Excel", "*.xlsx"), ("Todos os ficheiros", "*.*")],
            title="Guardar Relatório como...",
            initialfile=f"Relatorio_{self.combo_empresa_ativa.get().replace(' ', '_')}_{datetime.now():%Y-%m-%d}.xlsx"
        )
        if not caminho_ficheiro: return
        try:
            df_filtrado.to_excel(caminho_ficheiro, index=False, engine='openpyxl')
            self.set_status("Relatório exportado com sucesso.")
            messagebox.showinfo("Sucesso", f"Relatório exportado com sucesso para:\n{caminho_ficheiro}")
        except Exception as e:
            self.set_status(f"Erro ao exportar: {e}")
            messagebox.showerror("Erro de Exportação", f"Não foi possível exportar o ficheiro.\nErro: {e}")

    def abrir_janela_graficos(self):
        if not MATPLOTLIB_DISPONIVEL:
            messagebox.showerror("Biblioteca em Falta", "A biblioteca 'matplotlib' é necessária para a análise gráfica.\nPor favor, instale-a com o comando:\n\npip install matplotlib")
            return

        df_filtrado = self._get_filtered_data()
        if df_filtrado.empty:
            messagebox.showinfo("Sem Dados", "Não há dados para gerar gráficos com os filtros atuais.")
            return

        graficos_window = tk.Toplevel(self.root)
        graficos_window.title(f"Análise Gráfica - {self.combo_empresa_ativa.get()}")
        graficos_window.geometry("1000x700")
        graficos_window.transient(self.root)
        graficos_window.grab_set()

        notebook = ttk.Notebook(graficos_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text='Despesas por Grupo')
        self._criar_grafico_pizza(tab1, df_filtrado)
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text='Receita vs. Despesa Mensal')
        self._criar_grafico_barras(tab2, df_filtrado)
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text='Evolução do Saldo')
        self._criar_grafico_linha(tab3, df_filtrado)

    def _criar_grafico_pizza(self, parent, df):
        frame_controles = ttk.Frame(parent)
        frame_controles.pack(fill='x', pady=5)
        ttk.Label(frame_controles, text="Agrupar por:").pack(side='left', padx=5)
        combo_grupo = ttk.Combobox(frame_controles, values=["Categoria", "Centro de Custo"], state='readonly')
        combo_grupo.pack(side='left', padx=5)
        combo_grupo.set("Categoria")
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill='both', expand=True)
        
        def atualizar_grafico_pizza():
            for widget in canvas_frame.winfo_children(): widget.destroy()
            grupo_selecionado = combo_grupo.get()
            dados_despesas = df[df['Tipo'] == 'Despesa'].groupby(grupo_selecionado)['Valor'].sum()
            if dados_despesas.empty:
                ttk.Label(canvas_frame, text="Não há despesas para exibir.").pack(pady=20)
                return
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.pie(dados_despesas, labels=dados_despesas.index, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
            ax.set_title(f"Distribuição de Despesas por {grupo_selecionado}")
            centre_circle = plt.Circle((0,0),0.70,fc='white')
            fig.gca().add_artist(centre_circle)
            ax.axis('equal')  
            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)

        combo_grupo.bind("<<ComboboxSelected>>", lambda e: atualizar_grafico_pizza())
        atualizar_grafico_pizza()

    def _criar_grafico_barras(self, parent, df):
        df_plot = df.copy()
        df_plot['Mês'] = df_plot['Data'].dt.to_period('M')
        dados_agrupados = df_plot.groupby(['Mês', 'Tipo'])['Valor'].sum().unstack(fill_value=0)
        
        fig, ax = plt.subplots(figsize=(10, 6))

        color_map = {'Despesa': 'red', 'Receita': 'green'}
        
        colunas_ordenadas = []
        if 'Despesa' in dados_agrupados.columns:
            colunas_ordenadas.append('Despesa')
        if 'Receita' in dados_agrupados.columns:
            colunas_ordenadas.append('Receita')

        if colunas_ordenadas:
            dados_agrupados[colunas_ordenadas].plot(
                kind='bar', 
                ax=ax, 
                color=[color_map[col] for col in colunas_ordenadas]
            )

        ax.set_title("Receitas vs. Despesas Mensais")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Valor (R$)")
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _criar_grafico_linha(self, parent, df):
        df_plot = df.copy().sort_values(by="Data")
        df_plot['Movimento'] = df_plot.apply(lambda row: row['Valor'] if row['Tipo'] == 'Receita' else -row['Valor'], axis=1)
        df_plot['Saldo Acumulado'] = df_plot['Movimento'].cumsum()
        fig, ax = plt.subplots(figsize=(10, 6))
        df_plot.plot(kind='line', x='Data', y='Saldo Acumulado', ax=ax, legend=None, marker='o', linestyle='-')
        ax.set_title("Evolução do Saldo Acumulado")
        ax.set_xlabel("Data")
        ax.set_ylabel("Saldo (R$)")
        ax.grid(True, linestyle='--', alpha=0.7)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def gerar_dados_teste(self):
        if not messagebox.askyesno("Confirmar", "Isto irá apagar todos os dados atuais e gerar um novo conjunto de dados de teste. Deseja continuar?"):
            return

        self.df_lancamentos = pd.DataFrame(columns=self.colunas)
        
        self.dados_empresas = {
            "Tecnologia BR": ["Desenvolvimento", "Marketing Digital", "Infraestrutura"],
            "Varejo SP": ["Loja Centro", "Logística", "Administrativo"]
        }
        self.categorias = ["Software", "Hardware", "Publicidade", "Salários", "Fornecedores", "Vendas de Produtos", "Serviços", "Geral"]

        lancamentos = []
        hoje = datetime.now()
        data_mais_antiga = hoje - timedelta(days=365)
        
        for i in range(150):
            empresa = random.choice(list(self.dados_empresas.keys()))
            centro_custo = random.choice(self.dados_empresas[empresa])
            categoria = random.choice(self.categorias)
            tipo = random.choices(["Receita", "Despesa"], weights=[0.3, 0.7], k=1)[0]
            data = hoje - timedelta(days=random.randint(0, 365))
            
            if tipo == "Receita":
                descricao = f"Venda {random.choice(['Produto X', 'Serviço Y', 'Contrato Z'])} #{random.randint(100,999)}"
                valor = random.uniform(500, 15000)
            else:
                descricao = f"Pagamento {random.choice(['Fornecedor A', 'Software B', 'Aluguel C'])}"
                valor = random.uniform(100, 8000)

            lancamentos.append([data, empresa, centro_custo, categoria, descricao, tipo, valor])

        self.df_lancamentos = pd.DataFrame(lancamentos, columns=self.colunas)

        self.combo_empresa_ativa['values'] = list(self.dados_empresas.keys())
        self.combo_empresa_ativa.set(list(self.dados_empresas.keys())[0])
        self.date_inicio.set_date(data_mais_antiga)
        self.date_fim.set_date(hoje)
        self.atualizar_contexto_empresa()
        self.atualizar_combobox_categorias()
        
        self.salvar_dados() 
        self.set_status("Dados de teste gerados e guardados com sucesso!")

if __name__ == "__main__":
    root = tk.Tk()
    app = CentroCustoApp(root)
    root.mainloop()