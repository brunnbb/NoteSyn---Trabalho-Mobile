# ==============================================================================
# views/tarefas.py
# Interface de CRUD para as tarefas com verificação de status.
# ==============================================================================

from datetime import datetime

import flet as ft

from src.core.state import dados_tarefas
from src.core.utils import border_all, exibir_notificacao


def view_tarefas(page: ft.Page, p: dict) -> ft.Container:
    """
    Constrói a tela de gerenciamento de tarefas (CRUD + controle de status).

    Responsabilidades:
    - Criar, editar e remover tarefas
    - Marcar tarefas como concluídas/pendentes (toggle)
    - Exibir métricas derivadas (total, concluídas, pendentes)
    - Renderizar lista com feedback visual por prioridade e status

    Características arquiteturais:
    - Estado global mutável (dados_tarefas)
    - Estado local para edição e data selecionada
    - Renderização manual (rebuild completo da lista)
    - UI não reativa automaticamente (uso explícito de page.update)

    Observações importantes:
    - Datas são armazenadas como string (acoplamento com formatação)
    - IDs são incrementais em memória (sem persistência)
    - Atualizações de stats dependem de chamada manual

    Parâmetros:
    - page: instância da página Flet (render e notificações)
    - p: dicionário de tema (cores)

    Retorna:
    - ft.Container com toda a view de tarefas
    """

    # None = criação | valor = edição
    tarefa_id_em_edicao = None

    # ---------------------- FORMULÁRIO ----------------------

    # Campo principal da tarefa (obrigatório)
    titulo_tarefa = ft.TextField(
        label="Título da Tarefa",
        prefix_icon=ft.Icons.TASK_ALT,
        border_color=p["borda_padrao"],
        color=p["txt_card_valor"],
        label_style=ft.TextStyle(color=p["txt_card_label"]),
        width=400,
    )

    # Campo descritivo opcional
    descricao_tarefa = ft.TextField(
        label="Descrição",
        multiline=True,
        min_lines=2,
        max_lines=4,
        border_color=p["borda_padrao"],
        color=p["txt_card_valor"],
        label_style=ft.TextStyle(color=p["txt_card_label"]),
        width=400,
    )

    # Define prioridade (impacta cor do card)
    prioridade_dropdown = ft.Dropdown(
        label="Prioridade",
        width=150,
        options=[
            ft.dropdown.Option("baixa", "Baixa"),
            ft.dropdown.Option("média", "Média"),
            ft.dropdown.Option("alta", "Alta"),
            ft.dropdown.Option("urgente", "Urgente"),
        ],
        value="média",
        border_color=p["borda_padrao"],
        color=p["txt_card_valor"],
        label_style=ft.TextStyle(color=p["txt_card_label"]),
    )

    # ---------------------- DATA ----------------------

    # Estado local da data (não vinculado automaticamente ao DatePicker)
    data_vencimento_text = ft.Text("Data: Hoje", size=11, color=p["txt_card_label"])
    data_selecionada = None

    def atualizar_data(e):
        """
        Atualiza manualmente a data selecionada no DatePicker.

        Observação:
        - Flet não faz binding automático aqui
        - Precisamos sincronizar manualmente UI + estado
        """
        nonlocal data_selecionada
        if data_picker.value:
            data_selecionada = data_picker.value.strftime("%d/%m/%Y")
            data_vencimento_text.value = f"Data: {data_selecionada}"
            page.update()

    data_picker = ft.DatePicker(on_change=atualizar_data)

    # Botão alterna entre criar e editar dinamicamente
    btn_salvar_tarefa = ft.FilledButton(
        "Adicionar Tarefa",
        icon=ft.Icons.ADD_TASK,
        color=p["txt_card_valor"],
        bgcolor=p["borda_green"],
        on_click=lambda e: salvar_tarefa(e),
    )

    # Lista renderizada manualmente (sem binding automático)
    lista_tarefas = ft.Column(spacing=10)

    # ---------------------- AÇÕES ----------------------

    def carregar_tarefa_para_edicao(tarefa: dict):
        """
        Carrega dados da tarefa no formulário e ativa modo edição.

        Efeitos:
        - Preenche campos
        - Atualiza estado local
        - Muda aparência do botão
        """
        nonlocal tarefa_id_em_edicao, data_selecionada
        tarefa_id_em_edicao = tarefa["id"]

        titulo_tarefa.value = tarefa["titulo"]
        descricao_tarefa.value = tarefa["descricao"]
        prioridade_dropdown.value = tarefa["prioridade"]
        data_selecionada = tarefa["data_vencimento"]
        data_vencimento_text.value = f"Data: {data_selecionada}"

        # Feedback visual de modo edição
        btn_salvar_tarefa.content = "Atualizar Tarefa"
        btn_salvar_tarefa.icon = ft.Icons.EDIT
        btn_salvar_tarefa.bgcolor = p["borda_dica"]

        page.update()

    def limpar_formulario_tarefa():
        """
        Reseta formulário para modo criação.

        Efeitos:
        - Limpa todos os campos
        - Remove estado de edição
        - Restaura botão padrão
        """
        nonlocal tarefa_id_em_edicao, data_selecionada
        tarefa_id_em_edicao = None

        titulo_tarefa.value = ""
        descricao_tarefa.value = ""
        prioridade_dropdown.value = "média"

        data_selecionada = None
        data_vencimento_text.value = "Data: Hoje"

        btn_salvar_tarefa.content = "Adicionar Tarefa"
        btn_salvar_tarefa.icon = ft.Icons.ADD_TASK
        btn_salvar_tarefa.bgcolor = p["borda_green"]

    # ---------------------- STATS ----------------------

    # Textos de estatísticas (não reativos automaticamente)
    txt_total = ft.Text(size=12, color=p["txt_subtitulo"], weight=ft.FontWeight.BOLD)
    txt_concluidas = ft.Text(size=12, color=p["borda_green"], weight=ft.FontWeight.BOLD)
    txt_pendentes = ft.Text(size=12, color=p["borda_red"], weight=ft.FontWeight.BOLD)

    def atualizar_stats():
        """
        Calcula métricas derivadas do estado global.

        Métricas:
        - Total de tarefas
        - Quantidade concluída
        - Quantidade pendente

        Observação:
        - Deve ser chamado manualmente após qualquer mutação
        """
        total = len(dados_tarefas)
        concluidas = sum(1 for t in dados_tarefas if t["concluida"])
        pendentes = total - concluidas

        txt_total.value = f"Total: {total}"
        txt_concluidas.value = f"Concluídas: {concluidas}"
        txt_pendentes.value = f"Pendentes: {pendentes}"

    def atualizar_lista_tarefas():
        """
        Reconstrói toda a lista de tarefas + estatísticas.

        Estratégia:
        - Atualiza métricas
        - Limpa lista
        - Recria cada item manualmente
        - Força render com page.update()

        Trade-off:
        - Simples, porém O(n) a cada atualização
        """
        atualizar_stats()
        lista_tarefas.controls.clear()

        for tarefa in dados_tarefas:
            # Cor baseada na prioridade (mapeamento direto)
            cor_prioridade = {
                "baixa": p["borda_green"],
                "média": p["borda_dica"],
                "alta": p["borda_red"],
                "urgente": "#ff006e",
            }.get(tarefa["prioridade"], p["borda_padrao"])

            def marcar_concluida(e, tid):
                """
                Alterna status de conclusão da tarefa.

                Implementação:
                - Mutação direta no estado global
                - Re-render completo após alteração
                """
                for t in dados_tarefas:
                    if t["id"] == tid:
                        t["concluida"] = not t["concluida"]
                        exibir_notificacao(page, "Status da tarefa alterado!")
                atualizar_lista_tarefas()

            card_controls: list[ft.Control] = [
                ft.Checkbox(
                    value=tarefa["concluida"],
                    # Default arg evita bug de late binding
                    on_change=lambda e, tid=tarefa["id"]: marcar_concluida(e, tid),
                    fill_color=p["borda_blue"],
                ),
                ft.Column(
                    [
                        ft.Text(
                            tarefa["titulo"],
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=p["txt_card_valor"],
                            # Estilo condicional para concluídas
                            style=ft.TextStyle(
                                decoration=ft.TextDecoration.LINE_THROUGH
                            )
                            if tarefa["concluida"]
                            else None,
                        ),
                        ft.Text(tarefa["descricao"], size=11, color=p["txt_subtitulo"]),
                        ft.Row(
                            [
                                ft.Text(
                                    f"⏰ {tarefa['data_vencimento']}",
                                    size=9,
                                    color=p["txt_card_label"],
                                ),
                                ft.Text(
                                    f"🎯 {tarefa['prioridade'].upper()}",
                                    size=9,
                                    color=cor_prioridade,
                                ),
                            ],
                            spacing=15,
                        ),
                    ],
                    spacing=5,
                    expand=True,
                ),
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.EDIT_OUTLINED,
                            icon_color=p["borda_blue"],
                            tooltip="Editar",
                            on_click=lambda e, t=tarefa: carregar_tarefa_para_edicao(t),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=p["borda_red"],
                            tooltip="Deletar",
                            # Evita problema de referência tardia
                            on_click=lambda e, tid=tarefa["id"]: deletar_tarefa(tid),
                        ),
                    ],
                    spacing=0,
                ),
            ]

            tarefa_card = ft.Container(
                content=ft.Row(controls=card_controls, spacing=10),
                padding=15,
                bgcolor=p["bg_card"],
                border=border_all(1, cor_prioridade),
                border_radius=8,
            )

            lista_tarefas.controls.append(tarefa_card)

        page.update()

    def salvar_tarefa(e):
        """
        Cria ou atualiza uma tarefa.

        Fluxo:
        - Validação
        - Determinação de CREATE ou UPDATE
        - Mutação do estado global
        - Re-renderização
        """
        nonlocal tarefa_id_em_edicao, data_selecionada

        if not titulo_tarefa.value:
            exibir_notificacao(
                page, "O título da tarefa não pode ser vazio!", sucesso=False
            )
            return

        # Fallback para data atual
        final_date = data_selecionada or datetime.now().strftime("%d/%m/%Y")

        if tarefa_id_em_edicao is not None:
            # UPDATE
            for t in dados_tarefas:
                if t["id"] == tarefa_id_em_edicao:
                    t["titulo"] = titulo_tarefa.value
                    t["descricao"] = descricao_tarefa.value
                    t["prioridade"] = prioridade_dropdown.value or "média"
                    t["data_vencimento"] = final_date
                    break
            exibir_notificacao(page, "Tarefa atualizada com sucesso!")
        else:
            # CREATE
            nova_tarefa = {
                "id": max([t["id"] for t in dados_tarefas], default=0) + 1,
                "titulo": titulo_tarefa.value,
                "descricao": descricao_tarefa.value,
                "concluida": False,
                "prioridade": prioridade_dropdown.value or "média",
                "data_vencimento": final_date,
            }
            dados_tarefas.append(nova_tarefa)
            exibir_notificacao(page, "Tarefa criada com sucesso!")

        limpar_formulario_tarefa()
        atualizar_lista_tarefas()

    def deletar_tarefa(tarefa_id):
        """
        Remove tarefa pelo ID.

        Detalhe importante:
        - Usa slice assignment para preservar referência da lista
        """
        dados_tarefas[:] = [t for t in dados_tarefas if t["id"] != tarefa_id]

        exibir_notificacao(page, "Tarefa removida.")

        if tarefa_id_em_edicao == tarefa_id:
            limpar_formulario_tarefa()

        atualizar_lista_tarefas()

    # Render inicial
    atualizar_lista_tarefas()

    # ---------------------- LAYOUT ----------------------

    form_controls: list[ft.Control] = [
        ft.Text(
            "Informações da Tarefa",
            size=14,
            weight=ft.FontWeight.BOLD,
            color=p["txt_titulo"],
        ),
        titulo_tarefa,
        descricao_tarefa,
        ft.Row(
            [
                prioridade_dropdown,
                ft.IconButton(
                    icon=ft.Icons.CALENDAR_TODAY,
                    icon_color=p["borda_blue"],
                    tooltip="Selecionar data",
                    on_click=lambda e: page.show_dialog(data_picker),
                ),
                data_vencimento_text,
            ],
            spacing=10,
        ),
        ft.Row(
            [
                btn_salvar_tarefa,
                ft.TextButton(
                    "Cancelar", on_click=lambda e: limpar_formulario_tarefa()
                ),
            ],
            spacing=10,
        ),
    ]

    main_controls: list[ft.Control] = [
        ft.Text(
            "Minhas Tarefas",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=p["txt_titulo"],
        ),
        ft.Divider(height=20, color=p["txt_divider"]),
        ft.Container(
            content=ft.Column(controls=form_controls, spacing=10),
            padding=20,
            bgcolor=p["bg_card"],
            border=border_all(2, p["borda_green"]),
            border_radius=10,
        ),
        ft.Divider(height=20, color=p["txt_divider"]),
        ft.Row(
            [
                txt_total,
                txt_concluidas,
                txt_pendentes,
            ],
            spacing=20,
        ),
        lista_tarefas,
    ]

    return ft.Container(
        content=ft.Column(
            controls=main_controls,
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        bgcolor=p["bg_page"],
        expand=True,
    )
