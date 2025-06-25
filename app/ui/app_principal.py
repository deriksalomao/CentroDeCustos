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
        self.root.title("Sistema de Gestão para Transportadora")
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
        self.combo_empresa_ativa = ttk.Combobox(frame_empresa_ativa, state="readonly"); self.combo_empresa_ativa.pack(fill=X); self.combo_empresa_ativa.bind("<<ComboboxSelected>>", self.controller.on_empresa_selecionada)
        frame_acoes = ttk.LabelFrame(parent, text="Ações", padding=10); frame_acoes.pack(fill=X, pady=(0, 10))
        ttk.Button(frame_acoes, text="Adicionar Novo Lançamento", command=self.controller.abrir_janela_novo_lancamento, bootstyle="success").pack(fill=X, ipady=5)
        
        frame_gestao = ttk.LabelFrame(parent, text="Cadastros", padding=10); frame_gestao.pack(fill=X, pady=(0, 10))
        
        self.entry_novo_cliente = PlaceholderEntry(frame_gestao, placeholder="Novo Cliente"); self.entry_novo_cliente.pack(fill=X, pady=(0,5))
        ttk.Button(frame_gestao, text="Adicionar Cliente", command=self.controller.adicionar_cliente, bootstyle="outline-primary").pack(fill=X, pady=(0,10))

        self.entry_novo_veiculo = PlaceholderEntry(frame_gestao, placeholder="Novo Veículo (Placa)"); self.entry_novo_veiculo.pack(fill=X, pady=(0,5))
        ttk.Button(frame_gestao, text="Adicionar Veículo", command=self.controller.adicionar_veiculo, bootstyle="outline-primary").pack(fill=X, pady=(0,10))
        
        self.entry_novo_cc = PlaceholderEntry(frame_gestao, placeholder="Novo Centro de Custo"); self.entry_novo_cc.pack(fill=X, pady=(0,5))
        ttk.Button(frame_gestao, text="Adicionar Centro de Custo", command=self.controller.adicionar_centro_custo, bootstyle="outline-primary").pack(fill=X, pady=(0,10))
        
        self.entry_nova_categoria = PlaceholderEntry(frame_gestao, placeholder="Nova Categoria (Ex: Pedágio)"); self.entry_nova_categoria.pack(fill=X, pady=(0,5))
        ttk.Button(frame_gestao, text="Adicionar Categoria", command=self.controller.adicionar_categoria, bootstyle="outline-primary").pack(fill=X, pady=(0,10))

        self.entry_nova_empresa = PlaceholderEntry(frame_gestao, placeholder="Nova Empresa (Matriz/Filial)"); self.entry_nova_empresa.pack(fill=X, pady=(0,5))
        ttk.Button(frame_gestao, text="Adicionar Empresa", command=self.controller.adicionar_empresa, bootstyle="outline-primary").pack(fill=X)
        
        frame_resumo = ttk.LabelFrame(parent, text="Resumo Financeiro", padding=10); frame_resumo.pack(fill=X, pady=(0, 10), side=BOTTOM); frame_resumo.columnconfigure(1, weight=1)
        ttk.Label(frame_resumo, text="Receitas:", font="-weight bold").grid(row=0, column=0, sticky=W); ttk.Label(frame_resumo, textvariable=self.total_receitas_var, bootstyle="success").grid(row=0, column=1, sticky=E)
        ttk.Label(frame_resumo, text="Despesas:", font="-weight bold").grid(row=1, column=0, sticky=W); ttk.Label(frame_resumo, textvariable=self.total_despesas_var, bootstyle="danger").grid(row=1, column=1, sticky=E)
        ttk.Label(frame_resumo, text="Saldo:", font="-weight bold -size 12").grid(row=2, column=0, sticky=W, pady=(10, 0))
        self.label_saldo = ttk.Label(frame_resumo, textvariable=self.saldo_final_var, font="-weight bold -size 12"); self.label_saldo.grid(row=2, column=1, sticky=E, pady=(10, 0))
        frame_ferramentas = ttk.LabelFrame(parent, text="Ferramentas", padding=10); frame_ferramentas.pack(fill="x", pady=15, side=BOTTOM)
        ttk.Button(frame_ferramentas, text="Gerar Dados de Teste", command=self.controller.gerar_dados_teste, bootstyle=(WARNING, OUTLINE)).pack(fill='x')

    def criar_painel_direito(self, parent):
        filter_frame = ttk.LabelFrame(parent, text="Filtros e Ações", padding=10); filter_frame.pack(fill=X, pady=(0, 10))
        top_filter_frame = ttk.Frame(filter_frame); top_filter_frame.pack(fill=X, pady=(0,10)); top_filter_frame.columnconfigure((1,3,5), weight=1)
        ttk.Label(top_filter_frame, text="De:").grid(row=0, column=0, padx=(0,5), pady=5, sticky=W)
        self.date_inicio = ttk.DateEntry(top_filter_frame, dateformat='%d/%m/%Y'); self.date_inicio.grid(row=0, column=1, sticky=EW, padx=(0,10))
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
        ttk.Button(action_filter_frame, text="Aplicar Filtros", command=self.controller.atualizar_relatorio_e_resumo, bootstyle="primary").pack(side=LEFT)
        ttk.Button(action_filter_frame, text="Limpar Filtros", command=self.controller.limpar_filtros, bootstyle="secondary-outline").pack(side=LEFT, padx=10)
        ttk.Button(action_filter_frame, text="Exportar para Excel", command=self.controller.exportar_para_excel, bootstyle="info").pack(side=LEFT)
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
        self.tree_relatorio.column("Data", anchor="center", width=90)
        self.tree_relatorio.column("Tipo", anchor="center", width=80)
        self.tree_relatorio.column("Status", anchor="center", width=80)

        self.tree_relatorio.bind("<Double-1>", self.controller.abrir_janela_edicao)
        
        ttk.Button(registros_tab, text="Excluir Lançamento Selecionado", command=self.controller.excluir_lancamento_selecionado, bootstyle=(DANGER, OUTLINE)).pack(pady=(5,10))

    def criar_janela_lancamento(self, titulo, centros_custo, veiculos, clientes, categorias, callback_salvar, dados_edicao=None):
        popup = ttk.Toplevel(title=titulo); popup.transient(self.root); popup.grab_set(); popup.geometry("450x600"); popup.place_window_center()
        frame = ttk.Frame(popup, padding=15); frame.pack(fill=BOTH, expand=TRUE); frame.columnconfigure(1, weight=1)
        
        row_idx = 0
        ttk.Label(frame, text="Data:").grid(row=row_idx, column=0, sticky=W, pady=5); 
        entry_data = ttk.DateEntry(frame, dateformat='%d/%m/%Y'); entry_data.grid(row=row_idx, column=1, sticky=EW, pady=5); row_idx += 1
        
        ttk.Label(frame, text="Tipo:").grid(row=row_idx, column=0, sticky=W, pady=5)
        combo_tipo = ttk.Combobox(frame, values=["Despesa", "Receita"], state='readonly'); combo_tipo.grid(row=row_idx, column=1, sticky=EW, pady=5); row_idx += 1
        
        ttk.Label(frame, text="Categoria:").grid(row=row_idx, column=0, sticky=W, pady=5);
        combo_cat = ttk.Combobox(frame, values=categorias, state='readonly'); combo_cat.grid(row=row_idx, column=1, sticky=EW, pady=5); row_idx += 1

        ttk.Label(frame, text="Centro de Custo:").grid(row=row_idx, column=0, sticky=W, pady=5)
        combo_cc = ttk.Combobox(frame, values=centros_custo, state='readonly'); combo_cc.grid(row=row_idx, column=1, sticky=EW, pady=5); row_idx += 1
        
        ttk.Label(frame, text="Veículo:").grid(row=row_idx, column=0, sticky=W, pady=5)
        combo_veiculo = ttk.Combobox(frame, values=veiculos, state='readonly'); combo_veiculo.grid(row=row_idx, column=1, sticky=EW, pady=5); row_idx += 1

        ttk.Label(frame, text="Descrição:").grid(row=row_idx, column=0, sticky=W, pady=5)
        entry_desc = ttk.Entry(frame); entry_desc.grid(row=row_idx, column=1, sticky=EW, pady=5); row_idx += 1

        ttk.Label(frame, text="Valor (R$):").grid(row=row_idx, column=0, sticky=W, pady=5)
        entry_valor = ttk.Entry(frame); entry_valor.grid(row=row_idx, column=1, sticky=EW, pady=5); row_idx += 1
        
        frame_receita = ttk.Frame(frame); frame_receita.grid(row=row_idx, column=0, columnspan=2, sticky='ew')
        ttk.Label(frame_receita, text="Cliente:").grid(row=0, column=0, sticky=W, pady=5)
        combo_cliente = ttk.Combobox(frame_receita, values=clientes, state='readonly'); combo_cliente.grid(row=0, column=1, sticky=EW, pady=5)
        ttk.Label(frame_receita, text="Status Pag.:").grid(row=1, column=0, sticky=W, pady=5)
        combo_status = ttk.Combobox(frame_receita, values=["Pago", "Pendente"], state='readonly'); combo_status.grid(row=1, column=1, sticky=EW, pady=5)

        frame_combustivel = ttk.Frame(frame); frame_combustivel.grid(row=row_idx + 1, column=0, columnspan=2, sticky='ew')
        ttk.Label(frame_combustivel, text="Litros:").grid(row=0, column=0, sticky=W, pady=5)
        entry_litros = ttk.Entry(frame_combustivel); entry_litros.grid(row=0, column=1, sticky=EW, pady=5)
        ttk.Label(frame_combustivel, text="Preço/Litro:").grid(row=1, column=0, sticky=W, pady=5)
        entry_preco_litro = ttk.Entry(frame_combustivel); entry_preco_litro.grid(row=1, column=1, sticky=EW, pady=5)
        ttk.Label(frame_combustivel, text="Odómetro (KM):").grid(row=2, column=0, sticky=W, pady=5)
        entry_odometro = ttk.Entry(frame_combustivel); entry_odometro.grid(row=2, column=1, sticky=EW, pady=5)

        def toggle_fields(event=None):
            tipo = combo_tipo.get(); categoria = combo_cat.get()
            if tipo == "Receita": frame_receita.grid()
            else: frame_receita.grid_remove()
            if categoria == "Combustível": frame_combustivel.grid()
            else: frame_combustivel.grid_remove()

        combo_tipo.bind("<<ComboboxSelected>>", toggle_fields)
        combo_cat.bind("<<ComboboxSelected>>", toggle_fields)

        if dados_edicao is not None:
            try:
                data_lancamento = dados_edicao.get('Data');
                if data_lancamento and pd.notna(data_lancamento):
                    data_str = data_lancamento.strftime('%d/%m/%Y'); entry_data.entry.delete(0, END); entry_data.entry.insert(0, data_str)
                combo_tipo.set(dados_edicao.get('Tipo', 'Despesa'))
                combo_cat.set(dados_edicao.get('Categoria', ''))
                combo_cc.set(dados_edicao.get('Centro de Custo', ''))
                combo_veiculo.set(dados_edicao.get('Veículo', 'N/A'))
                entry_desc.insert(0, dados_edicao.get('Descrição', ''))
                entry_valor.insert(0, f"{dados_edicao.get('Valor', 0.0):.2f}")
                combo_cliente.set(dados_edicao.get('Cliente', ''))
                combo_status.set(dados_edicao.get('Status', ''))
                entry_litros.insert(0, str(dados_edicao.get('Litros', '')))
                entry_preco_litro.insert(0, str(dados_edicao.get('Preco_Litro', '')))
                entry_odometro.insert(0, str(dados_edicao.get('KM_Odometro', '')))
                toggle_fields()
            except Exception as e:
                messagebox.showerror("Erro ao Carregar Dados", f"Não foi possível carregar os dados para edição.\n\nDetalhe: {e}", parent=popup); traceback.print_exc()
        else:
            combo_tipo.set('Despesa'); combo_veiculo.set('N/A'); toggle_fields()
        
        def on_save():
            try:
                if not all([combo_cat.get(), combo_cc.get(), entry_desc.get(), combo_tipo.get(), entry_valor.get()]):
                    messagebox.showwarning("Campos Vazios", "Campos essenciais devem ser preenchidos.", parent=popup); return
                valor_float = float(entry_valor.get().replace(",", ".")); data_str = entry_data.entry.get(); data_obj = datetime.strptime(data_str, '%d/%m/%Y')
                
                dados = {'Data': data_obj, 'Centro de Custo': combo_cc.get(), 'Veículo': combo_veiculo.get(), 'Categoria': combo_cat.get(), 'Descrição': entry_desc.get(), 'Tipo': combo_tipo.get(), 'Valor': valor_float}
                
                if combo_tipo.get() == "Receita":
                    if not combo_cliente.get() or not combo_status.get():
                        messagebox.showwarning("Campos de Receita", "Para receitas, Cliente e Status são obrigatórios.", parent=popup); return
                    dados['Cliente'] = combo_cliente.get(); dados['Status'] = combo_status.get()
                
                if combo_cat.get() == "Combustível":
                    dados['Litros'] = float(entry_litros.get() or 0)
                    dados['Preco_Litro'] = float(entry_preco_litro.get() or 0)
                    dados['KM_Odometro'] = int(entry_odometro.get() or 0)

                callback_salvar(dados); popup.destroy()
            except (ValueError, TypeError):
                messagebox.showerror("Erro de Validação", "Verifique se os valores numéricos (Valor, Litros, etc.) estão corretos.", parent=popup)
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro: {e}", parent=popup); traceback.print_exc()
        
        btn_salvar = ttk.Button(frame, text="Salvar", command=on_save, bootstyle="success"); btn_salvar.grid(row=10, column=0, columnspan=2, pady=15, ipady=5); entry_desc.focus_set()

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
        hoje = datetime.now(); data_inicio_str = hoje.replace(day=1).strftime('%d/%m/%Y'); self.date_inicio.entry.delete(0, END); self.date_inicio.entry.insert(0, data_inicio_str)
        data_fim_str = hoje.strftime('%d/%m/%Y'); self.date_fim.entry.delete(0, END); self.date_fim.entry.insert(0, data_fim_str)
        self.combo_filtro_tipo.set("Todos"); self.combo_filtro_cc.set("Todos"); self.combo_filtro_veiculo.set("Todos"); self.combo_filtro_categoria.set("Todos"); self.combo_filtro_cliente.set("Todos"); self.combo_filtro_status.set("Todos")
        self.set_status("Filtros limpos.")
    
    def set_status(self, message): self.status_var.set(message)
    def destruir(self): self.root.destroy()
    def atualizar_empresas_combobox(self, empresas): self.combo_empresa_ativa['values'] = empresas
    def set_empresa_ativa(self, nome_empresa): self.combo_empresa_ativa.set(nome_empresa)
    
    def atualizar_filtros_combobox(self, centros_custo, veiculos, clientes, categorias):
        self.combo_filtro_cc['values'] = centros_custo; self.combo_filtro_cc.set("Todos")
        self.combo_filtro_veiculo['values'] = veiculos; self.combo_filtro_veiculo.set("Todos")
        self.combo_filtro_cliente['values'] = clientes; self.combo_filtro_cliente.set("Todos")
        self.combo_filtro_categoria['values'] = categorias; self.combo_filtro_categoria.set("Todos")
        
    def atualizar_treeview_lancamentos(self, dataframe):
        for i in self.tree_relatorio.get_children():
            self.tree_relatorio.delete(i)
        if dataframe is None:
            return
        for index, row in dataframe.iterrows():
            # CORREÇÃO APLICADA AQUI
            valor_str = f"R$ {float(row.get('Valor', 0)):,.2f}"
            
            cliente_str = row.get("Cliente")
            status_str = row.get("Status")
            
            # Se o valor for 'nan' ou vazio, exibe "N/A"
            if pd.isna(cliente_str) or str(cliente_str).strip() == "" or str(cliente_str).strip() == "N/A":
                 cliente_str = "N/A"
            if pd.isna(status_str) or str(status_str).strip() == "" or str(status_str).strip() == "N/A":
                status_str = "N/A"

            # Para despesas, Cliente e Status devem sempre ser N/A
            if row.get("Tipo") == "Despesa":
                cliente_str = "N/A"
                status_str = "N/A"

            valores_linha = (
                row['Data'].strftime('%d/%m/%Y'),
                row.get("Empresa", ""),
                row.get("Centro de Custo", ""),
                row.get("Veículo", ""),
                row.get("Categoria", ""),
                row.get("Descrição", ""),
                row.get("Tipo", ""),
                valor_str,
                cliente_str,
                status_str
            )
            self.tree_relatorio.insert("", "end", iid=index, values=valores_linha)
            
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
    def atualizar_graficos(self, dataframe): self.graficos_tab.atualizar_todos_os_graficos(dataframe)