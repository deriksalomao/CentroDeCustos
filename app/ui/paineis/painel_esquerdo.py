# app/ui/panels/left_panel.py
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry

class PainelEsquerdo(ttk.Frame):
    def __init__(self, parent_frame, controller):
        super().__init__(parent_frame)
        self.controller = controller 
        self._create_widgets()

    def _create_widgets(self):

        empresa_frame = ttk.LabelFrame(self, text="Empresa Ativa")
        empresa_frame.pack(pady=10, padx=10, fill='x')
        self.combo_empresa_ativa = ttk.Combobox(empresa_frame, state="readonly")
        self.combo_empresa_ativa.pack(pady=5, padx=5, fill='x')
        # A ligação do comando <<ComboboxSelected>> será feita no controller
        # ou no AppPrincipal após a instanciação do PainelEsquerdo.

        cadastros_frame = ttk.LabelFrame(self, text="Cadastros Rápidos")
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
        
        resumo_frame = ttk.LabelFrame(self, text="Resumo Financeiro")
        resumo_frame.pack(pady=10, padx=10, fill='x')
        self.lbl_receitas = ttk.Label(resumo_frame, text="Receitas: R$ 0.00")
        self.lbl_receitas.pack(anchor='w')
        self.lbl_despesas = ttk.Label(resumo_frame, text="Despesas: R$ 0.00")
        self.lbl_despesas.pack(anchor='w')
        self.lbl_saldo = ttk.Label(resumo_frame, text="Saldo: R$ 0.00")
        self.lbl_saldo.pack(anchor='w')

    # Métodos para atualizar os labels do resumo financeiro
    # Eles seriam chamados de fora (pelo controller ou AppPrincipal)
    def update_financial_summary(self, receitas, despesas, saldo):
        self.lbl_receitas.config(
            text=f"Receitas: R$ {receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            foreground="green"
        )
        self.lbl_despesas.config(
            text=f"Despesas: R$ {despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            foreground="red"
        )
        saldo_text = f"Saldo: R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        if saldo > 0:
            self.lbl_saldo.config(text=saldo_text, foreground="green")
        elif saldo < 0:
            self.lbl_saldo.config(text=saldo_text, foreground="red")
        else:
            self.lbl_saldo.config(text=saldo_text, foreground="black")

    # Métodos para atualizar o dropdown de empresa, ou para obter valores das entradas
    def update_empresa_dropdown(self, empresas, set_default=False):
        self.combo_empresa_ativa['values'] = empresas
        if set_default and empresas:
            self.combo_empresa_ativa.set(empresas[0])
    
    def get_empresa_ativa(self):
        return self.combo_empresa_ativa.get()

    def get_add_cliente_value(self):
        return self.entry_novo_cliente.get()
    # Adicione getters para os outros campos de adição rápida conforme necessário