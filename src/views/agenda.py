# ==============================================================================
# views/agenda.py
# Exibe a linha do tempo de tarefas e notas combinadas.
# ==============================================================================

from datetime import datetime, timedelta

import flet as ft

from src.core import database as db
from src.core.utils import border_all


def view_agenda(page: ft.Page, p: dict) -> ft.Container:
    """
    Constrói a view de Agenda.

    Esta tela combina dados de:
    - notas (dados_notas)
    - tarefas (dados_tarefas)

    E os organiza em uma timeline diária para os próximos N dias,
    onde N é controlado por um Slider.

    Parâmetros:
    - page: instância da página Flet (necessária para update)
    - p: dicionário de tema (cores e estilos)

    Retorna:
    - ft.Container com a UI completa da agenda
    """

    # Slider que controla quantos dias à frente serão exibidos
    dias_slider = ft.Slider(
        min=1,
        max=30,
        value=7,
        divisions=29,
        label="{value} dias",
        width=300,
        active_color=p["borda_blue"],
    )

    # Container principal onde os dias serão renderizados dinamicamente
    agenda_container = ft.Column(spacing=10)

    def atualizar_agenda(e=None):
        """
        Reconstrói completamente a agenda.

        Fluxo:
        1. Limpa o container
        2. Itera sobre os próximos N dias
        3. Filtra tarefas e notas por data
        4. Renderiza cada dia como um card
        """

        agenda_container.controls.clear()

        dias_mostrar = int(dias_slider.value) if dias_slider.value else 7
        hoje = datetime.now()

        # Busca dados frescos do banco a cada atualização da agenda
        todas_tarefas = db.listar_tarefas()
        todas_notas = db.listar_notas()

        for i in range(dias_mostrar):
            # Calcula a data atual da iteração
            data_atual = hoje + timedelta(days=i)
            data_str = data_atual.strftime("%d/%m/%Y")

            # Mapeamento manual do dia da semana
            dia_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"][
                data_atual.weekday()
            ]

            # Filtragem baseada em string → acoplamento com formato de data
            tarefas_dia = [t for t in todas_tarefas if t["data_vencimento"] == data_str]
            notas_dia = [n for n in todas_notas if n["data"] == data_str]

            # Container dos eventos do dia
            eventos_dia = ft.Column(spacing=5)

            # ---------------------- NOTAS ----------------------
            for nota in notas_dia:
                nota_row: list[ft.Control] = [
                    ft.Icon(ft.Icons.NOTE, size=16, color=p["borda_blue"]),
                    ft.Text(nota["titulo"], size=11, color=p["txt_card_valor"]),
                ]

                eventos_dia.controls.append(
                    ft.Container(
                        content=ft.Row(nota_row, spacing=8),
                        padding=8,
                        bgcolor=p["bg_card_blue"],
                        border_radius=5,
                    )
                )

            # ---------------------- TAREFAS ----------------------
            for tarefa in tarefas_dia:
                tarefa_row: list[ft.Control] = [
                    ft.Icon(
                        # Ícone muda conforme status
                        ft.Icons.CHECK_CIRCLE
                        if tarefa["concluida"]
                        else ft.Icons.RADIO_BUTTON_UNCHECKED,
                        size=16,
                        color=p["borda_green"]
                        if tarefa["concluida"]
                        else p["borda_red"],
                    ),
                    ft.Text(
                        tarefa["titulo"],
                        size=11,
                        color=p["txt_card_valor"],
                        # Texto riscado se concluída
                        style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)
                        if tarefa["concluida"]
                        else None,
                    ),
                ]

                eventos_dia.controls.append(
                    ft.Container(
                        content=ft.Row(tarefa_row, spacing=8),
                        padding=8,
                        bgcolor=p["bg_card_green"],
                        border_radius=5,
                    )
                )

            # Caso não haja eventos no dia
            if not eventos_dia.controls:
                eventos_dia.controls.append(
                    ft.Text(
                        "Sem eventos",
                        size=10,
                        color=p["txt_card_label"],
                        italic=True,
                    )
                )

            # ---------------------- HEADER DO DIA ----------------------
            header_row: list[ft.Control] = [
                ft.Column(
                    [
                        ft.Text(
                            f"{data_str}",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=p["txt_card_valor"],
                        ),
                        ft.Text(dia_semana, size=10, color=p["txt_card_label"]),
                    ],
                    spacing=3,
                ),
                ft.VerticalDivider(width=20, color=p["txt_divider"]),
                eventos_dia,
            ]

            # Estrutura do card do dia
            card_column: list[ft.Control] = [
                ft.Row(controls=header_row, spacing=10, expand=True)
            ]

            dia_card = ft.Container(
                content=ft.Column(controls=card_column, spacing=8),
                padding=15,
                bgcolor=p["bg_card"],
                border=border_all(1, p["borda_padrao"]),
                border_radius=8,
            )

            agenda_container.controls.append(dia_card)

        # Atualização manual da UI (Flet não é reativo por padrão aqui)
        page.update()

    # Atualiza agenda sempre que o slider muda
    dias_slider.on_change = atualizar_agenda

    # Render inicial
    atualizar_agenda()

    agenda_controls: list[ft.Control] = [
        ft.Text(
            "Minha Agenda",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=p["txt_titulo"],
        ),
        ft.Divider(height=20, color=p["txt_divider"]),
        ft.Text("Próximos dias:", size=12, color=p["txt_subtitulo"]),
        dias_slider,
        ft.Divider(height=20, color=p["txt_divider"]),
        agenda_container,
    ]

    return ft.Container(
        content=ft.Column(
            controls=agenda_controls,
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        bgcolor=p["bg_page"],
        expand=True,
    )
