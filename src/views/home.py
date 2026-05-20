# ==============================================================================
# views/home.py
# Dashboard principal exibindo resumos e progresso.
# ==============================================================================
import flet as ft

from src.core.state import dados_notas, dados_tarefas, estado
from src.core.utils import border_all, controls_list


def view_home(p: dict) -> ft.Container:
    total_notas = len(dados_notas)
    total_tarefas = len(dados_tarefas)
    tarefas_pendentes = sum(1 for t in dados_tarefas if not t["concluida"])
    tarefas_concluidas = sum(1 for t in dados_tarefas if t["concluida"])

    progresso = (tarefas_concluidas / total_tarefas * 100) if total_tarefas > 0 else 0

    def criar_card_estatistica(
        titulo: str, valor: str, icone: ft.IconData, cor: str
    ) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls_list(
                    ft.Icon(icone, size=32, color=cor),
                    ft.Text(titulo, size=12, color=p["txt_card_label"]),
                    ft.Text(
                        valor,
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=p["txt_card_valor"],
                    ),
                ),
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
            bgcolor=p["bg_card"],
            border=border_all(2, cor),
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=4,
                color=p["sombra"],
                offset=ft.Offset(0, 2),
            ),
        )

    cards_stats = ft.Row(
        [
            criar_card_estatistica(
                "Total de Notas",
                str(total_notas),
                ft.Icons.NOTE_OUTLINED,
                p["borda_blue"],
            ),
            criar_card_estatistica(
                "Tarefas Pendentes",
                str(tarefas_pendentes),
                ft.Icons.ASSIGNMENT_OUTLINED,
                p["borda_red"],
            ),
            criar_card_estatistica(
                "Concluídas",
                str(tarefas_concluidas),
                ft.Icons.CHECK_CIRCLE_OUTLINED,
                p["borda_green"],
            ),
        ],
        spacing=15,
        wrap=True,
    )

    progresso_slider = ft.Slider(
        min=0,
        max=100,
        value=progresso,
        disabled=True,
        width=300,
        height=40,
        active_color=p["borda_green"],
        inactive_color=p["borda_padrao"],
    )

    progresso_controls: list[ft.Control] = [
        ft.Text(
            "Progresso de Tarefas",
            size=14,
            weight=ft.FontWeight.BOLD,
            color=p["txt_titulo"],
        ),
        ft.Row(
            [
                progresso_slider,
                ft.Text(f"{progresso:.1f}%", size=12, color=p["txt_subtitulo"]),
            ],
            spacing=10,
        ),
    ]
    secao_progresso = ft.Container(
        content=ft.Column(controls=progresso_controls, spacing=10),
        padding=20,
        bgcolor=p["bg_card"],
        border=border_all(1, p["borda_green"]),
        border_radius=10,
    )

    ultimas_notas = ft.Column(spacing=10)
    for nota in dados_notas[:3]:
        nota_controls: list[ft.Control] = [
            ft.Row(
                [
                    ft.Text(
                        nota["titulo"],
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color=p["txt_card_valor"],
                    ),
                    ft.Icon(
                        ft.Icons.STAR if nota["importante"] else ft.Icons.STAR_OUTLINE,
                        size=16,
                        color=p["borda_dica"]
                        if nota["importante"]
                        else p["txt_card_label"],
                    ),
                ],
                spacing=10,
            ),
            ft.Text(
                nota["conteudo"][:60] + "..."
                if len(nota["conteudo"]) > 60
                else nota["conteudo"],
                size=11,
                color=p["txt_subtitulo"],
            ),
            ft.Text(
                f"📅 {nota['data']} • {nota['categoria'].upper()}",
                size=10,
                color=p["txt_card_label"],
            ),
        ]
        nota_card = ft.Container(
            content=ft.Column(controls=nota_controls, spacing=5),
            padding=15,
            bgcolor=p["bg_card"],
            border=border_all(1, p["borda_padrao"]),
            border_radius=8,
        )
        ultimas_notas.controls.append(nota_card)

    home_controls: list[ft.Control] = [
        ft.Text(
            f"Bem-vindo, {estado['usuario']}! 👋",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=p["txt_titulo"],
        ),
        ft.Divider(height=20, color=p["txt_divider"]),
        ft.Text("Resumo", size=16, weight=ft.FontWeight.BOLD, color=p["txt_titulo"]),
        cards_stats,
        ft.Divider(height=20, color=p["txt_divider"]),
        ft.Text(
            "Meu Progresso",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=p["txt_titulo"],
        ),
        secao_progresso,
        ft.Divider(height=20, color=p["txt_divider"]),
        ft.Text(
            "Últimas Notas",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=p["txt_titulo"],
        ),
        ultimas_notas,
    ]

    return ft.Container(
        content=ft.Column(
            controls=home_controls, spacing=15, scroll=ft.ScrollMode.AUTO
        ),
        padding=20,
        bgcolor=p["bg_page"],
        expand=True,
    )
