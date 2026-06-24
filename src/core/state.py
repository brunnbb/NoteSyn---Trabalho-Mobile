# ==============================================================================
# core/state.py
# Estado global de UI (tema, rota, responsividade).
# Os dados de notas e tarefas agora vivem no SQLite (ver core/database.py).
# ==============================================================================

estado = {
    "tema": "claro",
    "rota": "/",
    "mobile": True,
    "usuario": "Bruno",
}
