# ui_graficos.py
# Lida com a janela de Análise Gráfica e exportações.

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import io
from datetime import datetime

# --- IMPORTS CORRIGIDOS ---
# Adiciona todas as bibliotecas que este módulo utiliza
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import pandas as pd
    MATPLOTLIB_DISPONIVEL = True
except ImportError:
    MATPLOTLIB_DISPONIVEL = False

try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    REPORTLAB_DISPONIVEL = True
except ImportError:
    REPORTLAB_DISPONIVEL = False
# --- FIM DAS CORREÇÕES ---


class GraficosManager:
    def __init__(self, app):
        self.app = app

    def abrir_janela_graficos(self):
        if not MATPLOTLIB_DISPONIVEL:
            messagebox.showerror("Biblioteca em Falta", "Instale 'matplotlib' para usar a análise gráfica."); return
        df_filtrado = self.app.get_filtered_data()
        if df_filtrado.empty:
            messagebox.showinfo("Sem Dados", "Não há dados para gerar gráficos com os filtros atuais."); return
        
        plt.style.use('seaborn-v0_8-darkgrid')
        win = tk.Toplevel(self.app.root); win.title(f"Análise Gráfica - {self.app.combo_empresa_ativa.get()}"); win.geometry("1000x750")
        win.transient(self.app.root); win.grab_set()
        
        main_frame = ttk.Frame(win); main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        notebook = ttk.Notebook(main_frame); notebook.pack(fill='both', expand=True)
        botoes_frame = ttk.Frame(main_frame); botoes_frame.pack(fill='x', pady=(10, 0))
        ttk.Button(botoes_frame, text="Gerar Relatório PDF", command=lambda: self.gerar_relatorio_pdf(df_filtrado)).pack()
        
        tab1 = ttk.Frame(notebook); notebook.add(tab1, text='Despesas por Grupo')
        self._criar_grafico_pizza_ui(tab1, df_filtrado)
        tab2 = ttk.Frame(notebook); notebook.add(tab2, text='Receita vs. Despesa Mensal')
        self._criar_grafico_barras_ui(tab2, df_filtrado)
        tab3 = ttk.Frame(notebook); notebook.add(tab3, text='Evolução do Saldo')
        self._criar_grafico_linha_ui(tab3, df_filtrado)

    def _criar_grafico_pizza_ui(self, parent, df):
        frame_ctrl = ttk.Frame(parent); frame_ctrl.pack(fill='x', pady=5)
        ttk.Label(frame_ctrl, text="Agrupar por:").pack(side='left', padx=5)
        combo = ttk.Combobox(frame_ctrl, values=["Categoria", "Centro de Custo"], state='readonly'); combo.pack(side='left', padx=5); combo.set("Categoria")
        canvas_frame = ttk.Frame(parent); canvas_frame.pack(fill='both', expand=True)
        
        def atualizar():
            for w in canvas_frame.winfo_children(): w.destroy()
            grupo = combo.get()
            dados = df[df['Tipo'] == 'Despesa'].groupby(grupo)['Valor'].sum()
            if dados.empty: ttk.Label(canvas_frame, text="Não há despesas para exibir.").pack(pady=20); return
            fig = self._plotar_grafico_pizza_fig(dados, grupo)
            canvas = FigureCanvasTkAgg(fig, master=canvas_frame); canvas.draw(); canvas.get_tk_widget().pack(fill='both', expand=True)
        
        combo.bind("<<ComboboxSelected>>", lambda e: atualizar()); atualizar()

    def _criar_grafico_barras_ui(self, parent, df):
        fig = self._plotar_grafico_barras_fig(df)
        canvas = FigureCanvasTkAgg(fig, master=parent); canvas.draw(); canvas.get_tk_widget().pack(fill='both', expand=True)

    def _criar_grafico_linha_ui(self, parent, df):
        fig = self._plotar_grafico_linha_fig(df)
        canvas = FigureCanvasTkAgg(fig, master=parent); canvas.draw(); canvas.get_tk_widget().pack(fill='both', expand=True)

    def _plotar_grafico_pizza_fig(self, df_despesas, grupo):
        fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(aspect="equal"))
        explode = pd.Series(0.0, index=df_despesas.index)
        if not df_despesas.empty: explode[df_despesas.idxmax()] = 0.1
        colors = plt.cm.viridis(df_despesas.values / max(df_despesas.values.max(), 1))
        wedges, texts, autotexts = ax.pie(df_despesas, labels=df_despesas.index, autopct='%1.1f%%', startangle=140, pctdistance=0.85, explode=explode, colors=colors, shadow=True)
        plt.setp(autotexts, size=10, weight="bold", color="white"); plt.setp(texts, size=9)
        ax.set_title(f"Distribuição de Despesas por {grupo}", fontsize=14, fontweight='bold', pad=20)
        ax.add_artist(plt.Circle((0,0), 0.70, fc='white')); return fig

    def _plotar_grafico_barras_fig(self, df):
        df_plot = df.copy()
        df_plot['Mês'] = pd.to_datetime(df_plot['Data']).dt.to_period('M')
        dados = df_plot.groupby(['Mês', 'Tipo'])['Valor'].sum().unstack(fill_value=0).astype(float); dados.index = dados.index.strftime('%Y-%m')
        fig, ax = plt.subplots(figsize=(10, 6))
        color_map = {'Despesa': '#E74C3C', 'Receita': '#2ECC71'}
        col_ord = [col for col in ['Despesa', 'Receita'] if col in dados.columns]
        if col_ord:
            dados[col_ord].plot(kind='bar', ax=ax, color=[color_map[col] for col in col_ord])
            for container in ax.containers: ax.bar_label(container, fmt='R$ {:,.0f}', size=8, padding=3, rotation=90)
        ax.set_title("Receitas vs. Despesas Mensais", fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel("Mês", fontsize=10); ax.set_ylabel("Valor (R$)", fontsize=10)
        ax.tick_params(axis='x', rotation=45, labelsize=9); ax.legend(title='Tipo', fontsize=9)
        fig.tight_layout(); return fig

    def _plotar_grafico_linha_fig(self, df):
        df_plot = df.copy().sort_values(by="Data")
        fig, ax = plt.subplots(figsize=(10, 6))
        if not df_plot.empty:
            df_plot['Movimento'] = df_plot.apply(lambda row: row['Valor'] if row['Tipo'] == 'Receita' else -row['Valor'], axis=1)
            df_plot['Saldo Acumulado'] = df_plot['Movimento'].cumsum()
            y, x = df_plot['Saldo Acumulado'].values, df_plot['Data'].values
            ax.plot(x, y, color='#3498DB', marker='o', linestyle='-', markersize=5)
            ax.fill_between(x, y, where=y > 0, color='#2ECC71', alpha=0.3, interpolate=True)
            ax.fill_between(x, y, where=y <= 0, color='#E74C3C', alpha=0.3, interpolate=True)
            ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
        ax.set_title("Evolução do Saldo Acumulado", fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel("Data", fontsize=10); ax.set_ylabel("Saldo (R$)", fontsize=10)
        fig.tight_layout(); return fig

    def gerar_relatorio_pdf(self, df_filtrado):
        if not REPORTLAB_DISPONIVEL: messagebox.showerror("Biblioteca em Falta", "Instale 'reportlab' para gerar PDFs."); return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Ficheiros PDF", "*.pdf")], title="Salvar Relatório PDF", initialfile=f"Relatorio_{self.app.combo_empresa_ativa.get().replace(' ', '_')}_{datetime.now():%Y-%m-%d}.pdf")
        if not path: return
        try:
            doc = SimpleDocTemplate(path, rightMargin=inch/2, leftMargin=inch/2, topMargin=inch/2, bottomMargin=inch/2)
            styles = getSampleStyleSheet()
            story = [Paragraph(f"Relatório de Análise Gráfica", styles['h1']), Paragraph(f"Empresa: {self.app.combo_empresa_ativa.get()}", styles['h2']), Paragraph(f"Período: {self.app.date_inicio.get_date():%d/%m/%Y} a {self.app.date_fim.get_date():%d/%m/%Y}", styles['Normal']), Spacer(1, 0.4*inch)]
            
            def save_fig(fig):
                buf = io.BytesIO(); fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                plt.close(fig); buf.seek(0)
                return Image(buf, width=7*inch, height=4.5*inch, kind='proportional')

            dados_pizza = df_filtrado[df_filtrado['Tipo'] == 'Despesa'].groupby('Categoria')['Valor'].sum()
            if not dados_pizza.empty: story.extend([Paragraph("Distribuição de Despesas por Categoria", styles['h3']), save_fig(self._plotar_grafico_pizza_fig(dados_pizza, 'Categoria')), Spacer(1, 0.2*inch)])
            if not df_filtrado.empty:
                story.extend([Paragraph("Receitas vs. Despesas Mensais", styles['h3']), save_fig(self._plotar_grafico_barras_fig(df_filtrado)), Spacer(1, 0.2*inch)])
                story.extend([Paragraph("Evolução do Saldo Acumulado", styles['h3']), save_fig(self._plotar_grafico_linha_fig(df_filtrado))])

            doc.build(story)
            messagebox.showinfo("Sucesso", f"Relatório exportado para:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro de Exportação", f"Não foi possível gerar o PDF.\nErro: {e}")

    def exportar_para_excel(self):
        df_filtrado = self.app.get_filtered_data()
        if df_filtrado.empty: messagebox.showinfo("Informação", "Não há dados para exportar."); return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Ficheiros Excel", "*.xlsx")], title="Guardar Relatório como...", initialfile=f"Relatorio_{self.app.combo_empresa_ativa.get().replace(' ', '_')}_{datetime.now():%Y-%m-%d}.xlsx")
        if not path: return
        try:
            df_filtrado.to_excel(path, index=False, engine='openpyxl')
            messagebox.showinfo("Sucesso", f"Relatório exportado para:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro de Exportação", f"Não foi possível exportar o ficheiro.\nErro: {e}")
