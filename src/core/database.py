# ==============================================================================
# core/database.py
# Camada de persistência SQLite. Expõe funções CRUD para notas e tarefas.
# O banco é criado automaticamente em ~/.notesyn/notesyn.db na primeira execução.
# ==============================================================================

import sqlite3
from datetime import datetime
from pathlib import Path

# Diretório e arquivo do banco de dados
_DB_DIR = Path.home() / ".notesyn"
_DB_PATH = _DB_DIR / "notesyn.db"


def _get_connection() -> sqlite3.Connection:
    """
    Abre (ou cria) a conexão com o banco.
    row_factory permite acessar colunas por nome (como dict).
    """
    _DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_banco():
    """
    Cria as tabelas caso não existam ainda.
    Deve ser chamado uma única vez na inicialização do app (em main.py).
    """
    with _get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS notas (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo      TEXT    NOT NULL,
                conteudo    TEXT    NOT NULL DEFAULT '',
                data        TEXT    NOT NULL,
                categoria   TEXT    NOT NULL DEFAULT 'pessoal',
                importante  INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS tarefas (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo          TEXT    NOT NULL,
                descricao       TEXT    NOT NULL DEFAULT '',
                concluida       INTEGER NOT NULL DEFAULT 0,
                prioridade      TEXT    NOT NULL DEFAULT 'média',
                data_vencimento TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            );
        """)


# ==============================================================================
# Configurações — chave/valor persistido
# ==============================================================================


def get_config(chave: str, padrao: str = "") -> str:
    """Lê um valor de configuração. Retorna `padrao` se a chave não existir."""
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT valor FROM configuracoes WHERE chave = ?", (chave,)
        ).fetchone()
    return row["valor"] if row else padrao


def set_config(chave: str, valor: str) -> None:
    """Grava (INSERT OR REPLACE) um valor de configuração."""
    with _get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)",
            (chave, valor),
        )


# ==============================================================================
# CRUD — Notas
# ==============================================================================


def criar_nota(titulo: str, conteudo: str, categoria: str, importante: bool) -> dict:
    """
    INSERT de uma nova nota.
    Retorna a nota recém-criada como dict (com id gerado pelo banco).
    """
    data = datetime.now().strftime("%d/%m/%Y")
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO notas (titulo, conteudo, data, categoria, importante)
            VALUES (?, ?, ?, ?, ?)
            """,
            (titulo, conteudo, data, categoria, int(importante)),
        )
        assert cursor.lastrowid is not None
        return {
            "id": cursor.lastrowid,
            "titulo": titulo,
            "conteudo": conteudo,
            "data": data,
            "categoria": categoria,
            "importante": importante,
        }


def listar_notas() -> list[dict]:
    """SELECT de todas as notas, ordenadas por id decrescente (mais recentes primeiro)."""
    with _get_connection() as conn:
        rows = conn.execute("SELECT * FROM notas ORDER BY id DESC").fetchall()
    return [_row_to_nota(r) for r in rows]


def buscar_nota_por_id(nota_id: int) -> dict | None:
    """SELECT de uma nota pelo id. Retorna None se não encontrada."""
    with _get_connection() as conn:
        row = conn.execute("SELECT * FROM notas WHERE id = ?", (nota_id,)).fetchone()
    return _row_to_nota(row) if row else None


def atualizar_nota(
    nota_id: int, titulo: str, conteudo: str, categoria: str, importante: bool
) -> dict | None:
    """UPDATE de uma nota existente. Retorna a nota atualizada."""
    with _get_connection() as conn:
        conn.execute(
            """
            UPDATE notas
               SET titulo = ?, conteudo = ?, categoria = ?, importante = ?
             WHERE id = ?
            """,
            (titulo, conteudo, categoria, int(importante), nota_id),
        )
    return buscar_nota_por_id(nota_id)


def deletar_nota(nota_id: int) -> bool:
    """DELETE de uma nota pelo id. Retorna True se alguma linha foi removida."""
    with _get_connection() as conn:
        cursor = conn.execute("DELETE FROM notas WHERE id = ?", (nota_id,))
    return cursor.rowcount > 0


# ==============================================================================
# CRUD — Tarefas
# ==============================================================================


def criar_tarefa(
    titulo: str, descricao: str, prioridade: str, data_vencimento: str
) -> dict:
    """
    INSERT de uma nova tarefa.
    Retorna a tarefa recém-criada como dict.
    """
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tarefas (titulo, descricao, prioridade, data_vencimento, concluida)
            VALUES (?, ?, ?, ?, 0)
            """,
            (titulo, descricao, prioridade, data_vencimento),
        )
        assert cursor.lastrowid is not None
        return {
            "id": cursor.lastrowid,
            "titulo": titulo,
            "descricao": descricao,
            "concluida": False,
            "prioridade": prioridade,
            "data_vencimento": data_vencimento,
        }


def listar_tarefas() -> list[dict]:
    """SELECT de todas as tarefas, pendentes primeiro, depois por id."""
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM tarefas ORDER BY concluida ASC, id DESC"
        ).fetchall()
    return [_row_to_tarefa(r) for r in rows]


def buscar_tarefa_por_id(tarefa_id: int) -> dict | None:
    """SELECT de uma tarefa pelo id. Retorna None se não encontrada."""
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM tarefas WHERE id = ?", (tarefa_id,)
        ).fetchone()
    return _row_to_tarefa(row) if row else None


def atualizar_tarefa(
    tarefa_id: int, titulo: str, descricao: str, prioridade: str, data_vencimento: str
) -> dict | None:
    """UPDATE dos campos editáveis de uma tarefa. Retorna a tarefa atualizada."""
    with _get_connection() as conn:
        conn.execute(
            """
            UPDATE tarefas
               SET titulo = ?, descricao = ?, prioridade = ?, data_vencimento = ?
             WHERE id = ?
            """,
            (titulo, descricao, prioridade, data_vencimento, tarefa_id),
        )
    return buscar_tarefa_por_id(tarefa_id)


def alternar_conclusao_tarefa(tarefa_id: int) -> dict | None:
    """
    Faz o toggle do campo 'concluida' (0→1 ou 1→0).
    Retorna a tarefa com o novo estado.
    """
    with _get_connection() as conn:
        conn.execute(
            "UPDATE tarefas SET concluida = NOT concluida WHERE id = ?",
            (tarefa_id,),
        )
    return buscar_tarefa_por_id(tarefa_id)


def deletar_tarefa(tarefa_id: int) -> bool:
    """DELETE de uma tarefa pelo id. Retorna True se alguma linha foi removida."""
    with _get_connection() as conn:
        cursor = conn.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
    return cursor.rowcount > 0


# ==============================================================================
# Helpers internos
# ==============================================================================


def _row_to_nota(row: sqlite3.Row) -> dict:
    """Converte sqlite3.Row → dict com bool para o campo 'importante'."""
    return {
        "id": row["id"],
        "titulo": row["titulo"],
        "conteudo": row["conteudo"],
        "data": row["data"],
        "categoria": row["categoria"],
        "importante": bool(row["importante"]),
    }


def _row_to_tarefa(row: sqlite3.Row) -> dict:
    """Converte sqlite3.Row → dict com bool para o campo 'concluida'."""
    return {
        "id": row["id"],
        "titulo": row["titulo"],
        "descricao": row["descricao"],
        "concluida": bool(row["concluida"]),
        "prioridade": row["prioridade"],
        "data_vencimento": row["data_vencimento"],
    }
