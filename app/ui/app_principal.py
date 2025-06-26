# app/ui/app_principal.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, END, Listbox, SINGLE, VERTICAL, HORIZONTAL, BOTH, Y, X, LEFT, RIGHT, BOTTOM
from datetime import datetime, timedelta
import pandas as pd
import math

from .ui_graficos import GraficosFrame
from app.core.data_manager import DataManager
from app.core.controller import AppController

class PlaceholderEntry(ttk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['foreground'] or 'black'
        self.bind("<FocusIn>", self._focus_in)
        self.bind("<FocusOut>", self._focus_out)
        self.put_placeholder()
    def put_placeholder(self):
        self.delete(0, END); self.insert(0, self.placeholder); self.config(foreground=self.placeholder_color)
    def _focus_in(self, *args):
        if self.cget('foreground') == self.placeholder_color:
            self.delete('0', END); self.config(foreground=self.default_fg_color)
    def _focus_out(self, *args):
        if not self.get(): self.put_placeholder()
    def get(self):
        return "" if self.cget('foreground') == self.placeholder_color else super().get()

class AppPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão para Transportadora")
        self.root.geometry("1400x800")
        try: self.root.state('zoomed')
        except: pass
        self._setup_styles()
        self.total_receitas_var = ttk.StringVar(value="R$ 0.00")
        self.total_despesas_var = ttk.StringVar(value="R$ 0.00")
        self.saldo_final_var = ttk.StringVar(value="R$ 0.00")
        self.status_var = ttk.StringVar(value="Pronto.")
        self.pagination_var = ttk.StringVar(value="Página 1 de 1")
        self.model = DataManager()
        self.criar_widgets()
        self.controller = AppController(self.model, self)
        self.controller.iniciar_app()
        self.root.protocol("WM_DELETE_WINDOW", self.controller.ao_fechar)

    def _setup_styles(self):
        style = ttk.Style.get_instance(); fonte_global = ("Segoe UI", 10)
        style.configure('.', font=fonte_global)
        style.configure('Treeview.Heading', font=(fonte_global[0], fonte_global[1], 'bold'))
        style.configure('TLabelframe.Label', font=(fonte_global[0], fonte_global[1], 'bold'))
        style.configure('Treeview', rowheight=28)

    def criar_widgets(self):
        main_container = ttk.Frame(self.root, padding=10); main_container.pack(fill=BOTH, expand=True)
        left_panel = ttk.Frame(main_container, width=350); left_panel.pack(side=LEFT, fill=Y, padx=(0, 10)); left_panel.pack_propagate(False)
        right_panel = ttk.Frame(main_container); right_panel.pack(side=RIGHT, fill=BOTH, expand=True)
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=SUNKEN, anchor=W, padding=5); status_bar.pack(side=BOTTOM, fill=X)
        self.criar_painel_esquerdo(left_panel); self.criar_painel_direito(right_panel)

    def criar_painel_esquerdo(self, parent):
        frame_empresa_ativa = ttk.LabelFrame(parent, text="Sua Empresa", padding=10); frame_empresa_ativa.pack(fill=X, pady=(0, 10))
        self.combo_empresa_ativa = ttk.Combobox(frame_empresa_ativa, state="readonly"); self.combo_empresa_ativa.pack(fill=X); self.combo_empresa_ativa.bind("<<ComboboxSelected>>", lambda e: self.controller.on_empresa_selecionada())
        frame_acoes = ttk.LabelFrame(parent, text="Ações", padding=10); frame_acoes.pack(fill=X, pady=(0, 10))
        ttk.Button(frame_acoes, text="Adicionar Novo Lançamento", command=lambda: self.controller.abrir_janela_novo_lancamento(), bootstyle="success").pack(fill=X, ipady=5)
        ttk.Button(frame_acoes, text="Gerenciar Cadastros", command=lambda: self.controller.abrir_janela_gerenciamento(), bootstyle="secondary").pack(fill=X, ipady=5, pady=(5,0))
        frame_gestao = ttk.LabelFrame(parent, text="Cadastros Rápidos", padding=10); frame_gestao.pack(fill=X, pady=(0, 10))
        self.entry_novo_cliente = PlaceholderEntry(frame_gestao, placeholder="Novo Cliente"); self.entry_novo_cliente.pack(fill=X, pady=(0,5))
        ttk.Button(frame_gestao, text="Adicionar Cliente", command=lambda: self.controller.adicionar_cliente(), bootstyle="outline-primary").pack(fill=X, pady=(0,10))
        self.entry_novo_veiculo = PlaceholderEntry(frame_gestao, placeholder="Novo Veículo (Placa)"); self.entry_novo_veiculo.pack(fill=X, pady=(0,5))
        ttk.Button(frame_gestao, text="Adicionar Veículo", command=lambda: self.controller.adicionar_veiculo(), bootstyle="outline-primary").pack(fill=X, pady=(0,10))
        self.entry_novo_cc = PlaceholderEntry(frame_gestao, placeholder="Novo Centro de Custo"); self.entry_novo_cc.pack(fill=X, pady=(0,5))
        ttk.Button(frame_gestao, text="Adicionar Centro de Custo", command=lambda: self.controller.adicionar_centro_custo(), bootstyle="outline-primary").pack(fill=X, pady=(0,10))
        self.entry_nova_categoria = PlaceholderEntry(frame_gestao, placeholder="Nova Categoria (Ex: Pedágio)"); self.entry_nova_categoria.pack(fill=X, pady=(0,5))
        ttk.Button(frame_gestao, text="Adicionar Categoria", command=lambda: self.controller.adicionar_categoria(), bootstyle="outline-primary").pack(fill=X, pady=(0,10))
        self.entry_nova_empresa = PlaceholderEntry(frame_gestao, placeholder="Nova Empresa (Matriz/Filial)"); self.entry_nova_empresa.pack(fill=X, pady=(0,5))
        ttk.Button(frame_gestao, text="Adicionar Empresa", command=lambda: self.controller.adicionar_empresa(), bootstyle="outline-primary").pack(fill=X)
        frame_resumo = ttk.LabelFrame(parent, text="Resumo Financeiro", padding=10); frame_resumo.pack(fill=X, pady=(0, 10), side=BOTTOM); frame_resumo.columnconfigure(1, weight=1)
        ttk.Label(frame_resumo, text="Receitas:", font="-weight bold").grid(row=0, column=0, sticky=W); ttk.Label(frame_resumo, textvariable=self.total_receitas_var, bootstyle="success").grid(row=0, column=1, sticky=E)
        ttk.Label(frame_resumo, text="Despesas:", font="-weight bold").grid(row=1, column=0, sticky=W); ttk.Label(frame_resumo, textvariable=self.total_despesas_var, bootstyle="danger").grid(row=1, column=1, sticky=E)
        ttk.Label(frame_resumo, text="Saldo:", font="-weight bold -size 12").grid(row=2, column=0, sticky=W, pady=(10, 0))
        self.label_saldo = ttk.Label(frame_resumo, textvariable=self.saldo_final_var, font="-weight bold -size 12"); self.label_saldo.grid(row=2, column=1, sticky=E, pady=(10, 0))

    def criar_painel_direito(self, parent):
        filter_frame = ttk.LabelFrame(parent, text="Filtros e Ações", padding=10); filter_frame.pack(fill=X, pady=(0, 10))
        top_filter_frame = ttk.Frame(filter_frame); top_filter_frame.pack(fill=X, pady=(0,10)); top_filter_frame.columnconfigure((1,3,5), weight=1)
        hoje = datetime.now(); data_inicio_default = hoje - timedelta(days=365)
        ttk.Label(top_filter_frame, text="De:").grid(row=0, column=0, padx=(0,5), pady=5, sticky=W)
        self.date_inicio = ttk.DateEntry(top_filter_frame, dateformat='%d/%m/%Y', startdate=data_inicio_default); self.date_inicio.grid(row=0, column=1, sticky=EW, padx=(0,10))
        ttk.Label(top_filter_frame, text="Até:").grid(row=0, column=2, padx=(0,5), pady=5, sticky=W)
        self.date_fim = ttk.DateEntry(top_filter_frame, dateformat='%d/%m/%Y'); self.date_fim.grid(row=0, column=3, sticky=EW, padx=(0,10))
        ttk.Label(top_filter_frame, text="Centro de Custo:").grid(row=1, column=0, padx=(0,5), pady=5, sticky=W)
        self.combo_filtro_cc = ttk.Combobox(top_filter_frame, state="readonly"); self.combo_filtro_cc.grid(row=1, column=1, sticky=EW, padx=(0,10))
        ttk.Label(top_filter_frame, text="Veículo:").grid(row=1, column=2, padx=(0,5), pady=5, sticky=W)
        self.combo_filtro_veiculo = ttk.Combobox(top_filter_frame, state="readonly"); self.combo_filtro_veiculo.grid(row=1, column=3, sticky=EW, padx=(0,10))
        ttk.Label(top_filter_frame, text="Categoria:").grid(row=2, column=0, padx=(0,5), pady=5, sticky=W)
        self.combo_filtro_categoria = ttk.Combobox(top_filter_frame, state="readonly"); self.combo_filtro_categoria.grid(row=2, column=1, sticky=EW, padx=(0,10))
        ttk.Label(top_filter_frame, text="Tipo:").grid(row=2, column=2, padx=(0,5), pady=5, sticky=W)
        self.combo_filtro_tipo = ttk.Combobox(top_filter_frame, values=["Todos", "Receita", "Despesa"], state="readonly"); self.combo_filtro_tipo.grid(row=2, column=3, sticky=EW, padx=(0,10)); self.combo_filtro_tipo.set("Todos")
        ttk.Label(top_filter_frame, text="Cliente:").grid(row=3, column=0, padx=(0,5), pady=5, sticky=W)
        self.combo_filtro_cliente = ttk.Combobox(top_filter_frame, state="readonly"); self.combo_filtro_cliente.grid(row=3, column=1, sticky=EW, padx=(0,10))
        ttk.Label(top_filter_frame, text="Status Pag.:").grid(row=3, column=2, padx=(0,5), pady=5, sticky=W)
        self.combo_filtro_status = ttk.Combobox(top_filter_frame, state="readonly", values=["Todos", "Pago", "Pendente"]); self.combo_filtro_status.grid(row=3, column=3, sticky=EW, padx=(0,10)); self.combo_filtro_status.set("Todos")
        action_filter_frame = ttk.Frame(filter_frame); action_filter_frame.pack(fill=X, pady=(5,10))
        ttk.Button(action_filter_frame, text="Aplicar Filtros", command=lambda: self.controller.aplicar_filtros_e_resetar_pagina(), bootstyle="primary").pack(side=LEFT)
        ttk.Button(action_filter_frame, text="Limpar Filtros", command=lambda: self.controller.limpar_filtros(), bootstyle="secondary-outline").pack(side=LEFT, padx=10)
        ttk.Button(action_filter_frame, text="Exportar para Excel", command=lambda: self.controller.exportar_para_excel(), bootstyle="info").pack(side=LEFT)
        notebook = ttk.Notebook(parent); notebook.pack(fill=BOTH, expand=True)
        registros_tab = ttk.Frame(notebook); notebook.add(registros_tab, text='Registos Detalhados')
        self.graficos_tab = GraficosFrame(notebook); notebook.add(self.graficos_tab, text='Gráficos Visuais')
        tree_container = ttk.Frame(registros_tab); tree_container.pack(fill=BOTH, expand=True, padx=10, pady=(10,5))
        cols = ("Data", "Empresa", "Centro de Custo", "Veículo", "Categoria", "Descrição", "Tipo", "Valor", "Cliente", "Status")
        self.tree_relatorio = ttk.Treeview(tree_container, columns=cols, show="headings", bootstyle="primary")
        ys = ttk.Scrollbar(tree_container, orient=VERTICAL, command=self.tree_relatorio.yview); xs = ttk.Scrollbar(tree_container, orient=HORIZONTAL, command=self.tree_relatorio.xview)
        self.tree_relatorio.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        self.tree_relatorio.grid(row=0, column=0, sticky='nsew'); ys.grid(row=0, column=1, sticky='ns'); xs.grid(row=1, column=0, sticky='ew')
        tree_container.grid_rowconfigure(0, weight=1); tree_container.grid_columnconfigure(0, weight=1)
        for col in cols: self.tree_relatorio.heading(col, text=col)
        self.tree_relatorio.column("Valor", anchor="e", width=120)
        self.tree_relatorio.bind("<Double-1>", lambda e: self.controller.abrir_janela_edicao())
        pagination_frame = ttk.Frame(registros_tab); pagination_frame.pack(pady=(5,10))
        self.btn_anterior = ttk.Button(pagination_frame, text="< Anterior", command=lambda: self.controller.go_to_previous_page(), bootstyle="secondary"); self.btn_anterior.pack(side=LEFT, padx=5)
        self.lbl_pagination = ttk.Label(pagination_frame, textvariable=self.pagination_var); self.lbl_pagination.pack(side=LEFT, padx=5)
        self.btn_proximo = ttk.Button(pagination_frame, text="Próximo >", command=lambda: self.controller.go_to_next_page(), bootstyle="secondary"); self.btn_proximo.pack(side=LEFT, padx=5)
        ttk.Label(pagination_frame, text="Itens por pág:").pack(side=LEFT, padx=(20, 5))
        self.combo_itens_por_pagina = ttk.Combobox(pagination_frame, values=[50, 100, 200, 500], state="readonly", width=5); self.combo_itens_por_pagina.set(100); self.combo_itens_por_pagina.pack(side=LEFT)
        self.combo_itens_por_pagina.bind("<<ComboboxSelected>>", lambda e: self.controller.change_items_per_page())
        ttk.Button(registros_tab, text="Excluir Lançamento Selecionado", command=lambda: self.controller.excluir_lancamento_selecionado(), bootstyle=(DANGER, OUTLINE)).pack(pady=(5,10))

    def criar_janela_lancamento(self, titulo, centros_custo, veiculos, clientes, categorias, callback_salvar, dados_edicao=None):
        popup = ttk.Toplevel(title=titulo); popup.transient(self.root); popup.grab_set(); popup.geometry("450x600"); popup.place_window_center()
        frame = ttk.Frame(popup, padding=15); frame.pack(fill=BOTH, expand=TRUE); frame.columnconfigure(1, weight=1)
        row = 0
        ttk.Label(frame, text="Data:").grid(row=row, column=0, sticky=W, pady=5); entry_data = ttk.DateEntry(frame, dateformat='%d/%m/%Y'); entry_data.grid(row=row, column=1, sticky=EW, pady=5); row+=1
        ttk.Label(frame, text="Tipo:").grid(row=row, column=0, sticky=W, pady=5); combo_tipo = ttk.Combobox(frame, values=["Despesa", "Receita"], state='readonly'); combo_tipo.grid(row=row, column=1, sticky=EW, pady=5); row+=1
        ttk.Label(frame, text="Categoria:").grid(row=row, column=0, sticky=W, pady=5); combo_cat = ttk.Combobox(frame, values=categorias, state='readonly'); combo_cat.grid(row=row, column=1, sticky=EW, pady=5); row+=1
        ttk.Label(frame, text="Cliente:").grid(row=row, column=0, sticky=W, pady=5); combo_cliente = ttk.Combobox(frame, values=["N/A"] + clientes, state='readonly'); combo_cliente.grid(row=row, column=1, sticky=EW, pady=5); row+=1
        ttk.Label(frame, text="Centro de Custo:").grid(row=row, column=0, sticky=W, pady=5); combo_cc = ttk.Combobox(frame, values=[""] + centros_custo, state='readonly'); combo_cc.grid(row=row, column=1, sticky=EW, pady=5); row+=1
        ttk.Label(frame, text="Veículo:").grid(row=row, column=0, sticky=W, pady=5); combo_veiculo = ttk.Combobox(frame, values=["N/A"] + veiculos, state='readonly'); combo_veiculo.grid(row=row, column=1, sticky=EW, pady=5); row+=1
        ttk.Label(frame, text="Descrição:").grid(row=row, column=0, sticky=W, pady=5); entry_desc = ttk.Entry(frame); entry_desc.grid(row=row, column=1, sticky=EW, pady=5); row+=1
        ttk.Label(frame, text="Valor (R$):").grid(row=row, column=0, sticky=W, pady=5); entry_valor = ttk.Entry(frame); entry_valor.grid(row=row, column=1, sticky=EW, pady=5); row+=1
        
        frame_status = ttk.Frame(frame); frame_status.grid(row=row, column=0, columnspan=2, sticky='ew');
        ttk.Label(frame_status, text="Status Pag.:").grid(row=0, column=0, sticky=W, pady=5); combo_status = ttk.Combobox(frame_status, values=["Pago", "Pendente"], state='readonly'); combo_status.grid(row=0, column=1, sticky=EW, pady=5, padx=(4,0)); row+=1
        
        frame_combustivel = ttk.Frame(frame); frame_combustivel.grid(row=row, column=0, columnspan=2, sticky='ew')
        ttk.Label(frame_combustivel, text="Litros:").grid(row=0, column=0, sticky=W, pady=5); entry_litros = ttk.Entry(frame_combustivel); entry_litros.grid(row=0, column=1, sticky=EW, pady=5)
        ttk.Label(frame_combustivel, text="Preço/Litro:").grid(row=1, column=0, sticky=W, pady=5); entry_preco_litro = ttk.Entry(frame_combustivel); entry_preco_litro.grid(row=1, column=1, sticky=EW, pady=5)
        ttk.Label(frame_combustivel, text="Odómetro (KM):").grid(row=2, column=0, sticky=W, pady=5); entry_odometro = ttk.Entry(frame_combustivel); entry_odometro.grid(row=2, column=1, sticky=EW, pady=5)

        def toggle_fields(event=None):
            if combo_tipo.get() == "Receita": frame_status.grid()
            else: frame_status.grid_remove()
            if combo_cat.get() == "Combustível": frame_combustivel.grid()
            else: frame_combustivel.grid_remove()

        combo_tipo.bind("<<ComboboxSelected>>", toggle_fields); combo_cat.bind("<<ComboboxSelected>>", toggle_fields)

        if dados_edicao:
            try:
                data_lancamento = pd.to_datetime(dados_edicao.get('Data')); entry_data.entry.delete(0, END); entry_data.entry.insert(0, data_lancamento.strftime('%d/%m/%Y'))
                combo_tipo.set(dados_edicao.get('Tipo', 'Despesa'))
                combo_cat.set(dados_edicao.get('Categoria', ''))
                combo_cliente.set(dados_edicao.get('Cliente', 'N/A'))
                combo_cc.set(dados_edicao.get('Centro_de_Custo', ''))
                combo_veiculo.set(dados_edicao.get('Veículo', 'N/A'))
                entry_desc.insert(0, dados_edicao.get('Descrição', ''))
                entry_valor.insert(0, f"{dados_edicao.get('Valor', 0.0):.2f}")
                combo_status.set(dados_edicao.get('Status', ''))
                entry_litros.insert(0, str(dados_edicao.get('Litros', '') or ''))
                entry_preco_litro.insert(0, str(dados_edicao.get('Preco_Litro', '') or ''))
                entry_odometro.insert(0, str(dados_edicao.get('KM_Odometro', '') or ''))
                toggle_fields()
            except Exception as e: messagebox.showerror("Erro ao Carregar Dados", f"Não foi possível carregar os dados para edição.\n\nDetalhe: {e}", parent=popup)
        else:
            combo_tipo.set('Despesa'); combo_veiculo.set('N/A'); combo_cliente.set('N/A'); toggle_fields()
        
        def on_save():
            try:
                if not all([combo_cat.get(), entry_desc.get(), combo_tipo.get(), entry_valor.get()]):
                    messagebox.showwarning("Campos Vazios", "Categoria, Descrição, Tipo e Valor são obrigatórios.", parent=popup); return
                valor_float = float(entry_valor.get().replace(",", ".")); data_obj = datetime.strptime(entry_data.entry.get(), '%d/%m/%Y')
                dados = {'Data': data_obj, 'Centro_de_Custo': combo_cc.get() or None, 'Veículo': combo_veiculo.get() if combo_veiculo.get() != "N/A" else None, 'Categoria': combo_cat.get(), 'Descrição': entry_desc.get(), 'Tipo': combo_tipo.get(), 'Valor': valor_float, 'Cliente': combo_cliente.get() if combo_cliente.get() != "N/A" else None}
                if combo_tipo.get() == "Receita":
                    if not combo_status.get(): messagebox.showwarning("Campo Obrigatório", "Para receitas, o Status do Pagamento é obrigatório.", parent=popup); return
                    dados['Status'] = combo_status.get()
                else: dados['Status'] = None
                if combo_cat.get() == "Combustível":
                    try:
                        dados['Litros'] = float(entry_litros.get().replace(',', '.') or 0); dados['Preco_Litro'] = float(entry_preco_litro.get().replace(',', '.') or 0); dados['KM_Odometro'] = int(entry_odometro.get() or 0)
                    except (ValueError, TypeError): messagebox.showerror("Erro de Validação", "Litros, Preço/Litro e Odómetro devem ser números válidos.", parent=popup); return
                callback_salvar(dados); popup.destroy()
            except (ValueError, TypeError): messagebox.showerror("Erro de Validação", "Verifique se o Valor e a Data estão em formatos corretos.", parent=popup)
            except Exception as e: messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro inesperado: {e}", parent=popup)
        
        btn_salvar = ttk.Button(frame, text="Salvar", command=on_save, bootstyle="success"); btn_salvar.grid(row=row+1, column=0, columnspan=2, pady=15, ipady=5); entry_desc.focus_set()

    def abrir_janela_gerenciamento(self):
        win = ttk.Toplevel(title="Gerenciar Cadastros"); win.transient(self.root); win.grab_set(); win.geometry("300x250"); win.place_window_center()
        frame = ttk.Frame(win, padding=20); frame.pack(fill=BOTH, expand=True)
        ttk.Button(frame, text="Gerenciar Clientes", command=self.controller.abrir_janela_gerenciar_clientes).pack(fill=X, ipady=5, pady=5)
        ttk.Button(frame, text="Gerenciar Veículos", command=self.controller.abrir_janela_gerenciar_veiculos).pack(fill=X, ipady=5, pady=5)
        ttk.Button(frame, text="Gerenciar Categorias", command=self.controller.abrir_janela_gerenciar_categorias).pack(fill=X, ipady=5, pady=5)
        ttk.Button(frame, text="Gerenciar Centros de Custo", command=lambda: self.mostrar_info("Em breve!")).pack(fill=X, ipady=5, pady=5)

    def abrir_janela_gerenciar_entidade(self, titulo, lista_itens, callback_adicionar, callback_excluir):
        win = ttk.Toplevel(title=titulo); win.transient(self.root); win.grab_set(); win.geometry("400x500"); win.place_window_center()
        frame_lista = ttk.Frame(win, padding=10); frame_lista.pack(fill=BOTH, expand=True)
        listbox = Listbox(frame_lista, selectmode=SINGLE); listbox.pack(side=LEFT, fill=BOTH, expand=True)
        for item in lista_itens: listbox.insert(END, item)
        scrollbar = ttk.Scrollbar(frame_lista, orient=VERTICAL, command=listbox.yview); scrollbar.pack(side=RIGHT, fill=Y)
        listbox.config(yscrollcommand=scrollbar.set)
        frame_botoes = ttk.Frame(win, padding=10); frame_botoes.pack(fill=X)
        def on_add():
            entidade_singular = titulo.split()[-1].lower()[:-1]
            novo_item = ttk.dialogs.dialogs.Prompt.get_string(title=f"Adicionar {entidade_singular.title()}", prompt=f"Nome do novo {entidade_singular}:")
            if novo_item and novo_item.strip():
                success, message = callback_adicionar(novo_item)
                if success: listbox.insert(END, novo_item); listbox.see(END); self.set_status(message)
                else: messagebox.showerror("Erro", message, parent=win)
        def on_delete():
            selecionados = listbox.curselection()
            if not selecionados: messagebox.showwarning("Nenhum item selecionado", "Selecione um item para excluir.", parent=win); return
            item_selecionado = listbox.get(selecionados[0])
            if messagebox.askyesno("Confirmar Exclusão", f"Tem a certeza que deseja excluir '{item_selecionado}'?", parent=win):
                success, message = callback_excluir(item_selecionado)
                if success: listbox.delete(selecionados[0]); self.set_status(message)
                else: messagebox.showerror("Erro ao Excluir", message, parent=win)
        ttk.Button(frame_botoes, text="Adicionar Novo", command=on_add, bootstyle="success").pack(side=LEFT, padx=5, expand=True)
        ttk.Button(frame_botoes, text="Excluir Selecionado", command=on_delete, bootstyle="danger").pack(side=RIGHT, padx=5, expand=True)

    def get_empresa_ativa(self): return self.combo_empresa_ativa.get()
    def get_nova_empresa(self): return self.entry_nova_empresa.get()
    def get_nova_categoria(self): return self.entry_nova_categoria.get()
    def get_novo_cc(self): return self.entry_novo_cc.get()
    def get_novo_veiculo(self): return self.entry_novo_veiculo.get()
    def get_novo_cliente(self): return self.entry_novo_cliente.get()
    def get_selected_lancamento_index(self):
        focus = self.tree_relatorio.focus()
        return int(focus) if focus else None
    def get_filtros(self): return {'data_inicio': self.date_inicio.entry.get(), 'data_fim': self.date_fim.entry.get(), 'cc': self.combo_filtro_cc.get(), 'veiculo': self.combo_filtro_veiculo.get(), 'categoria': self.combo_filtro_categoria.get(), 'tipo': self.combo_filtro_tipo.get(), 'cliente': self.combo_filtro_cliente.get(), 'status': self.combo_filtro_status.get()}
    def resetar_campos_de_filtro(self):
        hoje = datetime.now(); data_inicio_default = hoje - timedelta(days=365)
        self.date_inicio.entry.delete(0, END); self.date_inicio.entry.insert(0, data_inicio_default.strftime('%d/%m/%Y'))
        self.date_fim.entry.delete(0, END); self.date_fim.entry.insert(0, hoje.strftime('%d/%m/%Y'))
        self.combo_filtro_tipo.set("Todos"); self.combo_filtro_cc.set("Todos"); self.combo_filtro_veiculo.set("Todos"); self.combo_filtro_categoria.set("Todos"); self.combo_filtro_cliente.set("Todos"); self.combo_filtro_status.set("Todos")
        self.set_status("Filtros limpos.")
    def set_status(self, message): self.status_var.set(message)
    def destruir(self): self.root.destroy()
    def atualizar_empresas_combobox(self, empresas): self.combo_empresa_ativa['values'] = empresas
    def set_empresa_ativa(self, nome_empresa): self.combo_empresa_ativa.set(nome_empresa)
    def atualizar_filtros_combobox(self, centros_custo, veiculos, clientes, categorias):
        self.combo_filtro_cc['values'] = ["Todos"] + centros_custo; self.combo_filtro_cc.set("Todos")
        self.combo_filtro_veiculo['values'] = ["Todos", "N/A"] + veiculos; self.combo_filtro_veiculo.set("Todos")
        self.combo_filtro_cliente['values'] = ["Todos", "N/A"] + clientes; self.combo_filtro_cliente.set("Todos")
        self.combo_filtro_categoria['values'] = ["Todos"] + categorias; self.combo_filtro_categoria.set("Todos")
    def atualizar_treeview_lancamentos(self, dataframe):
        for i in self.tree_relatorio.get_children(): self.tree_relatorio.delete(i)
        if dataframe is None: return
        df_display = dataframe.rename(columns={"Centro_de_Custo": "Centro de Custo"})
        for index, row in df_display.iterrows():
            valor_str = f"R$ {float(row.get('Valor', 0)):,.2f}"
            cliente_str = row.get("Cliente") or "N/A"
            status_str = row.get("Status") or "N/A"
            if row.get("Tipo") == "Despesa": status_str = "N/A"
            valores_linha = (row['Data'].strftime('%d/%m/%Y'), row.get("Empresa", ""), row.get("Centro de Custo", ""), row.get("Veículo", ""), row.get("Categoria", ""), row.get("Descrição", ""), row.get("Tipo", ""), valor_str, cliente_str, status_str)
            self.tree_relatorio.insert("", "end", iid=index, values=valores_linha)
    def atualizar_resumo_financeiro(self, df):
        if df.empty: total_receitas, total_despesas, saldo = 0, 0, 0
        else:
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
            total_receitas = df[df['Tipo'] == 'Receita']['Valor'].sum(); total_despesas = df[df['Tipo'] == 'Despesa']['Valor'].sum(); saldo = total_receitas - total_despesas
        self.total_receitas_var.set(f"R$ {total_receitas:,.2f}"); self.total_despesas_var.set(f"R$ {total_despesas:,.2f}"); self.saldo_final_var.set(f"R$ {saldo:,.2f}")
        if saldo > 0: self.label_saldo.config(bootstyle="success")
        elif saldo < 0: self.label_saldo.config(bootstyle="danger")
        else: self.label_saldo.config(bootstyle="default")
    def mostrar_info(self, msg): messagebox.showinfo("Informação", msg, parent=self.root)
    def confirmar_acao(self, titulo, msg): return messagebox.askyesno(titulo, msg, parent=self.root)
    def atualizar_graficos(self, dataframe): self.graficos_tab.atualizar_todos_os_graficos(dataframe)
    def update_pagination_controls(self, current_page, total_pages):
        self.pagination_var.set(f"Página {current_page} de {total_pages}")
        self.btn_anterior.config(state="normal" if current_page > 1 else "disabled")
        self.btn_proximo.config(state="normal" if current_page < total_pages else "disabled")