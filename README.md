
### **Descrição do Projeto: Centro de Custos**

O **Centro de Custos** é uma aplicação de desktop para gerenciamento financeiro, desenvolvida em Python com uma interface gráfica construída em Tkinter. O sistema foi projetado para permitir que usuários (seja para uso pessoal ou de pequenos negócios) controlem suas finanças de forma organizada e eficiente.

A aplicação permite o registro detalhado de transações (lançamentos), associando cada uma a uma empresa e a uma categoria específica. Todos os dados são armazenados localmente (Em desenvolvimento), garantindo a privacidade e o controle total das informações pelo usuário.

#### **Recursos Principais:**

* 🔐 **Autenticação de Usuário:** Acesso ao sistema protegido por uma tela de login.
* 💸 **Gestão de Lançamentos:** Funcionalidades completas de CRUD (Criar, Ler, Atualizar, Deletar) para transações financeiras.
* 🏢 **Cadastro de Entidades:** Permite gerenciar as **Empresas** e **Categorias** utilizadas para classificar os lançamentos.
* 🔄 **Controle de Recorrências:** Facilita o gerenciamento de despesas e receitas recorrentes, como aluguéis ou salários.
* 💾 **Persistência Local:** Os dados são salvos em arquivos locais (`CSV` e `JSON`), utilizando a biblioteca Pandas para manipulação.
* 📊 **Dashboard (Futuro):** Interface preparada para receber gráficos e visualizações que fornecerão insights sobre a saúde financeira.

#### **Tecnologias Utilizadas:**

* **Linguagem:** Python
* **Interface Gráfica (GUI):** Tkinter, Ttkbootstrap (para temas) e Tkcalendar (para seleção de datas).
* **Manipulação de Dados:** Pandas