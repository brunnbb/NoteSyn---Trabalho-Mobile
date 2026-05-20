# ==============================================================================
# main.py
# O orquestrador central: gerencia o estado da tela, roteamento e responsividade.
# ==============================================================================
import flet as ft

from src.components.appbar import construir_appbar
from src.components.sidebar import menu_lateral
from src.core.constants import APP_NAME, BREAKPOINT_MOBILE
from src.core.state import estado
from src.core.theme import PALETAS
from src.core.utils import controls_list
from src.views.agenda import view_agenda
from src.views.config import view_config
from src.views.home import view_home
from src.views.notas import view_notas
from src.views.tarefas import view_tarefas


def main(page: ft.Page):
    # Configurações iniciais da janela/página
    page.title = APP_NAME
    page.padding = 0
    page.spacing = 0

    # Define o estado inicial de responsividade com base na largura da janela
    largura_atual = page.window.width or 800
    estado["mobile"] = largura_atual < BREAKPOINT_MOBILE

    def alternar_tema(e=None):
        """Alterna a flag de tema no estado e força a renderização da interface."""
        estado["tema"] = "claro" if estado["tema"] == "escuro" else "escuro"
        route_change()

    def navegar(rota: str):
        """Atualiza a rota atual e força a atualização da UI."""
        estado["rota"] = rota
        route_change()

    def route_change(*args):
        """
        Função principal que reconstrói a view toda vez que algo altera
        o estado ou a rota (Single Page Application Approach).
        """
        p = PALETAS[estado["tema"]]
        rota = estado["rota"]

        # Mapa de rotas: associa a string da rota a uma função de renderização
        views_map = {
            "/": lambda p_dict: view_home(p_dict),
            "/notas": lambda p_dict: view_notas(page, p_dict),
            "/tarefas": lambda p_dict: view_tarefas(page, p_dict),
            "/agenda": lambda p_dict: view_agenda(page, p_dict),
            "/config": lambda p_dict: view_config(
                page, p_dict, alternar_tema, route_change
            ),
        }

        view_fn = views_map.get(rota, views_map["/"])
        appbar = construir_appbar(page, p, alternar_tema, navegar)

        # Lógica Responsiva: Se for Mobile, não mostra Sidebar, apenas conteúdo
        if estado["mobile"]:
            page.views.clear()
            page.views.append(
                ft.View(
                    route=rota,
                    controls=[view_fn(p)],
                    appbar=appbar,
                    bgcolor=p["bg_page"],
                )
            )
        # Se for Desktop, coloca a Sidebar e a View lado a lado
        else:
            conteudo = ft.Row(
                controls_list(menu_lateral(p, navegar), view_fn(p)),
                expand=True,
                spacing=0,
            )
            page.views.clear()
            page.views.append(
                ft.View(
                    route=rota,
                    controls=[conteudo],
                    appbar=appbar,
                    bgcolor=p["bg_page"],
                )
            )
        page.update()

    def on_resize(e: ft.PageResizeEvent):
        """Monitora mudanças no tamanho da janela para alternar entre mobile/desktop."""
        novo_mobile = e.width < BREAKPOINT_MOBILE
        if novo_mobile != estado["mobile"]:
            estado["mobile"] = novo_mobile
            route_change()

    page.on_resize = on_resize
    route_change()  # Executa pela primeira vez


if __name__ == "__main__":
    ft.run(main)
