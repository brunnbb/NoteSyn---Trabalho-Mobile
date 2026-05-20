# ==============================================================================
# views/config.py
# Tela para gerenciar preferências de usuário e tema.
# ==============================================================================

import flet as ft

from src.core.constants import APP_VERSION
from src.core.state import estado
from src.core.utils import exibir_notificacao


def view_config(
    page: ft.Page, p: dict, alternar_tema_callback, route_change_callback
) -> ft.Container:
    """
    Constrói a tela de configurações da aplicação.

    Responsabilidades:
    - Permitir alteração do nome do usuário
    - Alternar tema (claro/escuro)
    - Exibir informações ("Sobre")

    Parâmetros:
    - page: instância da página Flet (usada para notificações e updates)
    - p: dicionário de tema (cores dinâmicas)
    - alternar_tema_callback: função externa para alternar tema
    - route_change_callback: força re-render da rota após mudanças

    Retorna:
    - ft.Container com toda a UI da tela de configurações
    """

    # Campo de entrada vinculado ao estado global do usuário
    nome_input = ft.TextField(
        label="Nome de Usuário",
        value=estado["usuario"],  # valor inicial vindo do estado global
        border_color=p["borda_padrao"],
        color=p["txt_card_valor"],
        label_style=ft.TextStyle(color=p["txt_card_label"]),
        width=300,
    )

    def salvar_configs(e):
        """
        Salva as configurações do usuário.

        Fluxo:
        1. Valida input
        2. Atualiza estado global
        3. Exibe feedback
        4. Força re-render da aplicação (via callback de rota)
        """
        if nome_input.value:
            # Mutação direta do estado global
            estado["usuario"] = nome_input.value

            exibir_notificacao(page, "Configurações atualizadas!")

            # Necessário para refletir mudanças em outras partes da UI
            route_change_callback()
        else:
            exibir_notificacao(
                page,
                "O nome de usuário não pode estar vazio.",
                sucesso=False,
            )

    # ---------------------- LAYOUT ----------------------

    config_controls: list[ft.Control] = [
        # Título principal
        ft.Text(
            "Configurações Gerais",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=p["txt_titulo"],
        ),
        ft.Divider(height=20, color=p["txt_divider"]),
        # ---------------------- SEÇÃO: PERSONALIZAÇÃO ----------------------
        ft.Text(
            "Personalização",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=p["txt_titulo"],
        ),
        ft.Row(
            [
                ft.Text("Tema do Aplicativo:", color=p["txt_card_valor"]),
                # Botão alterna ícone dinamicamente conforme estado atual
                ft.IconButton(
                    icon=ft.Icons.DARK_MODE
                    if estado["tema"] == "escuro"
                    else ft.Icons.LIGHT_MODE,
                    icon_color=p["borda_dica"],
                    tooltip="Alternar Tema",
                    # Delega lógica de tema para camada externa
                    on_click=alternar_tema_callback,
                ),
            ],
            spacing=10,
        ),
        ft.Divider(height=10, color=p["txt_divider"]),
        # ---------------------- SEÇÃO: PERFIL ----------------------
        ft.Text(
            "Perfil",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=p["txt_titulo"],
        ),
        nome_input,
        ft.FilledButton(
            "Salvar Alterações",
            icon=ft.Icons.SAVE,
            color=p["txt_card_valor"],
            bgcolor=p["borda_blue"],
            # Executa validação + persistência em memória
            on_click=salvar_configs,
        ),
        ft.Divider(height=10, color=p["txt_divider"]),
        # ---------------------- SEÇÃO: SOBRE ----------------------
        ft.Text(
            "Sobre",
            size=14,
            weight=ft.FontWeight.BOLD,
            color=p["txt_titulo"],
        ),
        # Versão da aplicação (constante)
        ft.Text(
            f"NoteSync v{APP_VERSION}",
            size=12,
            color=p["txt_subtitulo"],
        ),
        ft.Text(
            "Sistema de Agenda e Notas Pessoal",
            size=11,
            color=p["txt_card_label"],
        ),
        ft.Text(
            "Desenvolvido com Python + Flet",
            size=10,
            color=p["txt_card_label"],
            italic=True,
        ),
    ]

    # Container principal da página
    return ft.Container(
        content=ft.Column(
            controls=config_controls,
            spacing=15,
        ),
        padding=20,
        bgcolor=p["bg_page"],
        expand=True,
    )
