# ==============================================================================
# components/appbar.py
# Responsável pela construção da barra de topo (AppBar) da aplicação.
# Gerencia a troca de temas, navegação secundária e menu mobile (BottomSheet).
# ==============================================================================
import flet as ft

from src.components.sidebar import menu_lateral
from src.core.constants import APP_NAME
from src.core.state import estado


def construir_appbar(
    page: ft.Page, p: dict, alternar_tema_callback, navegar_callback
) -> ft.AppBar:
    """
    Constrói a AppBar. O parâmetro 'p' é o dicionário de cores (tema ativo).
    """
    return ft.AppBar(
        # O 'leading' é exibido apenas no modo mobile para abrir o menu lateral
        leading=ft.IconButton(
            icon=ft.Icons.MENU,
            icon_color=p["txt_titulo"],
            on_click=lambda e: page.show_dialog(
                # BottomSheet cria um painel que desliza de baixo para cima
                ft.BottomSheet(
                    content=ft.Container(
                        content=menu_lateral(p, navegar_callback),
                        padding=10,
                        bgcolor=p["bg_sidebar"],
                    )
                )
            ),
        )
        if estado["mobile"]
        else None,
        title=ft.Text(
            APP_NAME, color=p["txt_titulo"], weight=ft.FontWeight.BOLD, size=16
        ),
        center_title=False,
        bgcolor=p["bg_sidebar"],
        # Ações à direita da AppBar (ícone de tema e menu de usuário)
        actions=[
            ft.IconButton(
                icon=ft.Icons.DARK_MODE
                if estado["tema"] == "escuro"
                else ft.Icons.LIGHT_MODE,
                icon_color=p["txt_titulo"],
                on_click=alternar_tema_callback,
            ),
            ft.PopupMenuButton(
                items=[
                    # Exibe usuário logado (item apenas para leitura)
                    ft.PopupMenuItem(
                        content=ft.Text("Perfil: " + estado["usuario"]),
                        disabled=True,
                    ),
                    # Link para configurações
                    ft.PopupMenuItem(
                        content=ft.Text("Configurações"),
                        on_click=lambda e: navegar_callback("/config"),
                    ),
                ]
            ),
        ],
    )
