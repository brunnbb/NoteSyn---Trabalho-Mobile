# NoteSyn

Aplicativo de gerenciamento pessoal desenvolvido com **Python** e **Flet**, com persistência de dados em **SQLite**. Permite criar e organizar notas, tarefas e visualizar uma agenda, tudo em uma interface responsiva que se adapta a dispositivos móveis e desktop.

## Funcionalidades

- **Notas** — criação, edição e exclusão de notas com suporte a **Markdown**
- **Tarefas** — CRUD completo com prioridade, data de vencimento e controle de conclusão
- **Agenda** — visualização de notas e tarefas organizadas por data
- **Widget de clima** — exibe condições climáticas atuais via [Open-Meteo](https://open-meteo.com/) (sem API key), com cidade configurável e cache de 10 minutos
- **Temas** — alternância entre modo claro e escuro
- **Responsividade** — layout adaptado para mobile e desktop
- **Persistência** — todos os dados (notas, tarefas, configurações, cache de clima) são salvos em `~/.notesyn/notesyn.db`

## Requisitos

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) (recomendado) ou `pip`

## Instalação

**Com `uv` (recomendado):**

```bash
uv sync
```

**Com `pip`:**

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

## Executando

```bash
# Com uv
uv run flet run

# Com pip (ambiente virtual ativado)
flet run
```

> Execute os comandos a partir da pasta raiz do projeto.

## Estrutura do Projeto

```
NoteSyn/
├── main.py                  # Ponto de entrada — roteamento e ciclo de vida
├── pyproject.toml           # Metadados e dependências do projeto
├── requirements.txt         # Dependências para instalação via pip
└── src/
    ├── components/
    │   ├── appbar.py        # Barra superior com título e ações
    │   └── sidebar.py       # Menu lateral de navegação (desktop)
    ├── core/
    │   ├── constants.py     # Constantes globais (breakpoints, versão)
    │   ├── database.py      # Camada SQLite — CRUD de notas, tarefas e configurações
    │   ├── state.py         # Estado global de UI (tema, rota, usuário)
    │   ├── theme.py         # Paletas de cores para tema claro e escuro
    │   ├── utils.py         # Funções auxiliares compartilhadas
    │   └── weather.py       # Integração com a API Open-Meteo
    └── views/
        ├── home.py          # Dashboard — resumo, progresso e clima
        ├── notas.py         # Gerenciamento de notas com editor Markdown
        ├── tarefas.py       # Gerenciamento de tarefas
        ├── agenda.py        # Visualização por data
        └── config.py        # Configurações de perfil e tema
```

## Tecnologias

| Tecnologia | Uso |
|---|---|
| [Flet](https://flet.dev/) | Framework de UI (Flutter via Python) |
| SQLite (stdlib) | Persistência de dados local |
| [Open-Meteo](https://open-meteo.com/) | API de clima — gratuita, sem autenticação |
| [httpx](https://www.python-httpx.org/) | Cliente HTTP para chamadas à API |
| asyncio (stdlib) | Busca de clima sem bloquear a UI |
