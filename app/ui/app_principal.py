# app/ui/app_principal.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import pandas as pd
# Importar o DateEntry correto, diretamente do ttkbootstrap
from ttkbootstrap.widgets import DateEntry

class AppPrincipal:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.controller = None
        self.master.title("Controle de Centro de Custos")
        self.master.geometry("1200x800")
        
        self.paned_window = ttk.PanedWindow(master, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.paned_window, width=250)
        self.paned_window.add(self.left_frame, weight=1)

        self.right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_frame, weight=4)

        self.create_left_panel()
        self.create_right_panel()
        self.create_status_bar()

    def set_controller(self, controller):
        self.controller = controller
        # Configuração dos comandos dos botões
        self.btn_aplicar.config(command=self.controller.aplicar_filtros_e_resetar_pagina)
        self.btn_limpar.config(command=self.controller.limpar_filtros)
        self.btn_exportar.config(command=self.controller.exportar_para_excel)
        self.btn_prox_pagina.config(command=lambda: self.controller.change_page(1))
        self.btn_ant_pagina.config(command=lambda: self.controller.change_page(-1))
        self.btn_excluir_lancamento.config(command=self.controller.excluir_lancamento_selecionado)
        self.combo_empresa_ativa.bind("<<ComboboxSelected>>", self.controller.on_empresa_selecionada)
        self.btn_add_cliente.config(command=lambda: self.controller.adicionar_item_rapido('Cliente', self.entry_novo_cliente.get()))
        self.btn_add_veiculo.config(command=lambda: self.controller.adicionar_item_rapido('Veículo', self.entry_novo_veiculo.get()))
        self.btn_add_cc.config(command=lambda: self.controller.adicionar_item_rapido('Centro de Custo', self.entry_novo_cc.get()))
        self.btn_add_categoria.config(command=lambda: self.controller.adicionar_item_rapido('Categoria', self.entry_nova_categoria.get()))
        self.btn_add_empresa.config(command=lambda: self.controller.adicionar_item_rapido('Empresa', self.entry_nova_empresa.get()))

    # ... (O resto dos métodos create_left_panel, etc. permanecem os mesmos) ...
    def create_left_panel(self):
        empresa_frame = ttk.LabelFrame(self.left_frame, text="Empresa Ativa")
        empresa_frame.pack(pady=10, padx=10, fill='x')
        self.combo_empresa_ativa = ttk.Combobox(empresa_frame, state="readonly")
        self.combo_empresa_ativa.pack(pady=5, padx=5, fill='x')

        cadastros_frame = ttk.LabelFrame(self.left_frame, text="Cadastros Rápidos")
        cadastros_frame.pack(pady=10, padx=10, fill='x')
        
        ttk.Label(cadastros_frame, text="Novo Cliente").pack(anchor='w', padx=5)
        self.entry_novo_cliente = ttk.Entry(cadastros_frame)
        self.entry_novo_cliente.pack(fill='x', padx=5, pady=(0,5))
        self.btn_add_cliente = ttk.Button(cadastros_frame, text="Adicionar Cliente")
        self.btn_add_cliente.pack(fill='x', padx=5, pady=(0,10))

        ttk.Label(cadastros_frame, text="Novo Veículo (Placa)").pack(anchor='w', padx=5)
        self.entry_novo_veiculo = ttk.Entry(cadastros_frame)
        self.entry_novo_veiculo.pack(fill='x', padx=5, pady=(0,5))
        self.btn_add_veiculo = ttk.Button(cadastros_frame, text="Adicionar Veículo")
        self.btn_add_veiculo.pack(fill='x', padx=5, pady=(0,10))
        
        ttk.Label(cadastros_frame, text="Novo Centro de Custo").pack(anchor='w', padx=5)
        self.entry_novo_cc = ttk.Entry(cadastros_frame)
        self.entry_novo_cc.pack(fill='x', padx=5, pady=(0,5))
        self.btn_add_cc = ttk.Button(cadastros_frame, text="Adicionar Centro de Custo")
        self.btn_add_cc.pack(fill='x', padx=5, pady=(0,10))

        ttk.Label(cadastros_frame, text="Nova Categoria (Ex: Pedágio)").pack(anchor='w', padx=5)
        self.entry_nova_categoria = ttk.Entry(cadastros_frame)
        self.entry_nova_categoria.pack(fill='x', padx=5, pady=(0,5))
        self.btn_add_categoria = ttk.Button(cadastros_frame, text="Adicionar Categoria")
        self.btn_add_categoria.pack(fill='x', padx=5, pady=(0,10))
        
        ttk.Label(cadastros_frame, text="Nova Empresa (Matriz/Filial)").pack(anchor='w', padx=5)
        self.entry_nova_empresa = ttk.Entry(cadastros_frame)
        self.entry_nova_empresa.pack(fill='x', padx=5, pady=(0,5))
        self.btn_add_empresa = ttk.Button(cadastros_frame, text="Adicionar Empresa")
        self.btn_add_empresa.pack(fill='x', padx=5, pady=(0,10))
        
        resumo_frame = ttk.LabelFrame(self.left_frame, text="Resumo Financeiro")
        resumo_frame.pack(pady=10, padx=10, fill='x')
        self.lbl_receitas = ttk.Label(resumo_frame, text="Receitas: R$ 0.00")
        self.lbl_receitas.pack(anchor='w')
        self.lbl_despesas = ttk.Label(resumo_frame, text="Despesas: R$ 0.00")
        self.lbl_despesas.pack(anchor='w')
        self.lbl_saldo = ttk.Label(resumo_frame, text="Saldo: R$ 0.00")
        self.lbl_saldo.pack(anchor='w')

    def create_right_panel(self):
        btn_novo_lancamento = ttk.Button(self.right_frame, text="Adicionar Novo Lançamento", command=self.abrir_janela_novo_lancamento)
        btn_novo_lancamento.pack(pady=10, padx=10, anchor='w')
        
        filter_frame = ttk.LabelFrame(self.right_frame, text="Filtros")
        filter_frame.pack(pady=10, padx=10, fill='x')

        top_filter_frame = ttk.Frame(filter_frame)
        top_filter_frame.pack(fill='x', expand=True)

        hoje = datetime.now()
        data_inicio_default = hoje - timedelta(days=365)
        
        ttk.Label(top_filter_frame, text="De:").pack(side='left', padx=(0,5))
        # USANDO O DateEntry do ttkbootstrap
        self.date_inicio = DateEntry(top_filter_frame, dateformat='%d/%m/%Y', startdate=data_inicio_default, firstweekday=6)
        self.date_inicio.pack(side='left', padx=(0,10))

        ttk.Label(top_filter_frame, text="Até:").pack(side='left', padx=(0,5))
        # USANDO O DateEntry do ttkbootstrap
        self.date_fim = DateEntry(top_filter_frame, dateformat='%d/%m/%Y', startdate=hoje, firstweekday=6)
        self.date_fim.pack(side='left', padx=(0,10))

        self.btn_aplicar = ttk.Button(top_filter_frame, text="Aplicar Filtros")
        self.btn_aplicar.pack(side='left', padx=5)
        self.btn_limpar = ttk.Button(top_filter_frame, text="Limpar Filtros")
        self.btn_limpar.pack(side='left', padx=5)
        self.btn_exportar = ttk.Button(top_filter_frame, text="Exportar para Excel")
        self.btn_exportar.pack(side='left', padx=5)

        bottom_filter_frame = ttk.Frame(filter_frame)
        bottom_filter_frame.pack(fill='x', expand=True, pady=(10,0))
        
        self.combo_filtro_tipo = self.create_filter_combobox(bottom_filter_frame, "Tipo")
        self.combo_filtro_cc = self.create_filter_combobox(bottom_filter_frame, "Centro de Custo")
        self.combo_filtro_veiculo = self.create_filter_combobox(bottom_filter_frame, "Veículo")
        self.combo_filtro_categoria = self.create_filter_combobox(bottom_filter_frame, "Categoria")
        self.combo_filtro_cliente = self.create_filter_combobox(bottom_filter_frame, "Cliente")
        self.combo_filtro_status = self.create_filter_combobox(bottom_filter_frame, "Status")

        self.notebook = ttk.Notebook(self.right_frame)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)
        self.tab_registros = ttk.Frame(self.notebook)
        self.tab_graficos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_registros, text='Registros Detalhados')
        self.notebook.add(self.tab_graficos, text='Gráficos Visuais')

        self.create_registros_tab()

    def create_registros_tab(self):
        cols = ('Data', 'Empresa', 'Centro de Custo', 'Veículo', 'Categoria', 'Descrição', 'Tipo', 'Valor')
        self.tree_relatorio = ttk.Treeview(self.tab_registros, columns=cols, show='headings', height=20)
        for col in cols:
            self.tree_relatorio.heading(col, text=col)
            self.tree_relatorio.column(col, width=120)
        self.tree_relatorio.pack(side="top", fill="both", expand=True)

        paginacao_frame = ttk.Frame(self.tab_registros)
        paginacao_frame.pack(fill='x', pady=5)
        self.btn_ant_pagina = ttk.Button(paginacao_frame, text="< Anterior")
        self.btn_ant_pagina.pack(side='left', padx=5)
        self.lbl_pagina = ttk.Label(paginacao_frame, text="Página 1 de 1")
        self.lbl_pagina.pack(side='left', padx=5)
        self.btn_prox_pagina = ttk.Button(paginacao_frame, text="Próximo >")
        self.btn_prox_pagina.pack(side='left', padx=5)

        self.btn_excluir_lancamento = ttk.Button(paginacao_frame, text="Excluir Lançamento Selecionado")
        self.btn_excluir_lancamento.pack(side='right', padx=10)

    def create_filter_combobox(self, parent, label):
        frame = ttk.Frame(parent)
        frame.pack(side='left', padx=5, fill='x', expand=True)
        ttk.Label(frame, text=label).pack(side='top', anchor='w')
        combo = ttk.Combobox(frame, state="readonly")
        combo.pack(side='top', fill='x', expand=True)
        return combo

    def create_status_bar(self):
        self.status_bar = ttk.Label(self.master, text="Pronto", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def set_status(self, message):
        self.status_bar.config(text=message)

    def get_filtros(self):
        # O DateEntry do ttkbootstrap retorna o texto, então precisamos converter para data
        try:
            inicio = datetime.strptime(self.date_inicio.entry.get(), '%d/%m/%Y')
            fim = datetime.strptime(self.date_fim.entry.get(), '%d/%m/%Y')
        except ValueError:
            # Caso a data esteja em formato inválido, não filtra por data
            inicio, fim = None, None
        return {
            'data_inicio': inicio,
            'data_fim': fim,
            'cc': self.combo_filtro_cc.get(),
            'veiculo': self.combo_filtro_veiculo.get(),
            'categoria': self.combo_filtro_categoria.get(),
            'tipo': self.combo_filtro_tipo.get(),
            'cliente': self.combo_filtro_cliente.get(),
            'status': self.combo_filtro_status.get()
        }
    
    def get_empresa_ativa(self):
        return self.combo_empresa_ativa.get()
    
    def reset_filters(self):
        # Resetar as datas para o padrão (último ano até hoje)
        hoje = datetime.now()
        data_inicio_default = hoje - timedelta(days=365)

        # Formata as datas para a string no formato DD/MM/YYYY esperado pelo DateEntry
        data_inicio_str = data_inicio_default.strftime('%d/%m/%Y')
        data_fim_str = hoje.strftime('%d/%m/%Y')

        # Limpa o conteúdo atual e insere a nova data formatada
        self.date_inicio.entry.delete(0, tk.END)
        self.date_inicio.entry.insert(0, data_inicio_str)

        self.date_fim.entry.delete(0, tk.END)
        self.date_fim.entry.insert(0, data_fim_str)

        # Resetar os comboboxes de filtro para "Todos"
        self.combo_filtro_cc.set("Todos")
        self.combo_filtro_veiculo.set("Todos")
        self.combo_filtro_categoria.set("Todos")
        self.combo_filtro_tipo.set("Todos")
        self.combo_filtro_cliente.set("Todos")
        self.combo_filtro_status.set("Todos")

        # Resetar os comboboxes de filtro para "Todos"
        self.combo_filtro_cc.set("Todos")
        self.combo_filtro_veiculo.set("Todos")
        self.combo_filtro_categoria.set("Todos")
        self.combo_filtro_tipo.set("Todos")
        self.combo_filtro_cliente.set("Todos")
        self.combo_filtro_status.set("Todos")

    def update_empresa_dropdown(self, empresas, set_default=False):
        self.combo_empresa_ativa['values'] = empresas
        if set_default and empresas:
            self.combo_empresa_ativa.set(empresas[0])

    def update_dropdown(self, dropdown_name, values):
        dropdowns = {
            'cc': self.combo_filtro_cc, 'veiculo': self.combo_filtro_veiculo,
            'categoria': self.combo_filtro_categoria, 'tipo': self.combo_filtro_tipo,
            'cliente': self.combo_filtro_cliente, 'status': self.combo_filtro_status
        }
        if dropdown_name in dropdowns:
            dropdowns[dropdown_name]['values'] = ["Todos"] + values
            dropdowns[dropdown_name].set("Todos")
    
    def update_page_info(self, current, total):
        self.lbl_pagina.config(text=f"Página {current} de {total}")

    def update_lancamentos_treeview(self, dataframe):
        for i in self.tree_relatorio.get_children():
            self.tree_relatorio.delete(i)
        if dataframe is None: return

        df_display = dataframe.rename(columns={"Centro_de_Custo": "Centro de Custo"})
        for index, row in df_display.iterrows():
            valor_formatado = f"R$ {row.get('Valor', 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            data_formatada = row.get('Data', pd.Timestamp.now()).strftime('%d/%m/%Y')

            valores_linha = (
                data_formatada, row.get('Empresa', ''), row.get('Centro de Custo', ''),
                row.get('Veículo', ''), row.get('Categoria', ''), row.get('Descrição', ''),
                row.get('Tipo', ''), valor_formatado
            )
            self.tree_relatorio.insert("", "end", iid=index, values=valores_linha)

    def update_financial_summary(self, receitas, despesas, saldo):
            # Configura as Receitas em verde
            self.lbl_receitas.config(
                text=f"Receitas: R$ {receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                foreground="green" # Cor verde para receitas
            )

            # Configura as Despesas em vermelho
            self.lbl_despesas.config(
                text=f"Despesas: R$ {despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                foreground="red" # Cor vermelha para despesas
            )

            # Formata o texto do saldo
            saldo_text = f"Saldo: R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            # Define a cor do saldo com base no seu valor
            if saldo > 0:
                self.lbl_saldo.config(text=saldo_text, foreground="green") # Verde para saldo positivo
            elif saldo < 0:
                self.lbl_saldo.config(text=saldo_text, foreground="red") # Vermelho para saldo negativo
            else:
                self.lbl_saldo.config(text=saldo_text, foreground="black") # Preto para saldo zero ou neutro

    def get_selected_lancamento_id(self):
        selected_items = self.tree_relatorio.selection()
        if not selected_items: return None
        return selected_items[0]

    def ask_yes_no(self, message):
        return messagebox.askyesno("Confirmação", message)
        
    def abrir_janela_novo_lancamento(self):
        if self.controller:
            self.criar_janela_lancamento("Novo Lançamento", self.controller.salvar_novo_lancamento)

    def criar_janela_lancamento(self, titulo, callback_salvar, dados_edicao=None):
        popup = tk.Toplevel(self.master)
        popup.title(titulo)

        frame = ttk.Frame(popup, padding="10")
        frame.pack(fill="both", expand=True)

        def get_combobox_values(combobox):
            values = combobox['values']
            if isinstance(values, str):
                return []
            return list(values)

        row = 0
        ttk.Label(frame, text="Data:").grid(row=row, column=0, sticky="w", pady=5)
        entry_data = DateEntry(frame, dateformat='%d/%m/%Y', firstweekday=6)
        entry_data.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        ttk.Label(frame, text="Centro de Custo:").grid(row=row, column=0, sticky="w", pady=5)
        cc_values = get_combobox_values(self.combo_filtro_cc)
        combo_cc = ttk.Combobox(frame, state="readonly", values=cc_values[1:] if cc_values else [])
        combo_cc.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        ttk.Label(frame, text="Veículo:").grid(row=row, column=0, sticky="w", pady=5)
        veiculo_values = get_combobox_values(self.combo_filtro_veiculo)
        combo_veiculo = ttk.Combobox(frame, state="readonly", values=["N/A"] + (veiculo_values[1:] if veiculo_values else []))
        combo_veiculo.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1

        ttk.Label(frame, text="Categoria:").grid(row=row, column=0, sticky="w", pady=5)
        cat_values = get_combobox_values(self.combo_filtro_categoria)
        combo_cat = ttk.Combobox(frame, state="readonly", values=cat_values[1:] if cat_values else [])
        combo_cat.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1

        ttk.Label(frame, text="Descrição:").grid(row=row, column=0, sticky="w", pady=5)
        entry_desc = ttk.Entry(frame)
        entry_desc.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1

        ttk.Label(frame, text="Tipo:").grid(row=row, column=0, sticky="w", pady=5)
        combo_tipo = ttk.Combobox(frame, state="readonly", values=["Receita", "Despesa"])
        combo_tipo.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        ttk.Label(frame, text="Valor:").grid(row=row, column=0, sticky="w", pady=5)
        entry_valor = ttk.Entry(frame)
        entry_valor.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1

        def on_save():
            if not all([combo_cat.get(), entry_desc.get(), combo_tipo.get(), entry_valor.get()]):
                messagebox.showwarning("Campos Vazios", "Categoria, Descrição, Tipo e Valor são obrigatórios.", parent=popup)
                return

            try:
                valor_float = float(entry_valor.get().replace(",", "."))
                data_obj = datetime.strptime(entry_data.entry.get(), '%d/%m/%Y')
                dados = {
                    'Data': data_obj, 'Centro_de_Custo': combo_cc.get() or None,
                    'Veículo': combo_veiculo.get() if combo_veiculo.get() != "N/A" else None,
                    'Categoria': combo_cat.get(), 'Descrição': entry_desc.get(),
                    'Tipo': combo_tipo.get(), 'Valor': valor_float,
                    'Cliente': None, 'Status': 'Pendente'
                }
                callback_salvar(dados)
                popup.destroy()
            except ValueError:
                messagebox.showerror("Erro de Valor", "Verifique o formato do valor ou da data.", parent=popup)

        btn_salvar = ttk.Button(frame, text="Salvar", command=on_save)
        btn_salvar.grid(row=row, column=1, sticky="e", pady=10)
        
        frame.columnconfigure(1, weight=1)