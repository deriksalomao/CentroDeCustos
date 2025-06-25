# app/ui/ui_graficos.py
import ttkbootstrap as ttk
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class GraficosFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=ttk.BOTH, expand=True)

    def atualizar_todos_os_graficos(self, df_filtrado):
        # 1. Limpa todos os widgets antigos da aba
        for widget in self.winfo_children():
            widget.destroy()

        # 2. Se não houver dados, exibe uma mensagem centralizada
        if df_filtrado.empty:
            msg_label = ttk.Label(self, text="Sem dados para exibir no período selecionado.", font=("Segoe UI", 12))
            msg_label.pack(pady=50)
            return

        # 3. Cria um sistema de abas (Notebook) dentro da aba principal de gráficos
        notebook_graficos = ttk.Notebook(self)
        notebook_graficos.pack(fill=ttk.BOTH, expand=True, padx=5, pady=5)

        # 4. Cria um Frame para cada aba de gráfico
        tab_evolucao = ttk.Frame(notebook_graficos)
        tab_pizza = ttk.Frame(notebook_graficos)

        notebook_graficos.add(tab_evolucao, text='Evolução Mensal')
        notebook_graficos.add(tab_pizza, text='Distribuição de Despesas')

        # 5. Desenha cada gráfico em sua respectiva aba
        self._criar_grafico_evolucao(df_filtrado, parent_tab=tab_evolucao)
        self._criar_grafico_despesas_pizza(df_filtrado, parent_tab=tab_pizza)

    def _criar_grafico_evolucao(self, df, parent_tab):
        """Cria o gráfico de barras da evolução de Receitas x Despesas."""
        df_copia = df.copy()
        df_copia['Data'] = pd.to_datetime(df_copia['Data'])
        df_copia.set_index('Data', inplace=True)
        
        # CORREÇÃO APLICADA AQUI: Trocado 'M' por 'ME'
        df_mensal = df_copia.groupby([pd.Grouper(freq='ME'), 'Tipo'])['Valor'].sum().unstack(fill_value=0)
        
        # Garante que as colunas Despesa e Receita existam para evitar erros
        if 'Despesa' not in df_mensal: df_mensal['Despesa'] = 0
        if 'Receita' not in df_mensal: df_mensal['Receita'] = 0
            
        df_mensal.index = df_mensal.index.strftime('%b/%Y')

        figura = Figure(figsize=(10, 4), dpi=100)
        ax = figura.add_subplot(111)
        
        # O Pandas ordena as colunas alfabeticamente ('Despesa', 'Receita')
        df_mensal[['Despesa', 'Receita']].plot(kind='bar', ax=ax, color=['#dc3545', '#28a745'], width=0.8)

        ax.set_title('Evolução Mensal: Receitas vs. Despesas', fontsize=16, pad=20)
        ax.set_xlabel('')
        ax.set_ylabel('Valor (R$)')
        ax.tick_params(axis='x', rotation=45, labelsize=9)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.legend(['Despesas', 'Receitas'])
        figura.tight_layout()

        canvas = FigureCanvasTkAgg(figura, master=parent_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=ttk.BOTH, expand=True, padx=10, pady=10)

    def _criar_grafico_despesas_pizza(self, df, parent_tab):
        """Cria o gráfico de pizza da distribuição de despesas."""
        df_despesas = df[df['Tipo'] == 'Despesa'].copy()

        if df_despesas.empty:
            ttk.Label(parent_tab, text="Nenhuma despesa no período para exibir.").pack(pady=20)
            return

        despesas_por_categoria = df_despesas.groupby('Categoria')['Valor'].sum()

        figura = Figure(figsize=(8, 5), dpi=100)
        ax = figura.add_subplot(111)
        
        cores = plt.cm.get_cmap('viridis', len(despesas_por_categoria))
        wedges, texts, autotexts = ax.pie(
            despesas_por_categoria,
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops=dict(width=0.4, edgecolor='w'),
            colors=cores.colors,
            pctdistance=0.80
        )
        plt.setp(autotexts, size=9, weight="bold", color="white")
        ax.set_title('Distribuição de Despesas por Categoria', fontsize=16, pad=20)
        ax.legend(wedges, despesas_por_categoria.index, title="Categorias", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)
        figura.tight_layout()

        canvas = FigureCanvasTkAgg(figura, master=parent_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=ttk.BOTH, expand=True, padx=10, pady=10)