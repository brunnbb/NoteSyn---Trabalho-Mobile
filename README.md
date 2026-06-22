Aqui está o seu arquivo README.md completado e organizado, com as explicações da estrutura e os comandos necessários para cada gerenciador.

---

# NoteSyn

O **NoteSyn** é um aplicativo de gerenciamento de notas, tarefas e agenda, desenvolvido com Python e Flet.

### Requisitos

* Python 3.12+
* [`uv`](https://docs.astral.sh/uv/) (Recomendado)

## Estrutura do Projeto

```text
NoteSyn/
├── src/                    # Pasta do código-fonte dos itens da aplicação
│   ├── components/         # Componentes de interface reutilizáveis
│   │   ├── appbar.py       # Barra de navegação superior
│   │   └── sidebar.py      # Menu lateral de navegação
│   ├── core/               # Lógica central e configurações globais
│   │   ├── constants.py    # Constantes do sistema
│   │   ├── state.py        # Estado global e gerenciamento de dados
│   │   ├── theme.py        # Definições de paletas de cores e temas
│   │   └── utils.py        # Funções auxiliares e utilitários
│   ├── views/              # Telas (páginas) do aplicativo
│   │   ├── agenda.py       # Visualização da agenda
│   │   ├── config.py       # Tela de configurações
│   │   ├── home.py         # Dashboard principal
│   │   ├── notas.py        # Gerenciamento de notas
│   │   └── tarefas.py      # Gerenciamento de tarefas
│   └── __init__.py         # Torna src um pacote Python
├── .gitignore              # Arquivos ignorados pelo Git
├── .python-version         # Versão do Python utilizada no projeto
├── main.py                 # Ponto de entrada (execução) do projeto
├── pyproject.toml          # Definições do projeto e dependências (uv/pip)
├── README.md               # Documentação do projeto
├── requirements.txt        # Lista de dependências para instalação via pip
└── uv.lock                 # Arquivo de bloqueio de versões (uv)

```

### Instalação das Dependências

Para preparar o seu ambiente, escolha uma das opções abaixo:

**Usando `uv` (Recomendado):**
O `uv` é extremamente rápido e gerencia o ambiente automaticamente.

```bash
uv sync

# O uv normalmente já ativa o ambiente virtual automaticamente, mas você pode ativar manualmente se preferir
# Ativar (Windows)
.\venv\Scripts\activate
# Ativar (Linux/macOS)
source ./venv/bin/activate

```

**Usando `pip` e `venv` (Tradicional):**

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
.\venv\Scripts\activate
# Ativar (Linux/macOS)
source ./venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

```

## Rodando o Projeto

Após instalar as dependências, execute o comando correspondente:

* **Com `uv`:**
```bash
uv run flet run
# Ou
flet run

```

* **Com `pip`:**
```bash
flet run

```

## Observações

* Certifique-se de que o seu terminal esteja na pasta raiz `NoteSyn/` antes de rodar os comandos.
* Ainda não possui persistência de dados.
