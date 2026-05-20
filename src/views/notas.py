# ==============================================================================
# views/notas.py
# Interface de CRUD para anotações.
# ==============================================================================
from datetime import datetime

import flet as ft

from src.core.state import dados_notas
from src.core.utils import border_all, exibir_notificacao


def view_notas(page: ft.Page, p: dict) -> ft.Container:
    nota_id_em_edicao = None

    titulo_input = ft.TextField(
        label="Título da Nota",
        prefix_icon=ft.Icons.TITLE,
        border_color=p["borda_padrao"],
        color=p["txt_card_valor"],
        label_style=ft.TextStyle(color=p["txt_card_label"]),
        width=400,
    )

    conteudo_input = ft.TextField(
        label="Conteúdo",
        prefix_icon=ft.Icons.DESCRIPTION,
        multiline=True,
        min_lines=4,
        max_lines=6,
        border_color=p["borda_padrao"],
        color=p["txt_card_valor"],
        label_style=ft.TextStyle(color=p["txt_card_label"]),
        width=400,
    )

    categoria_dropdown = ft.Dropdown(
        label="Categoria",
        width=200,
        options=[
            ft.dropdown.Option("pessoal", "Pessoal"),
            ft.dropdown.Option("trabalho", "Trabalho"),
            ft.dropdown.Option("ideias", "Ideias"),
            ft.dropdown.Option("importante", "Importante"),
        ],
        value="pessoal",
        border_color=p["borda_padrao"],
        color=p["txt_card_valor"],
        label_style=ft.TextStyle(color=p["txt_card_label"]),
    )

    importante_switch = ft.Switch(
        label="Marcar como importante",
        value=False,
        active_color=p["borda_blue"],
        label_text_style=ft.TextStyle(color=p["txt_card_valor"]),
    )

    btn_salvar = ft.FilledButton(
        "Salvar Nota",
        icon=ft.Icons.SAVE,
        color=p["txt_card_valor"],
        bgcolor=p["borda_blue"],
        on_click=lambda e: salvar_nota(e),
    )

    lista_notas = ft.Column(spacing=10)

    def carregar_nota_para_edicao(nota: dict):
        nonlocal nota_id_em_edicao
        nota_id_em_edicao = nota["id"]
        titulo_input.value = nota["titulo"]
        conteudo_input.value = nota["conteudo"]
        categoria_dropdown.value = nota["categoria"]
        importante_switch.value = nota["importante"]
        btn_salvar.content = "Atualizar Nota"
        btn_salvar.icon = ft.Icons.EDIT
        btn_salvar.bgcolor = p["borda_dica"]
        page.update()

    def limpar_formulario_nota():
        nonlocal nota_id_em_edicao
        nota_id_em_edicao = None
        titulo_input.value = ""
        conteudo_input.value = ""
        categoria_dropdown.value = "pessoal"
        importante_switch.value = False
        btn_salvar.content = "Salvar Nota"
        btn_salvar.icon = ft.Icons.SAVE
        btn_salvar.bgcolor = p["borda_blue"]

    def atualizar_lista_notas():
        lista_notas.controls.clear()

        for nota in dados_notas:
            categoria_color = {
                "trabalho": p["borda_red"],
                "pessoal": p["borda_blue"],
                "ideias": p["borda_green"],
                "importante": p["borda_dica"],
            }.get(nota["categoria"], p["borda_padrao"])

            card_controls: list[ft.Control] = [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(
                                            nota["titulo"],
                                            size=13,
                                            weight=ft.FontWeight.BOLD,
                                            color=p["txt_card_valor"],
                                        ),
                                        ft.Icon(
                                            ft.Icons.STAR
                                            if nota["importante"]
                                            else ft.Icons.STAR_OUTLINE,
                                            size=14,
                                            color=p["borda_dica"]
                                            if nota["importante"]
                                            else p["txt_card_label"],
                                        ),
                                    ],
                                    spacing=5,
                                ),
                                ft.Text(
                                    nota["conteudo"],
                                    size=11,
                                    color=p["txt_subtitulo"],
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
                                    tooltip="Editar nota",
                                    on_click=lambda e, n=nota: (
                                        carregar_nota_para_edicao(n)
                                    ),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color=p["borda_red"],
                                    tooltip="Deletar nota",
                                    on_click=lambda e, nid=nota["id"]: deletar_nota(
                                        nid
                                    ),
                                ),
                            ],
                            spacing=0,
                        ),
                    ],
                    spacing=10,
                ),
                ft.Row(
                    [
                        ft.Text(
                            f"📅 {nota['data']}", size=9, color=p["txt_card_label"]
                        ),
                        ft.Text(
                            f"📌 {nota['categoria'].upper()}",
                            size=9,
                            color=categoria_color,
                        ),
                    ],
                    spacing=15,
                ),
            ]

            nota_card = ft.Container(
                content=ft.Column(controls=card_controls, spacing=8),
                padding=15,
                bgcolor=p["bg_card"],
                border=border_all(1, categoria_color),
                border_radius=8,
            )
            lista_notas.controls.append(nota_card)

        page.update()

    def salvar_nota(e):
        nonlocal nota_id_em_edicao
        if not titulo_input.value or not conteudo_input.value:
            exibir_notificacao(
                page, "Preencha o título e o conteúdo da nota!", sucesso=False
            )
            return

        if nota_id_em_edicao is not None:
            for nota in dados_notas:
                if nota["id"] == nota_id_em_edicao:
                    nota["titulo"] = titulo_input.value
                    nota["conteudo"] = conteudo_input.value
                    nota["categoria"] = categoria_dropdown.value or "pessoal"
                    nota["importante"] = importante_switch.value
                    break
            exibir_notificacao(page, "Nota atualizada com sucesso!")
        else:
            nova_nota = {
                "id": max([n["id"] for n in dados_notas], default=0) + 1,
                "titulo": titulo_input.value,
                "conteudo": conteudo_input.value,
                "data": datetime.now().strftime("%d/%m/%Y"),
                "categoria": categoria_dropdown.value or "pessoal",
                "importante": importante_switch.value,
                "tags": [],
            }
            dados_notas.append(nova_nota)
            exibir_notificacao(page, "Nova nota criada com sucesso!")

        limpar_formulario_nota()
        atualizar_lista_notas()

    def deletar_nota(nota_id):
        # Substitui a lista via slice para não perder referência na memória
        dados_notas[:] = [n for n in dados_notas if n["id"] != nota_id]
        exibir_notificacao(page, "Nota excluída.")
        if nota_id_em_edicao == nota_id:
            limpar_formulario_nota()
        atualizar_lista_notas()

    atualizar_lista_notas()

    form_controls: list[ft.Control] = [
        ft.Text(
            "Informações da Nota",
            size=14,
            weight=ft.FontWeight.BOLD,
            color=p["txt_titulo"],
        ),
        titulo_input,
        conteudo_input,
        ft.Row([categoria_dropdown, importante_switch], spacing=15),
        ft.Row(
            [
                btn_salvar,
                ft.TextButton("Cancelar", on_click=lambda e: limpar_formulario_nota()),
            ],
            spacing=10,
        ),
    ]

    main_controls: list[ft.Control] = [
        ft.Text(
            "Minhas Notas",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=p["txt_titulo"],
        ),
        ft.Divider(height=20, color=p["txt_divider"]),
        ft.Container(
            content=ft.Column(controls=form_controls, spacing=10),
            padding=20,
            bgcolor=p["bg_card"],
            border=border_all(2, p["borda_blue"]),
            border_radius=10,
        ),
        ft.Divider(height=20, color=p["txt_divider"]),
        ft.Text(
            f"Total de Notas: {len(dados_notas)}", size=12, color=p["txt_subtitulo"]
        ),
        lista_notas,
    ]

    return ft.Container(
        content=ft.Column(
            controls=main_controls, spacing=15, scroll=ft.ScrollMode.AUTO
        ),
        padding=20,
        bgcolor=p["bg_page"],
        expand=True,
    )
