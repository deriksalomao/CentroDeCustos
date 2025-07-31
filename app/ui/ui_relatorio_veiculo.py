import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *

class RelatorioVeiculo:
    def __init__(self, master, controller):
        self.master = master
        self.controller = controller
        self.empresa_ativa = self.controller.view.get_empresa_ativa()
        
        self.veiculos_da_empresa = self.controller.model.get_lookup_data('veiculos', self.empresa_ativa)

        # --- Configuração da Janela (Toplevel) ---
        self.win = tk.Toplevel(self.master)
        self.win.title(f"Relatório de Custo por Veículo - {self.empresa_ativa}")
        self.win.geometry("1200x700")
        self.win.transient(self.master)
        self.win.grab_set()

        # --- Frame de Filtros ---
        frame_filtros = ttk.LabelFrame(self.win, text="Filtros do Relatório", padding=10)
        frame_filtros.pack(padx=10, pady=10, fill='x')

        ttk.Label(frame_filtros, text="Mês/Ano (MM/AAAA):").pack(side='left', padx=(0, 5))
        self.entry_mes_ano = ttk.Entry(frame_filtros, width=10)
        self.entry_mes_ano.pack(side='left', padx=5)

        ttk.Label(frame_filtros, text="Veículo:").pack(side='left', padx=(10, 5))
        self.combo_veiculo = ttk.Combobox(frame_filtros, values=self.veiculos_da_empresa, state='readonly', width=20)
        self.combo_veiculo.pack(side='left', padx=5)

        btn_gerar = ttk.Button(frame_filtros, text="Gerar Relatório", command=self.gerar_relatorio, bootstyle=SUCCESS)
        btn_gerar.pack(side='left', padx=10)
        
        btn_exportar = ttk.Button(frame_filtros, text="Exportar para Excel", command=self.exportar_relatorio, bootstyle=INFO)
        btn_exportar.pack(side='right', padx=10)

        # --- Frame de Resumo do Veículo ---
        self.frame_resumo = ttk.LabelFrame(self.win, text="Resumo", padding=10)
        self.frame_resumo.pack(padx=10, pady=5, fill='x')
        self.lbl_resumo_veiculo = ttk.Label(self.frame_resumo, text="Veículo: - | Período: -")
        self.lbl_resumo_veiculo.pack()

        # --- Tabela de Dados (usando ttkbootstrap Tableview) ---
        frame_tabela = ttk.Frame(self.win, padding=10)
        frame_tabela.pack(fill='both', expand=True)

        # Definição das colunas baseada na sua planilha
        self.colunas = [
            {"text": "DATA", "stretch": False, "width": 100},
            {"text": "PNEU", "stretch": True}, {"text": "PECAS", "stretch": True},
            {"text": "BORRACHARIA", "stretch": True}, {"text": "MECANICO", "stretch": True},
            {"text": "COMBUSTIVEL", "stretch": True}, {"text": "AJUDANTE", "stretch": True},
            {"text": "MOTORISTA", "stretch": True}, {"text": "VR DESPESAS", "stretch": True},
            {"text": "AGREGADO", "stretch": True}, {"text": "FRETE VAS", "stretch": True},
            {"text": "ICMS", "stretch": True}, {"text": "TOTAL", "stretch": True},
            {"text": "SALDO", "stretch": True}, {"text": "INDICE", "stretch": True}
        ]
        
        self.tabela = Tableview(frame_tabela, coldata=self.colunas, rowdata=[], paginated=False, searchable=False, autofit=True)
        self.tabela.pack(fill='both', expand=True)
        
        # --- Frame de Totais ---
        frame_totais = ttk.LabelFrame(self.win, text="Totais do Período", padding=10)
        frame_totais.pack(padx=10, pady=10, fill='x')
        self.lbl_totais = ttk.Label(frame_totais, text="Aguardando geração do relatório...", font=("-weight bold"))
        self.lbl_totais.pack()

    def gerar_relatorio(self):
        """Pega os filtros da tela e pede para o controller processar os dados."""
        mes_ano = self.entry_mes_ano.get()
        placa = self.combo_veiculo.get()

        if not mes_ano or not placa:
            messagebox.showwarning("Filtros incompletos", "Por favor, preencha o Mês/Ano e selecione um Veículo.", parent=self.win)
            return
            
        self.tabela.delete_rows()
        self.lbl_resumo_veiculo.config(text=f"Veículo: {placa} | Período: {mes_ano}")
        self.lbl_totais.config(text="Processando dados...")

        # Chama o controller para buscar e processar os dados
        dados_relatorio, totais = self.controller.processar_relatorio_veiculo(placa, mes_ano)
        
        # Preenche a tabela com os dados recebidos do controller
        if dados_relatorio:
            self.tabela.insert_rows('end', dados_relatorio)
            self.tabela.autofit_columns()
        
        # Atualiza o label de totais com os dados recebidos
        if totais and (totais['total_despesas'] > 0 or totais['total_frete'] > 0):
            totais_texto = (
                f"TOTAL DESPESAS: R$ {totais['total_despesas']:,.2f}   |   "
                f"TOTAL FRETE: R$ {totais['total_frete']:,.2f}   |   "
                f"SALDO FINAL: R$ {totais['saldo_final']:,.2f}   |   "
                f"ÍNDICE MÉDIO: {totais['indice_medio']:.2f}%"
            )
            self.lbl_totais.config(text=totais_texto)
        else:
            self.lbl_totais.config(text="Nenhum dado encontrado para este período.")

    def exportar_relatorio(self):
        """Pede para o controller exportar os dados visíveis na tabela."""
        dados_visiveis = self.tabela.get_rows(visible=True)
        # Envia uma lista de listas para o controller
        self.controller.exportar_relatorio_veiculo([d.values for d in dados_visiveis])