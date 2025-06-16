# app_principal.py
# Contém a classe principal do aplicativo de gestão.

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import pandas as pd
from datetime import datetime, timedelta
import random

from data_manager import DataManager
from ui_recorrencias import RecorrenciasManager
from ui_graficos import GraficosManager

class AppPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão Financeira Multi-Empresa")
        self.root.geometry("1400x800")
        self.root.state('zoomed')

        self.data_manager = DataManager(self)
        self.recorrencias_manager = RecorrenciasManager(self)
        self.graficos_manager = GraficosManager(self)

        self.total_receitas_var = tk.StringVar(value="R$ 0.00")
        self.total_despesas_var = tk.StringVar(value="R$ 0.00")
        self.saldo_final_var = tk.StringVar(value="R$ 0.00")
        self.status_var = tk.StringVar(value="Pronto.")
        self.margem_lucro_var = tk.StringVar(value="0.00%")
        self.status_after_id = None

        self.setup_styles()
        self.data_manager.load_all_data()
        self.criar_widgets()
        self.data_manager.load_config()
        self.recorrencias_manager.verificar_e_lancar_recorrencias()
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

    def ao_fechar(self):
        self.data_manager.save_all_data()
        self.data_manager.save_config()
        if self.status_after_id: self.root.after_cancel(self.status_after_id)
        self.root.destroy()

    def set_status(self, message):
        if self.status_after_id: self.root.after_cancel(self.status_after_id)
        self.status_var.set(message)
        self.status_after_id = self.root.after(5000, lambda: self.status_var.set("Pronto."))

    def criar_widgets(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        left_panel = ttk.Frame(main_container, width=450); left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10); left_panel.pack_propagate(False)
        right_panel = ttk.Frame(main_container); right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, style="Status.TLabel"); status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.criar_painel_esquerdo(left_panel)
        self.criar_painel_direito(right_panel)
        self.atualizar_contexto_empresa()

    def criar_painel_esquerdo(self, parent):
        frame_acoes = ttk.Frame(parent); frame_acoes.pack(fill='x', padx=5, pady=(0, 10)); frame_acoes.columnconfigure(0, weight=1); frame_acoes.columnconfigure(1, weight=1)
        btn_graficos = ttk.Button(frame_acoes, text="Análise Gráfica", command=self.graficos_manager.abrir_janela_graficos, style="Info.TButton"); btn_graficos.grid(row=0, column=0, sticky='ew', padx=(0, 2))
        btn_recorrencias = ttk.Button(frame_acoes, text="Gerir Recorrências", command=self.recorrencias_manager.abrir_janela_recorrencias); btn_recorrencias.grid(row=0, column=1, sticky='ew', padx=(2, 0))
        
        frame_empresas = ttk.LabelFrame(parent, text="Gestão de Empresas", padding=(10, 5)); frame_empresas.pack(fill="x", padx=5, pady=5, side=tk.TOP); frame_empresas.columnconfigure(1, weight=1)
        ttk.Label(frame_empresas, text="Empresa Ativa:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_empresa_ativa = ttk.Combobox(frame_empresas, values=list(self.data_manager.dados_empresas.keys()), state="readonly"); self.combo_empresa_ativa.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.combo_empresa_ativa.set(list(self.data_manager.dados_empresas.keys())[0]); self.combo_empresa_ativa.bind("<<ComboboxSelected>>", self.atualizar_contexto_empresa)
        self.btn_excluir_empresa = ttk.Button(frame_empresas, text="Excluir", command=self.excluir_empresa_ativa, style="Danger.TButton", width=8); self.btn_excluir_empresa.grid(row=0, column=2, padx=(5,0))
        ttk.Label(frame_empresas, text="Nova Empresa:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_nova_empresa = ttk.Entry(frame_empresas); self.entry_nova_empresa.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        btn_add_empresa = ttk.Button(frame_empresas, text="Adicionar", command=self.adicionar_empresa, width=8); btn_add_empresa.grid(row=1, column=2, padx=5, pady=5)
        
        frame_categorias = ttk.LabelFrame(parent, text="Gestão de Categorias", padding=(10, 5)); frame_categorias.pack(fill="x", padx=5, pady=5, side=tk.TOP); frame_categorias.columnconfigure(1, weight=1)
        ttk.Label(frame_categorias, text="Categoria:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_excluir_categoria = ttk.Combobox(frame_categorias, state="readonly"); self.combo_excluir_categoria.grid(row=0, column=1, sticky="ew", padx=5)
        self.btn_excluir_categoria = ttk.Button(frame_categorias, text="Excluir", command=self.excluir_categoria, style="Danger.TButton", width=8); self.btn_excluir_categoria.grid(row=0, column=2, padx=5)
        ttk.Label(frame_categorias, text="Nova Categoria:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_nova_categoria = ttk.Entry(frame_categorias); self.entry_nova_categoria.grid(row=1, column=1, sticky="ew", padx=5)
        btn_add_categoria = ttk.Button(frame_categorias, text="Adicionar", command=self.adicionar_categoria, width=8); btn_add_categoria.grid(row=1, column=2, padx=5)
        
        frame_add_cc = ttk.LabelFrame(parent, text="Gestão de Centros de Custo", padding=(10, 5)); frame_add_cc.pack(fill="x", padx=5, pady=5, side=tk.TOP); frame_add_cc.columnconfigure(1, weight=1)
        ttk.Label(frame_add_cc, text="Novo Centro de Custo:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_novo_cc = ttk.Entry(frame_add_cc); self.entry_novo_cc.grid(row=0, column=1, sticky="ew", padx=5)
        btn_add_cc = ttk.Button(frame_add_cc, text="Adicionar", command=self.adicionar_centro_custo, width=8); btn_add_cc.grid(row=0, column=2, padx=5)
        
        btn_novo_lanc = ttk.Button(parent, text="Adicionar Novo Lançamento", command=self.abrir_janela_novo_lancamento, style="Success.TButton"); btn_novo_lanc.pack(fill='x', padx=5, pady=20, ipady=10, side=tk.TOP)
        
        frame_acoes_globais = ttk.Frame(parent); frame_acoes_globais.pack(fill='x', padx=5, pady=(10, 5), side=tk.BOTTOM)
        btn_salvar = ttk.Button(frame_acoes_globais, text="Salvar Alterações", command=self.data_manager.save_all_data); btn_salvar.pack(fill='x')
        
        frame_resumo = ttk.LabelFrame(parent, text="Resumo Financeiro (Filtro Aplicado)", padding=(10, 10)); frame_resumo.pack(fill="x", padx=5, pady=5, side=tk.BOTTOM)
        ttk.Label(frame_resumo, text="Total de Receitas:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5)
        ttk.Label(frame_resumo, textvariable=self.total_receitas_var, font=("Segoe UI", 10), foreground="blue").grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(frame_resumo, text="Total de Despesas:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", padx=5)
        ttk.Label(frame_resumo, textvariable=self.total_despesas_var, font=("Segoe UI", 10), foreground="orange").grid(row=1, column=1, sticky="w", padx=5)
        ttk.Label(frame_resumo, text="Saldo Final:", font=("Segoe UI", 12, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=(10,0))
        self.label_saldo = ttk.Label(frame_resumo, textvariable=self.saldo_final_var); self.label_saldo.grid(row=2, column=1, sticky="w", padx=5, pady=(10,0))
        ttk.Label(frame_resumo, text="Margem de Lucro:", font=("Segoe UI", 12, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=(5,0))
        self.label_margem = ttk.Label(frame_resumo, textvariable=self.margem_lucro_var); self.label_margem.grid(row=3, column=1, sticky="w", padx=5, pady=(5,0))
        
        frame_ferramentas = ttk.LabelFrame(parent, text="Ferramentas de Teste", padding=(10, 5)); frame_ferramentas.pack(fill="x", padx=5, pady=15, side=tk.BOTTOM)
        btn_gerar_dados = ttk.Button(frame_ferramentas, text="Gerar Dados de Teste", command=self.gerar_dados_teste); btn_gerar_dados.pack(fill='x')
        
        self.atualizar_combobox_categorias()
        
    def criar_painel_direito(self, parent):
        notebook = ttk.Notebook(parent); notebook.pack(fill='both', expand=True, padx=5, pady=5)
        tab_lancamentos = ttk.Frame(notebook); tab_dashboard = ttk.Frame(notebook)
        notebook.add(tab_lancamentos, text='Registro de Lançamentos'); notebook.add(tab_dashboard, text='Dashboard')
        
        frame_relatorio = ttk.LabelFrame(tab_lancamentos, text="Filtros e Registros", padding=(10, 5)); frame_relatorio.pack(fill="both", expand=True)
        container = ttk.Frame(frame_relatorio, padding=(0, 5)); container.pack(fill='x')
        
        linha1 = ttk.Frame(container); linha1.pack(fill='x', pady=(0, 5))
        ttk.Label(linha1, text="De:").pack(side='left', padx=(0, 5))
        self.date_inicio = DateEntry(linha1, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy'); self.date_inicio.pack(side='left')
        ttk.Label(linha1, text="Até:").pack(side='left', padx=(10, 5))
        self.date_fim = DateEntry(linha1, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy'); self.date_fim.pack(side='left')
        ttk.Label(linha1, text="Pesquisar Descrição:").pack(side='left', padx=(10, 5))
        self.entry_pesquisa = ttk.Entry(linha1); self.entry_pesquisa.pack(side='left', fill='x', expand=True, padx=5); self.entry_pesquisa.bind("<KeyRelease>", lambda e: self.atualizar_relatorio())
        
        linha2 = ttk.Frame(container); linha2.pack(fill='x')
        ttk.Label(linha2, text="Centro de Custo:").pack(side='left', padx=(0, 5))
        self.combo_filtro_cc = ttk.Combobox(linha2, state="readonly"); self.combo_filtro_cc.pack(side='left', padx=(0,10), fill='x', expand=True); self.combo_filtro_cc.bind("<<ComboboxSelected>>", lambda e: self.atualizar_relatorio())
        ttk.Label(linha2, text="Categoria:").pack(side='left', padx=(0, 5))
        self.combo_filtro_categoria = ttk.Combobox(linha2, state="readonly"); self.combo_filtro_categoria.pack(side='left', padx=(0,10), fill='x', expand=True); self.combo_filtro_categoria.bind("<<ComboboxSelected>>", lambda e: self.atualizar_relatorio())
        ttk.Label(linha2, text="Tipo:").pack(side='left', padx=(0, 5))
        self.combo_filtro_tipo = ttk.Combobox(linha2, values=["Todos", "Receita", "Despesa"], state="readonly"); self.combo_filtro_tipo.pack(side='left', padx=(0,10)); self.combo_filtro_tipo.set("Todos"); self.combo_filtro_tipo.bind("<<ComboboxSelected>>", lambda e: self.atualizar_relatorio())
        ttk.Button(linha2, text="Filtrar", command=self.atualizar_relatorio, width=8).pack(side='left', padx=5)
        
        tree_container = ttk.Frame(frame_relatorio); tree_container.pack(fill='both', expand=True, pady=(5,0))
        self.tree_relatorio = ttk.Treeview(tree_container, columns=("data", "empresa", "centro_custo", "categoria", "descricao", "tipo", "valor"), show="headings"); self.tree_relatorio.bind("<Double-1>", self.abrir_janela_edicao)
        ys = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree_relatorio.yview); xs = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree_relatorio.xview)
        self.tree_relatorio.configure(yscrollcommand=ys.set, xscrollcommand=xs.set); ys.pack(side=tk.RIGHT, fill=tk.Y); xs.pack(side=tk.BOTTOM, fill=tk.X); self.tree_relatorio.pack(side=tk.LEFT, fill="both", expand=True)
        
        for col, name, width in [("data", "Data", 130), ("empresa", "Empresa", 120), ("centro_custo", "Centro de Custo", 150), ("categoria", "Categoria", 120), ("descricao", "Nome/Descrição", 250), ("tipo", "Tipo", 80), ("valor", "Valor (R$)", 100)]:
            self.tree_relatorio.heading(col, text=name); self.tree_relatorio.column(col, width=width, anchor='w' if col != 'valor' else 'e')
        
        frame_botoes = ttk.Frame(frame_relatorio); frame_botoes.pack(side="bottom", pady=5, fill="x")
        ttk.Button(frame_botoes, text="Exportar para Excel", command=self.graficos_manager.exportar_para_excel).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Limpar Lançamentos da Empresa", command=self.limpar_lancamentos_empresa, style="Danger.TButton").pack(side="right", padx=5)
        ttk.Button(frame_botoes, text="Excluir Lançamento", command=self.excluir_lancamento_selecionado, style="Danger.TButton").pack(side="right", padx=5)
        
        ttk.Label(tab_dashboard, text="Em breve: um Dashboard com os principais indicadores!", font=("Segoe UI", 14)).pack(padx=20, pady=20)
        
    def atualizar_contexto_empresa(self, event=None):
        empresa_ativa = self.combo_empresa_ativa.get()
        if empresa_ativa:
            self.btn_excluir_empresa.configure(state=tk.NORMAL if empresa_ativa != "Empresa Padrão" else tk.DISABLED)
            self.combo_filtro_cc['values'] = ["Todos"] + self.data_manager.dados_empresas.get(empresa_ativa, [])
            self.combo_filtro_cc.set("Todos")
            self.combo_filtro_categoria['values'] = ["Todos"] + self.data_manager.categorias
            self.combo_filtro_categoria.set("Todos")
            self.atualizar_relatorio()

    def adicionar_empresa(self):
        nova_empresa = self.entry_nova_empresa.get().strip().title()
        if not nova_empresa: return
        if nova_empresa in self.data_manager.dados_empresas: messagebox.showinfo("Informação", f"A empresa '{nova_empresa}' já existe."); return
        self.data_manager.dados_empresas[nova_empresa] = ["Geral"]
        self.combo_empresa_ativa['values'] = list(self.data_manager.dados_empresas.keys())
        self.combo_empresa_ativa.set(nova_empresa)
        self.entry_nova_empresa.delete(0, tk.END)
        self.atualizar_contexto_empresa()
        self.set_status(f"Empresa '{nova_empresa}' adicionada.")

    def excluir_empresa_ativa(self):
        empresa = self.combo_empresa_ativa.get()
        if empresa == "Empresa Padrão": return
        if messagebox.askyesno("Confirmar Exclusão", f"Excluir a empresa '{empresa}' e TODOS os seus dados?"):
            del self.data_manager.dados_empresas[empresa]
            self.data_manager.df_lancamentos = self.data_manager.df_lancamentos[self.data_manager.df_lancamentos['Empresa'] != empresa].reset_index(drop=True)
            self.combo_empresa_ativa['values'] = list(self.data_manager.dados_empresas.keys())
            self.combo_empresa_ativa.set("Empresa Padrão")
            self.atualizar_contexto_empresa()
            self.set_status(f"Empresa '{empresa}' excluída.")

    def adicionar_centro_custo(self):
        empresa = self.combo_empresa_ativa.get()
        novo_cc = self.entry_novo_cc.get().strip().title()
        if not all([empresa, novo_cc]): return
        if novo_cc in self.data_manager.dados_empresas[empresa]: messagebox.showinfo("Informação", "Centro de custo já existe."); return
        self.data_manager.dados_empresas[empresa].append(novo_cc)
        self.atualizar_contexto_empresa()
        self.set_status(f"Centro de custo '{novo_cc}' adicionado.")

    def adicionar_categoria(self):
        nova_cat = self.entry_nova_categoria.get().strip().title()
        if not nova_cat: return
        if nova_cat in self.data_manager.categorias: messagebox.showinfo("Informação", "Categoria já existe."); return
        self.data_manager.categorias.append(nova_cat)
        self.atualizar_combobox_categorias()
        self.combo_filtro_categoria['values'] = ["Todos"] + self.data_manager.categorias
        self.set_status(f"Categoria '{nova_cat}' adicionada.")

    def excluir_categoria(self):
        cat = self.combo_excluir_categoria.get()
        if not cat: return
        if cat == "Geral": messagebox.showerror("Ação Proibida", "A categoria 'Geral' não pode ser excluída."); return
        if messagebox.askyesno("Confirmar Exclusão", f"Excluir a categoria '{cat}'?\nLançamentos com esta categoria serão movidos para 'Geral'."):
            self.data_manager.df_lancamentos.loc[self.data_manager.df_lancamentos['Categoria'] == cat, 'Categoria'] = 'Geral'
            self.data_manager.categorias.remove(cat)
            self.atualizar_combobox_categorias()
            self.combo_filtro_categoria['values'] = ["Todos"] + self.data_manager.categorias
            self.combo_filtro_categoria.set("Todos")
            self.atualizar_relatorio()
            self.set_status(f"Categoria '{cat}' excluída.")

    def atualizar_combobox_categorias(self):
        cats = [c for c in self.data_manager.categorias if c != "Geral"]
        self.combo_excluir_categoria['values'] = cats
        self.combo_excluir_categoria.set(cats[0] if cats else '')

    def _adicionar_lancamento_logica(self, empresa, cc, categoria, descricao, tipo, valor):
        novo_lanc = pd.DataFrame([[datetime.now(), empresa, cc, categoria, descricao, tipo, valor]], columns=self.data_manager.colunas)
        self.data_manager.df_lancamentos = pd.concat([self.data_manager.df_lancamentos, novo_lanc], ignore_index=True)
        self.atualizar_relatorio()
        self.set_status("Lançamento adicionado com sucesso.")

    def abrir_janela_novo_lancamento(self):
        empresa_ativa = self.combo_empresa_ativa.get()
        if not empresa_ativa: return
        popup = tk.Toplevel(self.root); popup.title("Adicionar Novo Lançamento")
        popup.geometry(f"450x280+{self.root.winfo_x()+200}+{self.root.winfo_y()+200}")
        popup.transient(self.root); popup.grab_set()
        frame = ttk.Frame(popup, padding=15); frame.pack(fill='both', expand=True); frame.columnconfigure(1, weight=1)
        
        ttk.Label(frame, text="Centro de Custo:").grid(row=0, column=0, sticky='w', pady=5)
        combo_cc = ttk.Combobox(frame, values=self.data_manager.dados_empresas[empresa_ativa], state='readonly'); combo_cc.grid(row=0, column=1, sticky='ew', pady=5)
        if self.data_manager.dados_empresas[empresa_ativa]: combo_cc.set(self.data_manager.dados_empresas[empresa_ativa][0])
        
        ttk.Label(frame, text="Categoria:").grid(row=1, column=0, sticky='w', pady=5)
        combo_cat = ttk.Combobox(frame, values=self.data_manager.categorias, state='readonly'); combo_cat.grid(row=1, column=1, sticky='ew', pady=5); combo_cat.set("Geral")
        
        ttk.Label(frame, text="Nome/Descrição:").grid(row=2, column=0, sticky='w', pady=5)
        entry_desc = ttk.Entry(frame); entry_desc.grid(row=2, column=1, sticky='ew', pady=5); entry_desc.focus_set()
        
        ttk.Label(frame, text="Tipo:").grid(row=3, column=0, sticky='w', pady=5)
        combo_tipo = ttk.Combobox(frame, values=["Receita", "Despesa"], state='readonly'); combo_tipo.grid(row=3, column=1, sticky='ew', pady=5); combo_tipo.set("Despesa")
        
        ttk.Label(frame, text="Valor (R$):").grid(row=4, column=0, sticky='w', pady=5)
        entry_valor = ttk.Entry(frame); entry_valor.grid(row=4, column=1, sticky='ew', pady=5)
        
        def salvar():
            try:
                valor = float(entry_valor.get().replace(",", "."))
                if valor <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Erro de Validação", "O valor deve ser um número positivo.", parent=popup); return
            self._adicionar_lancamento_logica(empresa_ativa, combo_cc.get(), combo_cat.get(), entry_desc.get().strip(), combo_tipo.get(), valor)
            popup.destroy()
        
        btn_salvar = ttk.Button(frame, text="Adicionar Lançamento", command=salvar)
        btn_salvar.grid(row=5, column=0, columnspan=2, pady=15)

    def excluir_lancamento_selecionado(self):
        if not self.tree_relatorio.focus(): return
        if messagebox.askyesno("Confirmar", "Excluir o lançamento selecionado?"):
            self.data_manager.df_lancamentos.drop(int(self.tree_relatorio.focus()), inplace=True)
            self.data_manager.df_lancamentos = self.data_manager.df_lancamentos.reset_index(drop=True)
            self.atualizar_relatorio()
            self.set_status("Lançamento excluído.")

    def limpar_lancamentos_empresa(self):
        empresa = self.combo_empresa_ativa.get()
        if not empresa: return
        if messagebox.askyesno("Confirmar Limpeza", f"Tem a certeza de que deseja apagar TODOS os lançamentos da '{empresa}'?"):
            self.data_manager.df_lancamentos = self.data_manager.df_lancamentos[self.data_manager.df_lancamentos['Empresa'] != empresa].reset_index(drop=True)
            self.atualizar_relatorio()
            self.set_status(f"Lançamentos da empresa '{empresa}' foram apagados.")
    
    def get_filtered_data(self):
        empresa = self.combo_empresa_ativa.get()
        if not empresa or self.data_manager.df_lancamentos.empty: return pd.DataFrame(columns=self.colunas)
        
        df = self.data_manager.df_lancamentos[self.data_manager.df_lancamentos['Empresa'] == empresa].copy()
        
        start_date = pd.to_datetime(self.date_inicio.get_date())
        end_date = pd.to_datetime(self.date_fim.get_date()).replace(hour=23, minute=59, second=59)
        df = df[(df['Data'] >= start_date) & (df['Data'] <= end_date)]
        
        filters = {
            'Nome/Descrição': self.entry_pesquisa.get().strip().lower(),
            'Centro de Custo': self.combo_filtro_cc.get(),
            'Categoria': self.combo_filtro_categoria.get(),
            'Tipo': self.combo_filtro_tipo.get()
        }
        if filters['Nome/Descrição']: df = df[df['Nome/Descrição'].str.lower().str.contains(filters['Nome/Descrição'])]
        for col, val in filters.items():
            if col != 'Nome/Descrição' and val and val != "Todos":
                df = df[df[col] == val]
        return df

    def atualizar_relatorio(self):
        for i in self.tree_relatorio.get_children(): self.tree_relatorio.delete(i)
        df_filtrado = self.get_filtered_data()
        
        if not self.combo_empresa_ativa.get():
             self.atualizar_resumo(pd.DataFrame())
             return

        df_ordenado = df_filtrado.sort_values(by="Data", ascending=False)
        for index, row in df_ordenado.iterrows():
            self.tree_relatorio.insert("", "end", iid=index, values=(row["Data"].strftime("%Y-%m-%d %H:%M"), row["Empresa"], row["Centro de Custo"], row["Categoria"], row["Nome/Descrição"], row["Tipo"], f"{row['Valor']:.2f}"))
        
        self.atualizar_resumo(df_filtrado)

    def atualizar_resumo(self, df):
        if df.empty:
            total_receitas, total_despesas, saldo, margem = 0, 0, 0, 0
        else:
            total_receitas = df[df['Tipo'] == 'Receita']['Valor'].sum()
            total_despesas = df[df['Tipo'] == 'Despesa']['Valor'].sum()
            saldo = total_receitas - total_despesas
            margem = (saldo / total_receitas) * 100 if total_receitas > 0 else 0
        
        self.total_receitas_var.set(f"R$ {total_receitas:,.2f}")
        self.total_despesas_var.set(f"R$ {total_despesas:,.2f}")
        self.saldo_final_var.set(f"R$ {saldo:,.2f}")
        self.margem_lucro_var.set(f"{margem:.2f}%")
        
        style = "Neutral.TLabel"
        if saldo > 0: style = "Success.TLabel"
        elif saldo < 0: style = "Error.TLabel"
        self.label_saldo.configure(style=style)
        self.label_margem.configure(style=style)

    def abrir_janela_edicao(self, event):
        if not self.tree_relatorio.focus(): return
        index = int(self.tree_relatorio.focus())
        dados = self.data_manager.df_lancamentos.loc[index]
        
        win = tk.Toplevel(self.root); win.title("Editar Lançamento")
        win.geometry(f"400x300+{self.root.winfo_x()+200}+{self.root.winfo_y()+200}")
        win.transient(self.root); win.grab_set()
        
        frame = ttk.Frame(win, padding=10); frame.pack(fill='both', expand=True); frame.columnconfigure(1, weight=1)
        
        campos = {}
        ttk.Label(frame, text="Centro de Custo:").grid(row=0, column=0, sticky='w', pady=5)
        campos['cc'] = ttk.Combobox(frame, values=self.data_manager.dados_empresas[dados['Empresa']], state='readonly'); campos['cc'].set(dados['Centro de Custo']); campos['cc'].grid(row=0, column=1, sticky='ew', pady=5)
        
        ttk.Label(frame, text="Categoria:").grid(row=1, column=0, sticky='w', pady=5)
        campos['cat'] = ttk.Combobox(frame, values=self.data_manager.categorias, state='readonly'); campos['cat'].set(dados['Categoria']); campos['cat'].grid(row=1, column=1, sticky='ew', pady=5)
        
        ttk.Label(frame, text="Nome/Descrição:").grid(row=2, column=0, sticky='w', pady=5)
        campos['desc'] = ttk.Entry(frame); campos['desc'].insert(0, dados['Nome/Descrição']); campos['desc'].grid(row=2, column=1, sticky='ew', pady=5)
        
        ttk.Label(frame, text="Tipo:").grid(row=3, column=0, sticky='w', pady=5)
        campos['tipo'] = ttk.Combobox(frame, values=["Receita", "Despesa"], state='readonly'); campos['tipo'].set(dados['Tipo']); campos['tipo'].grid(row=3, column=1, sticky='ew', pady=5)
        
        ttk.Label(frame, text="Valor (R$):").grid(row=4, column=0, sticky='w', pady=5)
        campos['valor'] = ttk.Entry(frame); campos['valor'].insert(0, f"{dados['Valor']:.2f}"); campos['valor'].grid(row=4, column=1, sticky='ew', pady=5)
        
        def salvar_edicao():
            try: novo_valor = float(campos['valor'].get().replace(",", ".")); assert novo_valor > 0
            except: messagebox.showerror("Erro", "Valor inválido.", parent=win); return
            
            self.data_manager.df_lancamentos.loc[index, 'Centro de Custo'] = campos['cc'].get()
            self.data_manager.df_lancamentos.loc[index, 'Categoria'] = campos['cat'].get()
            self.data_manager.df_lancamentos.loc[index, 'Nome/Descrição'] = campos['desc'].get()
            self.data_manager.df_lancamentos.loc[index, 'Tipo'] = campos['tipo'].get()
            self.data_manager.df_lancamentos.loc[index, 'Valor'] = novo_valor
            
            self.atualizar_relatorio()
            self.set_status("Lançamento editado com sucesso.")
            win.destroy()
        
        ttk.Button(frame, text="Salvar Alterações", command=salvar_edicao).grid(row=5, column=0, columnspan=2, pady=10)

    def gerar_dados_teste(self):
        if not messagebox.askyesno("Confirmar", "Isto irá apagar todos os dados atuais e gerar um novo conjunto de dados de teste. Deseja continuar?"): return
        self.data_manager.df_lancamentos = pd.DataFrame(columns=self.colunas)
        self.data_manager.dados_empresas = {"Tecnologia BR": ["Desenvolvimento", "Marketing", "Infraestrutura"], "Varejo SP": ["Loja Centro", "Logística", "Administrativo"]}
        self.data_manager.categorias = ["Software", "Hardware", "Publicidade", "Salários", "Fornecedores", "Vendas", "Serviços", "Geral"]
        lancamentos = []
        hoje = datetime.now(); data_antiga = hoje - timedelta(days=365)
        for _ in range(150):
            empresa = random.choice(list(self.data_manager.dados_empresas.keys())); cc = random.choice(self.data_manager.dados_empresas[empresa]); cat = random.choice(self.data_manager.categorias)
            tipo = random.choices(["Receita", "Despesa"], weights=[0.4, 0.6], k=1)[0]
            data = hoje - timedelta(days=random.randint(0, 365))
            desc = f"Venda {random.choice(['Prod A', 'Serv B'])} #{random.randint(100,999)}" if tipo == "Receita" else f"Pagamento {random.choice(['Forn X', 'Soft Y'])}"
            valor = random.uniform(500, 15000) if tipo == "Receita" else random.uniform(100, 8000)
            lancamentos.append([data, empresa, cc, cat, desc, tipo, valor])
        self.data_manager.df_lancamentos = pd.DataFrame(lancamentos, columns=self.colunas)
        self.combo_empresa_ativa['values'] = list(self.data_manager.dados_empresas.keys()); self.combo_empresa_ativa.set(list(self.data_manager.dados_empresas.keys())[0])
        self.date_inicio.set_date(data_antiga); self.date_fim.set_date(hoje)
        self.atualizar_contexto_empresa(); self.atualizar_combobox_categorias(); self.data_manager.save_all_data()
        self.set_status("Dados de teste gerados e guardados com sucesso!")
