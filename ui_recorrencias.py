# ui_recorrencias.py
# Lida com a janela e a lógica de Lançamentos Recorrentes.

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pandas as pd

class RecorrenciasManager:
    def __init__(self, app):
        self.app = app
        self.data_manager = app.data_manager

    def abrir_janela_recorrencias(self):
        win = tk.Toplevel(self.app.root); win.title("Gestão de Lançamentos Recorrentes"); win.geometry("800x500")
        win.transient(self.app.root); win.grab_set()
        frame = ttk.Frame(win, padding=10); frame.pack(fill='both', expand=True)
        colunas = ('descricao', 'valor', 'tipo', 'empresa', 'categoria', 'dia', 'ultimo_lancamento')
        tree = ttk.Treeview(frame, columns=colunas, show='headings'); tree.pack(side='left', fill='both', expand=True)
        tree.heading('descricao', text='Descrição'); tree.column('descricao', width=200)
        tree.heading('valor', text='Valor'); tree.column('valor', width=80, anchor='e')
        tree.heading('tipo', text='Tipo'); tree.column('tipo', width=80, anchor='center')
        tree.heading('empresa', text='Empresa'); tree.column('empresa', width=120)
        tree.heading('categoria', text='Categoria'); tree.column('categoria', width=100)
        tree.heading('dia', text='Dia do Mês'); tree.column('dia', width=80, anchor='center')
        tree.heading('ultimo_lancamento', text='Último Lançamento'); tree.column('ultimo_lancamento', width=120, anchor='center')
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview); scrollbar.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scrollbar.set)
        botoes_frame = ttk.Frame(win, padding=10); botoes_frame.pack(fill='x')

        def popular_tree():
            for i in tree.get_children(): tree.delete(i)
            for idx, rec in enumerate(self.data_manager.recorrencias):
                tree.insert('', 'end', iid=idx, values=(rec.get('descricao', ''), f"R$ {rec.get('valor', 0):.2f}", rec.get('tipo', ''), rec.get('empresa', ''), rec.get('categoria', ''), rec.get('dia_mes', ''), rec.get('ultimo_lancamento', 'Nunca')))

        def adicionar(): self._popup_gerir_recorrencia(callback=popular_tree)
        def editar():
            if not tree.focus(): return
            self._popup_gerir_recorrencia(self.data_manager.recorrencias[int(tree.focus())], int(tree.focus()), callback=popular_tree)
        def excluir():
            if not tree.focus(): return
            if messagebox.askyesno("Confirmar", "Tem a certeza que deseja excluir esta recorrência?"):
                del self.data_manager.recorrencias[int(tree.focus())]; popular_tree(); self.app.set_status("Recorrência excluída.")

        ttk.Button(botoes_frame, text="Adicionar Nova", command=adicionar).pack(side='left', padx=5)
        ttk.Button(botoes_frame, text="Editar Selecionada", command=editar).pack(side='left', padx=5)
        ttk.Button(botoes_frame, text="Excluir Selecionada", command=excluir, style="Danger.TButton").pack(side='right', padx=5)
        popular_tree()

    def _popup_gerir_recorrencia(self, dados=None, idx=None, callback=None):
        win = tk.Toplevel(self.app.root); win.title("Adicionar/Editar Recorrência"); win.geometry("450x350")
        win.transient(self.app.root); win.grab_set()
        frame = ttk.Frame(win, padding=15); frame.pack(fill='both', expand=True); frame.columnconfigure(1, weight=1)
        campos = {}
        ttk.Label(frame, text="Descrição:").grid(row=0, column=0, sticky='w', pady=5); campos['descricao'] = ttk.Entry(frame); campos['descricao'].grid(row=0, column=1, sticky='ew', pady=5)
        ttk.Label(frame, text="Valor (R$):").grid(row=1, column=0, sticky='w', pady=5); campos['valor'] = ttk.Entry(frame); campos['valor'].grid(row=1, column=1, sticky='ew', pady=5)
        ttk.Label(frame, text="Tipo:").grid(row=2, column=0, sticky='w', pady=5); campos['tipo'] = ttk.Combobox(frame, values=["Receita", "Despesa"], state='readonly'); campos['tipo'].grid(row=2, column=1, sticky='ew', pady=5)
        ttk.Label(frame, text="Empresa:").grid(row=3, column=0, sticky='w', pady=5); campos['empresa'] = ttk.Combobox(frame, values=list(self.data_manager.dados_empresas.keys()), state='readonly'); campos['empresa'].grid(row=3, column=1, sticky='ew', pady=5)
        ttk.Label(frame, text="Categoria:").grid(row=4, column=0, sticky='w', pady=5); campos['categoria'] = ttk.Combobox(frame, values=self.data_manager.categorias, state='readonly'); campos['categoria'].grid(row=4, column=1, sticky='ew', pady=5)
        ttk.Label(frame, text="Dia do Mês para Lançar:").grid(row=5, column=0, sticky='w', pady=5); campos['dia_mes'] = ttk.Spinbox(frame, from_=1, to=31); campos['dia_mes'].grid(row=5, column=1, sticky='ew', pady=5)
        
        if dados:
            campos['descricao'].insert(0, dados.get('descricao', '')); campos['valor'].insert(0, dados.get('valor', ''))
            campos['tipo'].set(dados.get('tipo', 'Despesa')); campos['empresa'].set(dados.get('empresa', ''))
            campos['categoria'].set(dados.get('categoria', '')); campos['dia_mes'].set(dados.get('dia_mes', 1))

        def salvar():
            try:
                rec = {'descricao': campos['descricao'].get(), 'valor': float(campos['valor'].get()), 'tipo': campos['tipo'].get(), 'empresa': campos['empresa'].get(), 'categoria': campos['categoria'].get(), 'dia_mes': int(campos['dia_mes'].get()), 'ultimo_lancamento': dados.get('ultimo_lancamento', 'Nunca') if dados else 'Nunca'}
                if not all(rec.values()): raise ValueError("Preencha todos os campos.")
            except Exception as e: messagebox.showerror("Erro de Validação", str(e), parent=win); return

            if idx is not None: self.data_manager.recorrencias[idx] = rec; self.app.set_status("Recorrência atualizada.")
            else: self.data_manager.recorrencias.append(rec); self.app.set_status("Recorrência adicionada.")
            if callback: callback()
            win.destroy()
        ttk.Button(frame, text="Salvar", command=salvar).grid(row=6, column=0, columnspan=2, pady=20)

    def verificar_e_lancar_recorrencias(self):
        hoje = datetime.now(); mudancas = False
        for rec in self.data_manager.recorrencias:
            ultimo = None
            if rec['ultimo_lancamento'] != 'Nunca':
                try: ultimo = datetime.strptime(rec['ultimo_lancamento'], '%Y-%m-%d')
                except ValueError: continue
            lancar = (ultimo is None or (ultimo.year, ultimo.month) != (hoje.year, hoje.month)) and hoje.day >= rec['dia_mes']
            if lancar:
                novo_lanc = pd.DataFrame([[hoje.replace(day=rec['dia_mes']), rec['empresa'], 'Geral', rec['categoria'], rec['descricao'], rec['tipo'], rec['valor']]], columns=self.data_manager.colunas)
                self.data_manager.df_lancamentos = pd.concat([self.data_manager.df_lancamentos, novo_lanc], ignore_index=True)
                rec['ultimo_lancamento'] = hoje.strftime('%Y-%m-%d'); mudancas = True
        
        if mudancas: self.app.atualizar_relatorio(); self.app.set_status("Lançamentos recorrentes foram criados/atualizados.")
