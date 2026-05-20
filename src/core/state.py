# ==============================================================================
# core/state.py
# Simula um banco de dados em memória e gerencia o estado global (tema, rota).
# ==============================================================================
from datetime import datetime

dados_notas = [
    {
        "id": 1,
        "titulo": "Reunião de Algo",
        "conteudo": "Discutir coisas bem importantes",
        "data": datetime.now().strftime("%d/%m/%Y"),
        "categoria": "trabalho",
        "importante": True,
    },
    {
        "id": 2,
        "titulo": "Ideias de Projeto",
        "conteudo": "Criar um Tinder para cavalos usando Flet",
        "data": datetime.now().strftime("%d/%m/%Y"),
        "categoria": "ideias",
        "importante": False,
    },
]

dados_tarefas = [
    {
        "id": 1,
        "titulo": "Comprar leite",
        "descricao": "Passar no mercado após o trabalho",
        "concluida": False,
        "prioridade": "baixa",
        "data_vencimento": datetime.now().strftime("%d/%m/%Y"),
    },
    {
        "id": 2,
        "titulo": "Entrega do relatório",
        "descricao": "Enviar relatório para pessoas",
        "concluida": True,
        "prioridade": "urgente",
        "data_vencimento": datetime.now().strftime("%d/%m/%Y"),
    },
]

estado = {
    "tema": "claro",
    "rota": "/",
    "mobile": False,
    "usuario": "Bruno",
}
