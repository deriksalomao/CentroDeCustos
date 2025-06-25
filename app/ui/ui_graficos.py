# app/ui/ui_graficos.py
import ttkbootstrap as ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class GraficosFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=ttk.BOTH, expand=True)

    def atualizar_grafico_despesas(self, df_filtrado):
        # 1. Limpa todos os widgets antigos da aba (sejam gráficos ou mensagens)
        for widget in self.winfo_children():
            widget.destroy()

        # 2. Filtra apenas as despesas
        df_despesas = df_filtrado[df_filtrado['Tipo'] == 'Despesa'].copy()
        
        # 3. Se não houver despesas, exibe a mensagem e para a execução
        if df_despesas.empty:
            msg_label = ttk.Label(self, text="Sem dados de despesa para exibir no período selecionado.", font=("Segoe UI", 12))
            msg_label.pack(pady=50)
            return

        # 4. Se houver dados, cria e exibe o gráfico
        despesas_por_categoria = df_despesas.groupby('Categoria')['Valor'].sum()

        figura = Figure(figsize=(8, 6), dpi=100)
        ax = figura.add_subplot(111)

        # Usando um mapa de cores para melhor visualização
        cores = plt.cm.get_cmap('tab20b', len(despesas_por_categoria))
        
        wedges, texts, autotexts = ax.pie(
            despesas_por_categoria,
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops=dict(width=0.4, edgecolor='w'),
            colors=cores.colors,
            pctdistance=0.80
        )

        # Estiliza o texto de porcentagem dentro do gráfico
        plt.setp(autotexts, size=9, weight="bold", color="white")

        ax.set_ylabel('')
        ax.set_title('Distribuição de Despesas por Categoria', fontsize=16, pad=20)
        
        ax.legend(wedges, despesas_por_categoria.index,
                  title="Categorias",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1),
                  fontsize=9)
                  
        figura.tight_layout()

        canvas = FigureCanvasTkAgg(figura, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=ttk.BOTH, expand=True, padx=10, pady=10)