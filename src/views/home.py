# ==============================================================================
# views/home.py
# Dashboard principal.
#
# ARQUITETURA DO CLIMA:
# - Cache síncrono: se o cache for válido (<30min), os controles são populados
#   ANTES da view ser retornada — sem thread, sem flash de "Carregando...".
# - Busca assíncrona: usa page.run_task() para garantir que page.update()
#   seja processado no event loop do Flet, evitando o bug de UI não atualizar
#   ao chamar update() de uma threading.Thread comum.
# ==============================================================================

import asyncio
import json
from datetime import datetime, timedelta

import flet as ft

from src.core import database as db
from src.core import weather
from src.core.state import estado
from src.core.utils import border_all, controls_list

_CIDADE_PADRAO = "Lages"
_CACHE_TTL_MIN = 30


# ==============================================================================
# Helpers de cache
# ==============================================================================


def _cache_valido() -> bool:
    ts_str = db.get_config("clima_cache_ts", "")
    if not ts_str:
        return False
    try:
        return datetime.now() - datetime.fromisoformat(ts_str) < timedelta(
            minutes=_CACHE_TTL_MIN
        )
    except ValueError:
        return False


def _salvar_cache(dados: dict, nome_cidade: str) -> None:
    db.set_config("clima_cache", json.dumps({"dados": dados, "cidade": nome_cidade}))
    db.set_config("clima_cache_ts", datetime.now().isoformat())


def _carregar_cache() -> tuple[dict, str] | None:
    raw = db.get_config("clima_cache", "")
    if not raw:
        return None
    try:
        obj = json.loads(raw)
        return obj["dados"], obj["cidade"]
    except (json.JSONDecodeError, KeyError):
        return None


def _label_cache() -> str:
    ts_str = db.get_config("clima_cache_ts", "")
    if not ts_str:
        return ""
    try:
        ts = datetime.fromisoformat(ts_str)
        return f"Atualizado às {ts.strftime('%H:%M')}"
    except ValueError:
        return ""


# ==============================================================================
# View
# ==============================================================================


