# app/ui/paineis/painel_direito.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import pandas as pd
from ttkbootstrap.widgets import DateEntry
from app.ui.ui_graficos import GraficosFrame # Importe a classe dos gráficos

class PainelDireito(ttk.Frame):
    def __init__(self, frame_pai, controlador):
        super().__init__(frame_pai)
        self.controlador = controlador
        self.pack(fill=tk.BOTH, expand=True) # Este painel preenche seu frame pai

        # É importante ter acesso ao widget mestre (janela principal) para popups Toplevel
        # O master do frame_pai é a janela principal (AppPrincipal.master/root)
        self.master_app_root = frame_pai.master 

        self._criar_widgets()

    def _criar_widgets(self):
        # Botão "Adicionar Novo Lançamento"
        self.btn_novo_lancamento = ttk.Button(self, text="Adicionar Novo Lançamento", command=self._abrir_janela_novo_lancamento)
        self.btn_novo_lancamento.pack(pady=10, padx=10, anchor='w')
        
        # Frame de Filtros
        frame_filtros = ttk.LabelFrame(self, text="Filtros")
        frame_filtros.pack(pady=10, padx=10, fill='x')

        frame_filtros_topo = ttk.Frame(frame_filtros)
        frame_filtros_topo.pack(fill='x', expand=True)

        hoje = datetime.now()
        data_inicio_padrao = hoje - timedelta(days=365)
        
        ttk.Label(frame_filtros_topo, text="De:").pack(side='left', padx=(0,5))
        self.entrada_data_inicio = DateEntry(frame_filtros_topo, dateformat='%d/%m/%Y', startdate=data_inicio_padrao, firstweekday=6)
        self.entrada_data_inicio.pack(side='left', padx=(0,10))

        ttk.Label(frame_filtros_topo, text="Até:").pack(side='left', padx=(0,5))
        self.entrada_data_fim = DateEntry(frame_filtros_topo, dateformat='%d/%m/%Y', startdate=hoje, firstweekday=6)
        self.entrada_data_fim.pack(side='left', padx=(0,10))

        self.btn_aplicar_filtros = ttk.Button(frame_filtros_topo, text="Aplicar Filtros")
        self.btn_aplicar_filtros.pack(side='left', padx=5)
        self.btn_limpar_filtros = ttk.Button(frame_filtros_topo, text="Limpar Filtros")
        self.btn_limpar_filtros.pack(side='left', padx=5)
        self.btn_exportar_excel = ttk.Button(frame_filtros_topo, text="Exportar para Excel")
        self.btn_exportar_excel.pack(side='left', padx=5)

        frame_filtros_baixo = ttk.Frame(frame_filtros)
        frame_filtros_baixo.pack(fill='x', expand=True, pady=(10,0))
        
        self.combo_filtro_tipo = self._criar_combobox_filtro(frame_filtros_baixo, "Tipo")
        self.combo_filtro_cc = self._criar_combobox_filtro(frame_filtros_baixo, "Centro de Custo")
        self.combo_filtro_veiculo = self._criar_combobox_filtro(frame_filtros_baixo, "Veículo")
        self.combo_filtro_categoria = self._criar_combobox_filtro(frame_filtros_baixo, "Categoria")
        self.combo_filtro_cliente = self._criar_combobox_filtro(frame_filtros_baixo, "Cliente")
        self.combo_filtro_status = self._criar_combobox_filtro(frame_filtros_baixo, "Status")

        # Notebook para as abas (Registros Detalhados e Gráficos Visuais)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)
        self.aba_registros = ttk.Frame(self.notebook)
        self.aba_graficos = ttk.Frame(self.notebook) # O frame para a aba de gráficos
        self.notebook.add(self.aba_registros, text='Registros Detalhados')
        self.notebook.add(self.aba_graficos, text='Gráficos Visuais')

        # --- ALTERAÇÃO AQUI ---
        # Instanciar o GraficosFrame e colocá-lo na aba_graficos
        self.graficos_view = GraficosFrame(self.aba_graficos)
        self.graficos_view.pack(fill='both', expand=True)
        # ---------------------

        self._criar_aba_registros()

    def _criar_combobox_filtro(self, pai, rotulo):
        frame = ttk.Frame(pai)
        frame.pack(side='left', padx=5, fill='x', expand=True)
        ttk.Label(frame, text=rotulo).pack(side='top', anchor='w')
        combo = ttk.Combobox(frame, state="readonly")
        combo.pack(side='top', fill='x', expand=True)
        return combo

    def _criar_aba_registros(self):
        # --- PARTE 1: CRIAÇÃO DOS CONTROLES DE PAGINAÇÃO (AGORA NO INÍCIO) ---
        # Vamos criar e posicionar a paginação na parte de baixo PRIMEIRO.
        frame_paginacao = ttk.Frame(self.aba_registros)
        frame_paginacao.pack(side="bottom", fill="x", pady=5) # Alterado para side="bottom"

        self.btn_pagina_anterior = ttk.Button(frame_paginacao, text="< Anterior")
        self.btn_pagina_anterior.pack(side='left', padx=5)

        self.lbl_info_pagina = ttk.Label(frame_paginacao, text="Página 1 de 1")
        self.lbl_info_pagina.pack(side='left', padx=5)

        self.btn_proxima_pagina = ttk.Button(frame_paginacao, text="Próximo >")
        self.btn_proxima_pagina.pack(side='left', padx=5)

        self.btn_editar_lancamento = ttk.Button(frame_paginacao, text="Editar Lançamento Selecionado", command=self._abrir_janela_editar_lancamento)
        self.btn_editar_lancamento.pack(side='right', padx=10)

        self.btn_excluir_lancamento = ttk.Button(frame_paginacao, text="Excluir Lançamento Selecionado")
        self.btn_excluir_lancamento.pack(side='right', padx=10)


        # --- PARTE 2: CRIAÇÃO DA TABELA (TREEVIEW) ---
        # Agora, a tabela pode se expandir e preencher o resto do espaço.
        colunas = ('Data', 'Empresa', 'Centro de Custo', 'Veículo', 'Cliente', 'Categoria', 'Descrição', 'Tipo', 'Valor', 'Status')
        self.arvore_relatorio = ttk.Treeview(self.aba_registros, columns=colunas, show='headings', height=20)

        # Configuração dos cabeçalhos e colunas
        for col in colunas:
            self.arvore_relatorio.heading(col, text=col)
            if col in ['Descrição', 'Centro de Custo']:
                self.arvore_relatorio.column(col, width=180)
            elif col in ['Data', 'Tipo', 'Status']:
                self.arvore_relatorio.column(col, width=100)
            else:
                self.arvore_relatorio.column(col, width=120)

        # Comando para exibir a tabela no espaço restante
        self.arvore_relatorio.pack(side="top", fill="both", expand=True)

    # Métodos que estavam em AppPrincipal e agora pertencem a PainelDireito
    def obter_filtros(self):
        try:
            inicio = datetime.strptime(self.entrada_data_inicio.entry.get(), '%d/%m/%Y')
            fim = datetime.strptime(self.entrada_data_fim.entry.get(), '%d/%m/%Y')
        except ValueError:
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

    def atualizar_dropdown(self, nome_dropdown, valores):
        dropdowns = {
            'cc': self.combo_filtro_cc, 'veiculo': self.combo_filtro_veiculo,
            'categoria': self.combo_filtro_categoria, 'tipo': self.combo_filtro_tipo,
            'cliente': self.combo_filtro_cliente, 'status': self.combo_filtro_status
        }
        if nome_dropdown in dropdowns:
            dropdowns[nome_dropdown]['values'] = ["Todos"] + valores
            dropdowns[nome_dropdown].set("Todos")

    def atualizar_info_pagina(self, atual, total):
        self.lbl_info_pagina.config(text=f"Página {atual} de {total}")

    def atualizar_arvore_lancamentos(self, dataframe):
        self.arvore_relatorio.delete(*self.arvore_relatorio.get_children())

        if dataframe is None or dataframe.empty:
            return

        df_exibicao = dataframe.rename(columns={"Centro_de_Custo": "Centro de Custo"})
        df_exibicao['Valor'] = pd.to_numeric(df_exibicao['Valor'], errors='coerce').fillna(0)
        df_exibicao['Data'] = pd.to_datetime(df_exibicao['Data'], errors='coerce')

        dados_formatados = []
        for index, row in df_exibicao.iterrows():
            valor_formatado = f"R$ {row['Valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            data_formatada = row['Data'].strftime('%d/%m/%Y') if pd.notna(row['Data']) else ''

            valores_linha = (
                data_formatada,
                str(row.get('Empresa', '')),
                str(row.get('Centro de Custo', '')),
                str(row.get('Veículo', '')),
                str(row.get('Cliente', '')),
                str(row.get('Categoria', '')),
                str(row.get('Descrição', '')),
                str(row.get('Tipo', '')),
                valor_formatado,
                str(row.get('Status', ''))
            )
            dados_formatados.append((index, valores_linha))

        for iid, valores in dados_formatados:
            self.arvore_relatorio.insert("", "end", iid=iid, values=valores)

    def obter_id_lancamento_selecionado(self):
        itens_selecionados = self.arvore_relatorio.selection()
        if not itens_selecionados: return None
        return itens_selecionados[0]
    
    def _abrir_janela_novo_lancamento(self):
        if self.controlador:
            self._criar_janela_lancamento("Novo Lançamento", self.controlador.salvar_novo_lancamento)

    def _abrir_janela_editar_lancamento(self):
        if self.controlador:
            self.controlador.editar_lancamento_selecionado()

    def _criar_janela_lancamento(self, titulo, callback_salvar, dados_edicao=None):
        # Usa self.master_app_root que foi configurado no __init__ para popups
        popup = tk.Toplevel(self.master_app_root) 
        popup.title(titulo)

        frame = ttk.Frame(popup, padding="10")
        frame.pack(fill="both", expand=True)

        def obter_valores_combobox(combobox):
            valores = combobox['values']
            if isinstance(valores, str):
                return []
            return list(valores)

        linha = 0 
        ttk.Label(frame, text="Data:").grid(row=linha, column=0, sticky="w", pady=5)
        entrada_data = DateEntry(frame, dateformat='%d/%m/%Y', firstweekday=6)
        entrada_data.grid(row=linha, column=1, sticky="ew", pady=5)
        linha += 1
        
        ttk.Label(frame, text="Centro de Custo:").grid(row=linha, column=0, sticky="w", pady=5)
        valores_cc = obter_valores_combobox(self.combo_filtro_cc)
        combo_cc = ttk.Combobox(frame, state="readonly", values=valores_cc[1:] if valores_cc else [])
        combo_cc.grid(row=linha, column=1, sticky="ew", pady=5)
        linha += 1
        
        ttk.Label(frame, text="Veículo:").grid(row=linha, column=0, sticky="w", pady=5)
        valores_veiculo = obter_valores_combobox(self.combo_filtro_veiculo)
        combo_veiculo = ttk.Combobox(frame, state="readonly", values=["N/A"] + (valores_veiculo[1:] if valores_veiculo else []))
        combo_veiculo.grid(row=linha, column=1, sticky="ew", pady=5)
        linha += 1

        ttk.Label(frame, text="Cliente:").grid(row=linha, column=0, sticky="w", pady=5)
        valores_cliente = obter_valores_combobox(self.combo_filtro_cliente)
        combo_cliente = ttk.Combobox(frame, state="readonly", values=["Nenhum"] + (valores_cliente[1:] if valores_cliente else []))
        combo_cliente.grid(row=linha, column=1, sticky="ew", pady=5)
        linha += 1

        ttk.Label(frame, text="Categoria:").grid(row=linha, column=0, sticky="w", pady=5)
        valores_cat = obter_valores_combobox(self.combo_filtro_categoria)
        combo_cat = ttk.Combobox(frame, state="readonly", values=valores_cat[1:] if valores_cat else [])
        combo_cat.grid(row=linha, column=1, sticky="ew", pady=5)
        linha += 1

        ttk.Label(frame, text="Descrição:").grid(row=linha, column=0, sticky="w", pady=5)
        entrada_desc = ttk.Entry(frame)
        entrada_desc.grid(row=linha, column=1, sticky="ew", pady=5)
        linha += 1

        ttk.Label(frame, text="Tipo:").grid(row=linha, column=0, sticky="w", pady=5)
        combo_tipo = ttk.Combobox(frame, state="readonly", values=["Receita", "Despesa"])
        combo_tipo.grid(row=linha, column=1, sticky="ew", pady=5)
        linha += 1
        
        ttk.Label(frame, text="Valor:").grid(row=linha, column=0, sticky="w", pady=5)
        entrada_valor = ttk.Entry(frame)
        entrada_valor.grid(row=linha, column=1, sticky="ew", pady=5)
        linha += 1

        ttk.Label(frame, text="Status:").grid(row=linha, column=0, sticky="w", pady=5)
        combo_status = ttk.Combobox(frame, state="readonly", values=["Pendente", "Pago", "Atrasado"])
        combo_status.grid(row=linha, column=1, sticky="ew", pady=5)
        linha += 1

        if dados_edicao:
            data_edicao = pd.to_datetime(dados_edicao['Data'])
            entrada_data.entry.delete(0, tk.END)
            entrada_data.entry.insert(0, data_edicao.strftime('%d/%m/%Y'))
            combo_cc.set(dados_edicao.get('Centro_de_Custo', ''))
            combo_veiculo.set(dados_edicao.get('Veículo', 'N/A'))
            combo_cliente.set(dados_edicao.get('Cliente', 'Nenhum'))
            combo_cat.set(dados_edicao.get('Categoria', ''))
            entrada_desc.insert(0, dados_edicao.get('Descrição', ''))
            combo_tipo.set(dados_edicao.get('Tipo', ''))
            entrada_valor.insert(0, f"{dados_edicao.get('Valor', 0.0):.2f}")
            combo_status.set(dados_edicao.get('Status', ''))


        def ao_salvar():
            if not all([combo_cat.get(), entrada_desc.get(), combo_tipo.get(), entrada_valor.get()]):
                messagebox.showwarning("Campos Vazios", "Categoria, Descrição, Tipo e Valor são obrigatórios.", parent=popup)
                return

            try:
                valor_float = float(entrada_valor.get().replace(",", "."))
                data_obj = datetime.strptime(entrada_data.entry.get(), '%d/%m/%Y')
                
                dados = {
                    'Data': data_obj, 'Centro_de_Custo': combo_cc.get() or None,
                    'Veículo': combo_veiculo.get() if combo_veiculo.get() != "N/A" else None,
                    'Categoria': combo_cat.get(), 'Descrição': entrada_desc.get(),
                    'Tipo': combo_tipo.get(), 'Valor': valor_float,
                    'Cliente': combo_cliente.get() if combo_cliente.get() != "Nenhum" else None,
                    'Status': combo_status.get() or 'Pendente'
                }

                callback_salvar(dados)
                popup.destroy()
            except ValueError:
                messagebox.showerror("Erro de Valor", "Verifique o formato do valor ou da data.", parent=popup)

        btn_salvar = ttk.Button(frame, text="Salvar", command=ao_salvar)
        btn_salvar.grid(row=linha, column=0, columnspan=2, pady=20)
        
        frame.columnconfigure(1, weight=1)

    def resetar_filtros(self):
        
        # Resetar Datas
        hoje = datetime.now()
        data_inicio_padrao = hoje - timedelta(days=365)
        
        # A forma correta de resetar o DateEntry é limpar o campo e inserir o novo valor
        self.entrada_data_inicio.entry.delete(0, tk.END)
        self.entrada_data_inicio.entry.insert(0, data_inicio_padrao.strftime('%d/%m/%Y'))
        
        self.entrada_data_fim.entry.delete(0, tk.END)
        self.entrada_data_fim.entry.insert(0, hoje.strftime('%d/%m/%Y'))

        # Resetar todos os Comboboxes de filtro
        self.combo_filtro_tipo.set("Todos")
        self.combo_filtro_cc.set("Todos")
        self.combo_filtro_veiculo.set("Todos")
        self.combo_filtro_categoria.set("Todos")
        self.combo_filtro_cliente.set("Todos")
        self.combo_filtro_status.set("Todos")