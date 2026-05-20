# ==============================================================================
# components/sidebar.py
# Define o layout da barra lateral fixa usada em dispositivos desktop.
# ==============================================================================
import flet as ft

from src.core.state import estado
from src.core.utils import border_all


def menu_lateral(p: dict, navegar_callback) -> ft.Container:
    """
    Constrói o menu lateral (sidebar).

    Parâmetros:
    - p: dicionário de tema (cores dinâmicas)
    - navegar_callback: função responsável por troca de rotas

    Retorno:
    - ft.Container representando a sidebar completa
    """

    def criar_item_menu(icone: ft.IconData, rotulo: str, rota: str) -> ft.Container:
        """Helper para criar itens de navegação consistentes."""
        ativo = estado["rota"] == rota

        item_controls: list[ft.Control] = [
            ft.Icon(
                icone,
                size=20,
                color=ft.Colors.WHITE if ativo else p["icone_menu_norm"],
            ),
            ft.Text(
                rotulo,
                size=13,
                color=ft.Colors.WHITE if ativo else p["txt_menu_normal"],
                weight=ft.FontWeight.BOLD if ativo else ft.FontWeight.NORMAL,
            ),
        ]

        return ft.Container(
            content=ft.Row(controls=item_controls, spacing=15),
            padding=15,
            # Muda a cor de fundo se o item estiver selecionado
            bgcolor=p["bg_menu_ativo"] if ativo else "transparent",
            border_radius=8,
            on_click=lambda e: navegar_callback(rota),
        )

    # Lista de itens do menu (com um Divider e um rodapé fixo)
    sidebar_controls: list[ft.Control] = [
        criar_item_menu(ft.Icons.HOME_OUTLINED, "Home", "/"),
        criar_item_menu(ft.Icons.NOTE_OUTLINED, "Notas", "/notas"),
        criar_item_menu(ft.Icons.ASSIGNMENT_OUTLINED, "Tarefas", "/tarefas"),
        criar_item_menu(ft.Icons.CALENDAR_TODAY_OUTLINED, "Agenda", "/agenda"),
        ft.Divider(height=20, color=p["borda_padrao"]),
        criar_item_menu(ft.Icons.SETTINGS_OUTLINED, "Configurações", "/config"),
        # 'expand=True' força o próximo Divider e o rodapé para o fim do container
        ft.Container(expand=True),
        ft.Divider(height=10, color=p["borda_padrao"]),
        ft.Text("© 2026 NoteSync", size=9, color=p["txt_card_label"]),
    ]

    return ft.Container(
        content=ft.Column(controls=sidebar_controls, spacing=0),
        width=250,
        padding=0,
        bgcolor=p["bg_sidebar"],
        border=border_all(1, p["borda_sidebar"]),
    )
