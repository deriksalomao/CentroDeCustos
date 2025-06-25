# app/ui/app_principal.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, END
from datetime import datetime
import traceback
import pandas as pd

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
        self.root.title("Sistema de Gestão Financeira Multi-Empresa")
        self.root.geometry("1400x800")
        try: self.root.state('zoomed')
        except: pass
        self._setup_styles()
        self.total_receitas_var = ttk.StringVar(value="R$ 0.00")
        self.total_despesas_var = ttk.StringVar(value="R$ 0.00")
        self.saldo_final_var = ttk.StringVar(value="R$ 0.00")
        self.status_var = ttk.StringVar(value="Pronto.")
        self.model = DataManager()
        self.controller = AppController(self.model, self)
        self.criar_widgets()
        self.controller.iniciar_app()
        self.root.protocol("WM_DELETE_WINDOW", self.controller.ao_fechar)

    def _setup_styles(self):
        style = ttk.Style.get_instance()
        fonte_global = ("Segoe UI", 10)
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
        frame_empresa_ativa = ttk.LabelFrame(parent, text="Empresa Ativa", padding=10); frame_empresa_ativa.pack(fill=X, pady=(0, 10))
        self.combo_empresa_ativa = ttk.Combobox(frame_empresa_ativa, state="readonly"); self.combo_empresa_ativa.pack(fill=X); self.combo_empresa_ativa.bind("<<ComboboxSelected>>", self.controller.on_empresa_selecionada)
        frame_acoes = ttk.LabelFrame(parent, text="Ações", padding=10); frame_acoes.pack(fill=X, pady=(0, 10))
        ttk.Button(frame_acoes, text="Adicionar Novo Lançamento", command=self.controller.abrir_janela_novo_lancamento, bootstyle="success").pack(fill=X, ipady=5)
        frame_gestao = ttk.LabelFrame(parent, text="Adicionar Entidades", padding=10); frame_gestao.pack(fill=X, pady=(0, 10))
        self.entry_nova_empresa = PlaceholderEntry(frame_gestao, placeholder="Nova Empresa"); self.entry_nova_empresa.pack(fill=X, pady=(0,5))
        ttk.Button(frame_gestao, text="Adicionar Empresa", command=self.controller.adicionar_empresa, bootstyle="outline-primary").pack(fill=X, pady=(0,10))
        self.entry_nova_categoria = PlaceholderEntry(frame_gestao, placeholder="Nova Categoria"); self.entry_nova_categoria.pack(fill=X, pady=(0,5))
        ttk.Button(frame_gestao, text="Adicionar Categoria", command=self.controller.adicionar_categoria, bootstyle="outline-primary").pack(fill=X, pady=(0,10))
        self.entry_novo_cc = PlaceholderEntry(frame_gestao, placeholder="Novo Centro de Custo"); self.entry_novo_cc.pack(fill=X, pady=(0,5))
        ttk.Button(frame_gestao, text="Adicionar Centro de Custo", command=self.controller.adicionar_centro_custo, bootstyle="outline-primary").pack(fill=X)
        frame_resumo = ttk.LabelFrame(parent, text="Resumo Financeiro", padding=10); frame_resumo.pack(fill=X, pady=(0, 10), side=BOTTOM); frame_resumo.columnconfigure(1, weight=1)
        ttk.Label(frame_resumo, text="Receitas:", font="-weight bold").grid(row=0, column=0, sticky=W); ttk.Label(frame_resumo, textvariable=self.total_receitas_var, bootstyle="success").grid(row=0, column=1, sticky=E)
        ttk.Label(frame_resumo, text="Despesas:", font="-weight bold").grid(row=1, column=0, sticky=W); ttk.Label(frame_resumo, textvariable=self.total_despesas_var, bootstyle="danger").grid(row=1, column=1, sticky=E)
        ttk.Label(frame_resumo, text="Saldo:", font="-weight bold -size 12").grid(row=2, column=0, sticky=W, pady=(10, 0))
        self.label_saldo = ttk.Label(frame_resumo, textvariable=self.saldo_final_var, font="-weight bold -size 12"); self.label_saldo.grid(row=2, column=1, sticky=E, pady=(10, 0))
        frame_ferramentas = ttk.LabelFrame(parent, text="Ferramentas", padding=10); frame_ferramentas.pack(fill="x", pady=15, side=BOTTOM)
        ttk.Button(frame_ferramentas, text="Gerar Dados de Teste", command=self.controller.gerar_dados_teste, bootstyle=(WARNING, OUTLINE)).pack(fill='x')

    def criar_painel_direito(self, parent):
        filter_frame = ttk.LabelFrame(parent, text="Filtros", padding=10)
        filter_frame.pack(fill=X, pady=(0, 10))
        top_filter_frame = ttk.Frame(filter_frame)
        top_filter_frame.pack(fill=X, pady=(0,10))
        top_filter_frame.columnconfigure((1,3,5), weight=1)
        ttk.Label(top_filter_frame, text="De:").grid(row=0, column=0, padx=(0,5), pady=5, sticky=W)
        self.date_inicio = ttk.DateEntry(top_filter_frame, dateformat='%d/%m/%Y')
        self.date_inicio.grid(row=0, column=1, sticky=EW, padx=(0,10))
        ttk.Label(top_filter_frame, text="Até:").grid(row=0, column=2, padx=(0,5), pady=5, sticky=W)
        self.date_fim = ttk.DateEntry(top_filter_frame, dateformat='%d/%m/%Y')
        self.date_fim.grid(row=0, column=3, sticky=EW, padx=(0,10))
        ttk.Label(top_filter_frame, text="Tipo:").grid(row=0, column=4, padx=(0,5), pady=5, sticky=W)
        self.combo_filtro_tipo = ttk.Combobox(top_filter_frame, values=["Todos", "Receita", "Despesa"], state="readonly")
        self.combo_filtro_tipo.grid(row=0, column=5, sticky=EW)
        self.combo_filtro_tipo.set("Todos")
        ttk.Label(top_filter_frame, text="Centro de Custo:").grid(row=1, column=0, padx=(0,5), pady=5, sticky=W)
        self.combo_filtro_cc = ttk.Combobox(top_filter_frame, state="readonly")
        self.combo_filtro_cc.grid(row=1, column=1, sticky=EW, padx=(0,10))
        ttk.Label(top_filter_frame, text="Categoria:").grid(row=1, column=2, padx=(0,5), pady=5, sticky=W)
        self.combo_filtro_categoria = ttk.Combobox(top_filter_frame, state="readonly")
        self.combo_filtro_categoria.grid(row=1, column=3, columnspan=3, sticky=EW)
        action_filter_frame = ttk.Frame(filter_frame)
        action_filter_frame.pack(fill=X, pady=(5,10))
        ttk.Button(action_filter_frame, text="Aplicar Filtros", command=self.controller.atualizar_relatorio_e_resumo, bootstyle="primary").pack(side=LEFT)
        ttk.Button(action_filter_frame, text="Limpar Filtros", command=self.controller.limpar_filtros, bootstyle="secondary-outline").pack(side=LEFT, padx=10)
        
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=BOTH, expand=True)

        # --- Aba de Registros ---
        registros_tab = ttk.Frame(notebook)
        notebook.add(registros_tab, text='Registros Detalhados')
        
        # --- Container para a tabela e scrollbars ---
        tree_container = ttk.Frame(registros_tab)
        tree_container.pack(fill=BOTH, expand=True, padx=10, pady=(10,5))
        
        cols = ("Data", "Empresa", "Centro de Custo", "Categoria", "Descrição", "Tipo", "Valor")
        self.tree_relatorio = ttk.Treeview(tree_container, columns=cols, show="headings", bootstyle="primary")
        ys = ttk.Scrollbar(tree_container, orient=VERTICAL, command=self.tree_relatorio.yview)
        xs = ttk.Scrollbar(tree_container, orient=HORIZONTAL, command=self.tree_relatorio.xview)
        self.tree_relatorio.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        
        # Layout correto da tabela e scrollbars dentro do container
        self.tree_relatorio.grid(row=0, column=0, sticky='nsew')
        ys.grid(row=0, column=1, sticky='ns')
        xs.grid(row=1, column=0, sticky='ew')
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        for col in cols: self.tree_relatorio.heading(col, text=col)
        self.tree_relatorio.bind("<Double-1>", self.controller.abrir_janela_edicao)
        
        # Botão de exclusão abaixo do container da tabela
        ttk.Button(registros_tab, text="Excluir Lançamento Selecionado", command=self.controller.excluir_lancamento_selecionado, bootstyle=(DANGER, OUTLINE)).pack(pady=(5,10))
        
        # --- Aba de Gráficos ---
        self.graficos_tab = GraficosFrame(notebook)
        notebook.add(self.graficos_tab, text='Gráficos Visuais')

    def criar_janela_lancamento(self, titulo, centros_custo, categorias, callback_salvar, dados_edicao=None):
        popup = ttk.Toplevel(title=titulo); popup.transient(self.root); popup.grab_set(); popup.geometry("450x360"); popup.place_window_center()
        frame = ttk.Frame(popup, padding=15); frame.pack(fill=BOTH, expand=TRUE); frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text="Data:").grid(row=0, column=0, sticky=W, pady=5)
        entry_data = ttk.DateEntry(frame, dateformat='%d/%m/%Y'); entry_data.grid(row=0, column=1, sticky=EW, pady=5)
        ttk.Label(frame, text="Centro de Custo:").grid(row=1, column=0, sticky=W, pady=5)
        combo_cc = ttk.Combobox(frame, values=centros_custo, state='readonly'); combo_cc.grid(row=1, column=1, sticky=EW, pady=5)
        ttk.Label(frame, text="Categoria:").grid(row=2, column=0, sticky=W, pady=5)
        combo_cat = ttk.Combobox(frame, values=categorias, state='readonly'); combo_cat.grid(row=2, column=1, sticky=EW, pady=5)
        ttk.Label(frame, text="Descrição:").grid(row=3, column=0, sticky=W, pady=5)
        entry_desc = ttk.Entry(frame); entry_desc.grid(row=3, column=1, sticky=EW, pady=5)
        ttk.Label(frame, text="Tipo:").grid(row=4, column=0, sticky=W, pady=5)
        combo_tipo = ttk.Combobox(frame, values=["Receita", "Despesa"], state='readonly'); combo_tipo.grid(row=4, column=1, sticky=EW, pady=5)
        ttk.Label(frame, text="Valor (R$):").grid(row=5, column=0, sticky=W, pady=5)
        entry_valor = ttk.Entry(frame); entry_valor.grid(row=5, column=1, sticky=EW, pady=5)
        if dados_edicao is not None:
            try:
                data_lancamento = dados_edicao.get('Data')
                if data_lancamento and pd.notna(data_lancamento):
                    data_str = data_lancamento.strftime('%d/%m/%Y'); entry_data.entry.delete(0, END); entry_data.entry.insert(0, data_str)
                combo_cc.set(dados_edicao.get('Centro de Custo', '')); combo_cat.set(dados_edicao.get('Categoria', '')); entry_desc.insert(0, dados_edicao.get('Descrição', '')); combo_tipo.set(dados_edicao.get('Tipo', '')); entry_valor.insert(0, f"{dados_edicao.get('Valor', 0.0):.2f}")
            except Exception as e:
                messagebox.showerror("Erro ao Carregar Dados", f"Não foi possível carregar os dados para edição.\n\nDetalhe: {e}", parent=popup); traceback.print_exc()
        else:
            combo_tipo.set('Despesa')
        def on_save():
            try:
                if not all([combo_cc.get(), combo_cat.get(), entry_desc.get(), combo_tipo.get(), entry_valor.get()]):
                    messagebox.showwarning("Campos Vazios", "Todos os campos devem ser preenchidos.", parent=popup); return
                valor_float = float(entry_valor.get().replace(",", ".")); data_str = entry_data.entry.get(); data_obj = datetime.strptime(data_str, '%d/%m/%Y')
                dados = {'Data': data_obj, 'Centro de Custo': combo_cc.get(), 'Categoria': combo_cat.get(), 'Descrição': entry_desc.get(), 'Tipo': combo_tipo.get(), 'Valor': valor_float}
                callback_salvar(dados); popup.destroy()
            except ValueError:
                messagebox.showerror("Erro de Validação", "O formato do 'Valor' é inválido.", parent=popup)
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro: {e}", parent=popup); traceback.print_exc()
        btn_salvar = ttk.Button(frame, text="Salvar", command=on_save, bootstyle="success"); btn_salvar.grid(row=6, column=0, columnspan=2, pady=15, ipady=5); entry_desc.focus_set()

    def get_empresa_ativa(self): return self.combo_empresa_ativa.get()
    def get_nova_empresa(self): return self.entry_nova_empresa.get()
    def get_nova_categoria(self): return self.entry_nova_categoria.get()
    def get_novo_cc(self): return self.entry_novo_cc.get()
    def get_selected_lancamento_index(self):
        focus = self.tree_relatorio.focus()
        return int(focus) if focus else None
    def get_filtros(self): return {'data_inicio': self.date_inicio.entry.get(), 'data_fim': self.date_fim.entry.get(), 'cc': self.combo_filtro_cc.get(), 'categoria': self.combo_filtro_categoria.get(), 'tipo': self.combo_filtro_tipo.get()}
    def resetar_campos_de_filtro(self):
        hoje = datetime.now(); data_inicio_str = hoje.replace(day=1).strftime('%d/%m/%Y'); self.date_inicio.entry.delete(0, END); self.date_inicio.entry.insert(0, data_inicio_str)
        data_fim_str = hoje.strftime('%d/%m/%Y'); self.date_fim.entry.delete(0, END); self.date_fim.entry.insert(0, data_fim_str)
        self.combo_filtro_tipo.set("Todos"); self.combo_filtro_cc.set("Todos"); self.combo_filtro_categoria.set("Todos"); self.set_status("Filtros limpos.")
    def set_status(self, message): self.status_var.set(message)
    def destruir(self): self.root.destroy()
    def atualizar_empresas_combobox(self, empresas): self.combo_empresa_ativa['values'] = empresas
    def set_empresa_ativa(self, nome_empresa): self.combo_empresa_ativa.set(nome_empresa)
    def atualizar_filtros_combobox(self, centros_custo, categorias):
        self.combo_filtro_cc['values'] = centros_custo; self.combo_filtro_cc.set("Todos")
        self.combo_filtro_categoria['values'] = categorias; self.combo_filtro_categoria.set("Todos")
    def atualizar_treeview_lancamentos(self, dataframe):
        for i in self.tree_relatorio.get_children(): self.tree_relatorio.delete(i)
        if dataframe is None: return
        for index, row in dataframe.iterrows():
            data_str = row['Data'].strftime('%d/%m/%Y'); valor_str = f"R$ {float(row['Valor']):,.2f}"
            self.tree_relatorio.insert("", "end", iid=index, values=(data_str, row["Empresa"], row["Centro de Custo"], row["Categoria"], row["Descrição"], row["Tipo"], valor_str))
    def atualizar_resumo_financeiro(self, df):
        if df.empty: total_receitas, total_despesas, saldo = 0, 0, 0
        else:
            total_receitas = df[df['Tipo'] == 'Receita']['Valor'].sum(); total_despesas = df[df['Tipo'] == 'Despesa']['Valor'].sum(); saldo = total_receitas - total_despesas
        self.total_receitas_var.set(f"R$ {total_receitas:,.2f}"); self.total_despesas_var.set(f"R$ {total_despesas:,.2f}"); self.saldo_final_var.set(f"R$ {saldo:,.2f}")
        if saldo > 0: self.label_saldo.config(bootstyle="success")
        elif saldo < 0: self.label_saldo.config(bootstyle="danger")
        else: self.label_saldo.config(bootstyle="default")
    def mostrar_info(self, msg): messagebox.showinfo("Informação", msg, parent=self.root)
    def confirmar_acao(self, titulo, msg): return messagebox.askyesno(titulo, msg, parent=self.root)
    def atualizar_graficos(self, dataframe): self.graficos_tab.atualizar_grafico_despesas(dataframe)