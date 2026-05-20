# ==============================================================================
# core/utils.py
# Funções utilitárias reaproveitáveis em várias partes do sistema.
# ==============================================================================
import flet as ft

from src.core.state import estado
from src.core.theme import PALETAS


def controls_list(*items: ft.Control) -> list[ft.Control]:
    return list(items)


def border_all(width: int, color: str) -> ft.Border:
    """Estilo utilitário para bordas compatível com Flet 0.85.1"""
    side = ft.BorderSide(width, color)
    return ft.Border(top=side, bottom=side, left=side, right=side)


def exibir_notificacao(page: ft.Page, mensagem: str, sucesso: bool = True):
    """Exibe feedback visual usando o SnackBar do Flet"""
    p = PALETAS[estado["tema"]]
    page.show_dialog(
        ft.SnackBar(
            content=ft.Text(
                mensagem, color=p["txt_card_valor"], weight=ft.FontWeight.BOLD
            ),
            bgcolor=p["borda_green"] if sucesso else p["borda_red"],
            duration=2000,
            show_close_icon=True,
        )
    )