def view_home(page: ft.Page, p: dict) -> ft.Container:

    # ------------------------------------------------------------------ stats
    todas_notas = db.listar_notas()
    todas_tarefas = db.listar_tarefas()
    total_notas = len(todas_notas)
    total_tarefas = len(todas_tarefas)
    concluidas = sum(1 for t in todas_tarefas if t["concluida"])
    pendentes = total_tarefas - concluidas
    progresso = (concluidas / total_tarefas * 100) if total_tarefas > 0 else 0

    def card_stat(
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

    secao_resumo = ft.Column(
        [
            ft.Text(
                "Resumo", size=16, weight=ft.FontWeight.BOLD, color=p["txt_titulo"]
            ),
            ft.Row(
                [
                    card_stat(
                        "Total de Notas",
                        str(total_notas),
                        ft.Icons.NOTE_OUTLINED,
                        p["borda_blue"],
                    ),
                    card_stat(
                        "Tarefas Pendentes",
                        str(pendentes),
                        ft.Icons.ASSIGNMENT_OUTLINED,
                        p["borda_red"],
                    ),
                    card_stat(
                        "Concluídas",
                        str(concluidas),
                        ft.Icons.CHECK_CIRCLE_OUTLINED,
                        p["borda_green"],
                    ),
                ],
                spacing=15,
                wrap=True,
            ),
        ],
        spacing=10,
        expand=True,
    )

    # --------------------------------------------------------------- progresso
    secao_progresso = ft.Column(
        [
            ft.Text(
                "Meu Progresso",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=p["txt_titulo"],
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Progresso de Tarefas",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=p["txt_titulo"],
                        ),
                        ft.Row(
                            [
                                ft.Slider(
                                    min=0,
                                    max=100,
                                    value=progresso,
                                    disabled=True,
                                    width=220,
                                    height=40,
                                    active_color=p["borda_green"],
                                    inactive_color=p["borda_padrao"],
                                ),
                                ft.Text(
                                    f"{progresso:.1f}%",
                                    size=12,
                                    color=p["txt_subtitulo"],
                                ),
                            ],
                            spacing=10,
                        ),
                    ],
                    spacing=10,
                ),
                padding=20,
                bgcolor=p["bg_card"],
                border=border_all(1, p["borda_green"]),
                border_radius=10,
            ),
        ],
        spacing=10,
        expand=True,
    )

    # ----------------------------------------------------------- últimas notas
    notas_col = ft.Column(spacing=8)
    for nota in todas_notas[:3]:
        notas_col.controls.append(
            ft.Container(
                content=ft.Column(
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
                    ],
                    spacing=5,
                ),
                padding=15,
                bgcolor=p["bg_card"],
                border=border_all(1, p["borda_padrao"]),
                border_radius=8,
            )
        )

    secao_notas = ft.Column(
        [
            ft.Text(
                "Últimas Notas",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=p["txt_titulo"],
            ),
            notas_col,
        ],
        spacing=10,
        expand=True,
    )

    # ------------------------------------------------------------------ clima
    cidade_salva = db.get_config("cidade_clima", _CIDADE_PADRAO)

    # Popula os valores iniciais de forma síncrona a partir do cache.
    # Isso evita o flash de "Carregando..." ao trocar de página/tema.
    _cache_inicial = _carregar_cache() if _cache_valido() else None

    if _cache_inicial:
        _dados_ini, _cidade_ini = _cache_inicial
        _emoji_ini = _dados_ini["emoji"]
        _temp_ini = f"{_dados_ini['temperatura']}°C"
        _desc_ini = _dados_ini["descricao"]
        _detalhes_ini = f"💧 Umidade: {_dados_ini['umidade']}%   💨 Vento: {_dados_ini['vento']} km/h"
        _cache_label = _label_cache()
        _cidade_nome_ini = _cidade_ini
    else:
        _emoji_ini = "🌡️"
        _temp_ini = "--°C"
        _desc_ini = "Carregando..."
        _detalhes_ini = ""
        _cache_label = ""
        _cidade_nome_ini = cidade_salva

    txt_emoji = ft.Text(_emoji_ini, size=40)
    txt_temp = ft.Text(
        _temp_ini, size=28, weight=ft.FontWeight.BOLD, color=p["txt_card_valor"]
    )
    txt_descricao = ft.Text(_desc_ini, size=12, color=p["txt_subtitulo"])
    txt_detalhes = ft.Text(_detalhes_ini, size=11, color=p["txt_card_label"])
    txt_cidade_nome = ft.Text(
        _cidade_nome_ini, size=13, weight=ft.FontWeight.BOLD, color=p["txt_titulo"]
    )
    txt_cache_info = ft.Text(
        _cache_label, size=9, color=p["txt_card_label"], italic=True
    )
    txt_erro = ft.Text("", size=10, color=p["borda_red"], italic=True)

    cidade_input = ft.TextField(
        value=cidade_salva,
        label="Digite a cidade",
        width=180,
        border_color=p["borda_padrao"],
        color=p["txt_card_valor"],
        label_style=ft.TextStyle(color=p["txt_card_label"]),
        visible=False,
        on_submit=lambda e: page.run_task(_confirmar_cidade),
    )
    btn_confirmar = ft.IconButton(
        icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
        icon_color=p["borda_green"],
        tooltip="Confirmar cidade",
        visible=False,
        on_click=lambda e: page.run_task(_confirmar_cidade),
    )
    btn_editar = ft.IconButton(
        icon=ft.Icons.EDIT_LOCATION_ALT_OUTLINED,
        icon_color=p["borda_blue"],
        tooltip="Alterar cidade",
        on_click=lambda e: page.run_task(_mostrar_input),
    )
    btn_refresh = ft.IconButton(
        icon=ft.Icons.REFRESH,
        icon_color=p["txt_card_label"],
        tooltip="Forçar atualização",
        on_click=lambda e: page.run_task(_forcar_busca),
    )

    def _aplicar(dados: dict, nome: str):
        txt_cidade_nome.value = nome
        txt_emoji.value = dados["emoji"]
        txt_temp.value = f"{dados['temperatura']}°C"
        txt_descricao.value = dados["descricao"]
        txt_detalhes.value = (
            f"💧 Umidade: {dados['umidade']}%   💨 Vento: {dados['vento']} km/h"
        )
        txt_cache_info.value = _label_cache()
        txt_erro.value = ""

    async def _mostrar_input():
        cidade_input.visible = True
        btn_confirmar.visible = True
        btn_editar.visible = False
        page.update()

    async def _confirmar_cidade():
        nova = (cidade_input.value or "").strip()
        if not nova:
            return
        cidade_input.visible = False
        btn_confirmar.visible = False
        btn_editar.visible = True
        txt_descricao.value = "Buscando..."
        txt_temp.value = "--°C"
        txt_detalhes.value = ""
        txt_cache_info.value = ""
        txt_erro.value = ""
        page.update()

        db.set_config("cidade_clima", nova)
        db.set_config("clima_cache_ts", "")  # invalida cache
        await _buscar(nova)

    async def _forcar_busca():
        db.set_config("clima_cache_ts", "")
        txt_descricao.value = "Atualizando..."
        txt_cache_info.value = ""
        page.update()
        cidade = db.get_config("cidade_clima", _CIDADE_PADRAO)
        await _buscar(cidade)

    async def _buscar(cidade: str):
        """
        Executa a chamada HTTP em uma thread de I/O separada (via asyncio.to_thread)
        para não bloquear o event loop do Flet, e usa update_async() para garantir
        que o render aconteça imediatamente após os dados chegarem.
        """
        resultado = await asyncio.to_thread(weather.buscar_clima_cidade, cidade)

        if resultado is None:
            txt_emoji.value = "❌"
            txt_temp.value = "--°C"
            txt_descricao.value = "Indisponível"
            txt_detalhes.value = ""
            txt_erro.value = f"Não foi possível obter o clima para '{cidade}'."
        else:
            dados, nome = resultado
            _aplicar(dados, nome)
            _salvar_cache(dados, nome)
            db.set_config("cidade_clima", nome)

        page.update()

    # Só dispara busca se o cache estava ausente/expirado
    if _cache_inicial is None:
        page.run_task(_buscar, cidade_salva)

    # ----------------------------------------------------------------- card clima
    card_clima = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.LOCATION_ON_OUTLINED,
                            size=16,
                            color=p["borda_blue"],
                        ),
                        txt_cidade_nome,
                        btn_editar,
                        btn_refresh,
                        cidade_input,
                        btn_confirmar,
                    ],
                    spacing=4,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    [txt_emoji, ft.Column([txt_temp, txt_descricao], spacing=2)],
                    spacing=15,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                txt_detalhes,
                txt_cache_info,
                txt_erro,
            ],
            spacing=10,
        ),
        padding=20,
        bgcolor=p["bg_card"],
        border=border_all(2, p["borda_blue"]),
        border_radius=10,
        shadow=ft.BoxShadow(
            spread_radius=1, blur_radius=4, color=p["sombra"], offset=ft.Offset(0, 2)
        ),
    )

    secao_clima = ft.Column(
        [
            ft.Text(
                "Clima Atual", size=16, weight=ft.FontWeight.BOLD, color=p["txt_titulo"]
            ),
            card_clima,
        ],
        spacing=10,
        expand=True,
    )

    # ----------------------------------------------------------------- layout
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    f"Bem-vindo, {estado['usuario']}! 👋",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=p["txt_titulo"],
                ),
                ft.Divider(height=20, color=p["txt_divider"]),
                ft.Row(
                    [secao_resumo, secao_progresso],
                    spacing=20,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Divider(height=20, color=p["txt_divider"]),
                ft.Row(
                    [secao_notas, secao_clima],
                    spacing=20,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        bgcolor=p["bg_page"],
        expand=True,
    )
