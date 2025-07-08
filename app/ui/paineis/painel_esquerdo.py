import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

class PainelEsquerdo(ttk.Frame):
    def __init__(self, parent_frame, controller):
        super().__init__(parent_frame)
        self.controller = controller
        self.combo_boxes_exclusao = {}
        self._create_widgets()

    def _create_widgets(self):

        # 1. Configura a grade (grid) do PainelEsquerdo.
        #    A linha 0 (rolagem) vai se expandir. A linha 1 (resumo) terá tamanho fixo.
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # 2. Área de Rolagem na linha 0
        scroll_area = ScrolledFrame(self, autohide=True)
        # Usa .grid() para posicionar e 'nsew' para preencher todo o espaço da célula.
        scroll_area.grid(row=0, column=0, sticky='nsew')

        # 3. Frame Fixo para o Resumo Financeiro na linha 1
        resumo_main_frame = ttk.LabelFrame(self, text="Resumo Financeiro")
        # Usa .grid() e 'ew' para preencher a largura. Adiciona padding externo.
        resumo_main_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=10)

        # O conteúdo do resumo financeiro permanece o mesmo
        self.lbl_receitas = ttk.Label(resumo_main_frame, text="Receitas: R$ 0.00")
        self.lbl_receitas.pack(anchor='w', padx=5, pady=(0, 2))
        self.lbl_despesas = ttk.Label(resumo_main_frame, text="Despesas: R$ 0.00")
        self.lbl_despesas.pack(anchor='w', padx=5, pady=2)
        self.lbl_saldo = ttk.Label(resumo_main_frame, text="Saldo: R$ 0.00")
        self.lbl_saldo.pack(anchor='w', padx=5, pady=(2, 0))


        # Widgets que ficam DENTRO da 'scroll_area' (não mudam)
        empresa_frame = ttk.LabelFrame(scroll_area, text="Empresa Ativa")
        empresa_frame.pack(pady=10, padx=10, fill='x')
        self.combo_empresa_ativa = ttk.Combobox(empresa_frame, state="readonly")
        self.combo_empresa_ativa.pack(pady=5, padx=5, fill='x')

        cadastros_frame = ttk.LabelFrame(scroll_area, text="Gerenciar Cadastros")
        cadastros_frame.pack(pady=10, padx=10, fill='x')

        # --- BOTÃO ADICIONADO AQUI ---
        # Botão para abrir a gestão de cadastros completa
        self.btn_gestao_cadastros = ttk.Button(cadastros_frame, text="Abrir Gestão Completa", command=lambda: self.controller.abrir_janela_gestao_cadastros())
        self.btn_gestao_cadastros.pack(pady=10, padx=5, fill='x')
        ttk.Separator(cadastros_frame, orient='horizontal').pack(fill='x', pady=5, padx=5)
        # --- FIM DA ADIÇÃO ---

        self.entry_novo_cliente, self.combo_boxes_exclusao['Cliente'] = self._criar_secao_cadastro(cadastros_frame, "Cliente")
        self.entry_novo_veiculo, self.combo_boxes_exclusao['Veículo'] = self._criar_secao_cadastro(cadastros_frame, "Veículo")
        self.entry_novo_cc, self.combo_boxes_exclusao['Centro de Custo'] = self._criar_secao_cadastro(cadastros_frame, "Centro de Custo")
        self.entry_nova_categoria, self.combo_boxes_exclusao['Categoria'] = self._criar_secao_cadastro(cadastros_frame, "Categoria")
        self.entry_nova_empresa, self.combo_boxes_exclusao['Empresa'] = self._criar_secao_cadastro(cadastros_frame, "Empresa")


    def _criar_secao_cadastro(self, parent, nome_item):
        """Cria uma seção completa de adição e exclusão para um tipo de item."""
        frame_geral = ttk.Frame(parent)
        frame_geral.pack(fill='x', pady=5, padx=5)

        ttk.Label(frame_geral, text=f"Novo(a) {nome_item}:").pack(anchor='w')
        frame_add = ttk.Frame(frame_geral)
        frame_add.pack(fill='x', expand=True)
        
        entry_add = ttk.Entry(frame_add)
        entry_add.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        btn_add = ttk.Button(frame_add, text="Adicionar", command=lambda n=nome_item: self.controller.adicionar_item_rapido(n, self._get_entry_value(n)))
        btn_add.pack(side='left')

        ttk.Label(frame_geral, text=f"Excluir {nome_item} Existente:").pack(anchor='w', pady=(5,0))
        frame_del = ttk.Frame(frame_geral)
        frame_del.pack(fill='x', expand=True, pady=(0, 10))

        combo_del = ttk.Combobox(frame_del, state="readonly")
        combo_del.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        btn_del = ttk.Button(frame_del, text="Excluir", style="danger.TButton", command=lambda n=nome_item: self.controller.excluir_item_rapido(n, self._get_combo_value(n)))
        btn_del.pack(side='left')

        if nome_item != "Empresa":
            ttk.Separator(frame_geral, orient='horizontal').pack(fill='x', pady=5)
            
        return entry_add, combo_del

    def _get_entry_value(self, nome_item):
        if nome_item == "Cliente": return self.entry_novo_cliente.get()
        if nome_item == "Veículo": return self.entry_novo_veiculo.get()
        if nome_item == "Centro de Custo": return self.entry_novo_cc.get()
        if nome_item == "Categoria": return self.entry_nova_categoria.get()
        if nome_item == "Empresa": return self.entry_nova_empresa.get()
        return ""

    def _get_combo_value(self, nome_item):
        return self.combo_boxes_exclusao[nome_item].get()
    
    def update_financial_summary(self, receitas, despesas, saldo):
        self.lbl_receitas.config(text=f"Receitas: R$ {receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), foreground="green")
        self.lbl_despesas.config(text=f"Despesas: R$ {despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), foreground="red")
        saldo_text = f"Saldo: R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.lbl_saldo.config(text=saldo_text, foreground="green" if saldo >= 0 else "red")

    def update_empresa_dropdown(self, empresas, set_default=False):
        self.combo_empresa_ativa['values'] = empresas
        self.combo_boxes_exclusao['Empresa']['values'] = empresas
        if set_default and empresas:
            self.combo_empresa_ativa.set(empresas[0])
    
    def update_cadastro_dropdown(self, tipo_item, valores):
        if tipo_item in self.combo_boxes_exclusao:
            self.combo_boxes_exclusao[tipo_item]['values'] = valores
            self.combo_boxes_exclusao[tipo_item].set('') 

    def get_empresa_ativa(self):
        return self.combo_empresa_ativa.get()

    def set_empresa_ativa(self, nome_empresa):
        self.combo_empresa_ativa.set(nome_empresa)