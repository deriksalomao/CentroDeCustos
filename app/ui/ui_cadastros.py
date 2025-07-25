# app/ui/ui_cadastros.py
import tkinter as tk
from tkinter import ttk, messagebox

class CadastrosManager:
    def __init__(self, master, controller):
        self.master = master
        self.controller = controller
        self.empresa_ativa = self.controller.view.get_empresa_ativa()

        self.win = tk.Toplevel(self.master)
        self.win.title(f"Gestão de Cadastros - {self.empresa_ativa}")
        self.win.geometry("800x600")
        self.win.transient(self.master)
        self.win.grab_set()

        self.notebook = ttk.Notebook(self.win)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        self.tipos_cadastro = ['Cliente', 'Veículo', 'Centro de Custo', 'Categoria']
        self.trees = {}

        for tipo in self.tipos_cadastro:
            self._criar_aba(tipo)

    def _criar_aba(self, tipo_cadastro):
        """Cria uma aba completa com Treeview e botões para um tipo de cadastro."""
        frame_aba = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame_aba, text=tipo_cadastro)

        frame_tree = ttk.Frame(frame_aba)
        frame_tree.pack(fill="both", expand=True)

        tree = ttk.Treeview(frame_tree, columns=('Nome'), show='headings')
        tree.heading('Nome', text='Nome')
        tree.pack(side="left", fill="both", expand=True)
        self.trees[tipo_cadastro] = tree

        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        frame_botoes = ttk.Frame(frame_aba)
        frame_botoes.pack(fill="x", pady=10)

        btn_adicionar = ttk.Button(frame_botoes, text=f"Adicionar Novo(a) {tipo_cadastro}",
                                   command=lambda t=tipo_cadastro: self._adicionar_item(t))
        btn_adicionar.pack(side="left", padx=5)

        btn_excluir = ttk.Button(frame_botoes, text=f"Excluir Selecionado(a)", style="danger.TButton",
                                 command=lambda t=tipo_cadastro: self._excluir_item(t))
        btn_excluir.pack(side="right", padx=5)

        self._popular_tree(tipo_cadastro)

    def _popular_tree(self, tipo_cadastro):
        """Busca os dados e preenche a Treeview."""
        tree = self.trees[tipo_cadastro]
        for i in tree.get_children():
            tree.delete(i)
        
        dados = self.controller.model.get_lookup_data(
            self._get_tabela_map()[tipo_cadastro], 
            self.empresa_ativa
        )
        
        for nome_item in sorted(dados):
            tree.insert("", "end", values=(nome_item,))
    
    def _adicionar_item(self, tipo_cadastro):
        """Abre um popup para adicionar um novo item."""
        from tkinter.simpledialog import askstring
        novo_nome = askstring(f"Adicionar {tipo_cadastro}", f"Digite o nome do(a) novo(a) {tipo_cadastro}:", parent=self.win)
        
        if novo_nome and novo_nome.strip():
            self.controller.adicionar_item_rapido(tipo_cadastro, novo_nome.strip())
            self._popular_tree(tipo_cadastro)
            self.controller.update_all_filters()

    def _excluir_item(self, tipo_cadastro):
        """Exclui o item selecionado na Treeview."""
        tree = self.trees[tipo_cadastro]
        selecionado = tree.focus()
        if not selecionado:
            messagebox.showwarning("Nenhum item selecionado", "Por favor, selecione um item para excluir.", parent=self.win)
            return

        item = tree.item(selecionado)
        nome_item = item['values'][0]

        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir '{nome_item}'?", parent=self.win):
            self.controller.excluir_item_rapido(tipo_cadastro, nome_item)
            self._popular_tree(tipo_cadastro)
            self.controller.update_all_filters()

    def _get_tabela_map(self):
        return {
            'Cliente': 'clientes',
            'Veículo': 'veiculos',
            'Centro de Custo': 'centros_de_custo',
            'Categoria': 'categorias'
        }