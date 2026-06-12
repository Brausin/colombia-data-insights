"""
ui.py — Sistema de diseño BI para el dashboard colombia-data-insights.

Sistema de diseño (ui-ux-pro-max · "Data-Dense Dashboard", tema oscuro
profesional — design-system/colombia-data-insights/MASTER.md):

    - Fondo #020617 (slate-950) con paneles #0F172A y bordes hairline #1E2A44.
    - Acentos de dato: verde #22C55E (positivo/acción), rojo #EF4444 (negativo),
      cian #38BDF8 (serie primaria), ámbar #F59E0B (alertas). El amarillo
      bandera #FFD100 se reserva como acento de marca (wordmark y tab activa).
    - Tipografía Fira Sans (UI) + Fira Code (cifras, tabular por diseño).
    - Iconos SVG inline (trazo Lucide) y Material Symbols en tabs;
      nunca emojis como iconos.
    - Hover sin saltos de layout (borde/sombra, 150–250 ms), focus visible,
      prefers-reduced-motion respetado, contraste mínimo 4.5:1.
    - Componentes propios para KPI, callouts y estados vacíos; nunca
      st.metric (rompe el tema) ni alertas con emoji.

Centraliza la paleta, el CSS global, los componentes HTML y registra un
template oscuro de Plotly que se aplica a todos los gráficos del tablero.
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

# ── Paleta "Data-Dense Dashboard" (ui-ux-pro-max) ────────────────────────────
COLORS = {
    "bg": "#020617",        # fondo slate-950
    "card": "#0F172A",      # panel
    "card2": "#111C33",     # panel elevado (hover/tooltip)
    "border": "#1E2A44",    # hairline
    "border2": "#334155",   # borde fuerte (inputs)
    "yellow": "#FFD100",    # marca Colombia (wordmark, tab activa)
    "blue": "#3B82F6",      # azul de apoyo
    "red": "#F87171",       # negativo en TEXTO (7:1 sobre bg)
    "red_chart": "#EF4444", # negativo en gráficos/rellenos
    "green": "#22C55E",     # acción / positivo en gráficos
    "c1": "#38BDF8",        # serie 1 · cian
    "c2": "#34D399",        # serie 2 · esmeralda (texto-seguro)
    "c3": "#F59E0B",        # serie 3 · ámbar
    "violet": "#A78BFA",    # serie 4 · violeta
    "text": "#F8FAFC",
    "muted": "#94A3B8",     # 7.8:1 sobre #020617
}

_GRID = "#16213B"
_TEMPLATE = "cdi_dark"
_FONT_UI = "'Fira Sans','Segoe UI',sans-serif"
_FONT_NUM = "'Fira Code',ui-monospace,monospace"


def _rgba(hex6: str, alpha: float) -> str:
    """Convierte ``#RRGGBB`` + alpha (0–1) a ``rgba(r,g,b,a)``."""
    h = hex6.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{alpha})"


# ── Iconos SVG (trazo estilo Lucide, viewBox 24×24) ──────────────────────────
ICONS = {
    "info": "<circle cx='12' cy='12' r='10'/><path d='M12 16v-4M12 8h.01'/>",
    "check-circle": "<path d='M21.8 10A10 10 0 1 1 17 3.34'/>"
                    "<path d='m9 11 3 3L22 4'/>",
    "alert-triangle": "<path d='m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 "
                      "4 21h16a2 2 0 0 0 1.73-3Z'/><path d='M12 9v4M12 17h.01'/>",
    "alert-circle": "<circle cx='12' cy='12' r='10'/><path d='M12 8v4M12 16h.01'/>",
    "database": "<ellipse cx='12' cy='5' rx='9' ry='3'/>"
                "<path d='M3 5v14a9 3 0 0 0 18 0V5'/><path d='M3 12a9 3 0 0 0 18 0'/>",
    "trending-up": "<polyline points='22 7 13.5 15.5 8.5 10.5 2 17'/>"
                   "<polyline points='16 7 22 7 22 13'/>",
    "trending-down": "<polyline points='22 17 13.5 8.5 8.5 13.5 2 7'/>"
                     "<polyline points='16 17 22 17 22 11'/>",
    "refresh": "<path d='M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8'/>"
               "<path d='M21 3v5h-5'/>"
               "<path d='M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16'/>"
               "<path d='M8 16H3v5'/>",
    "search-x": "<path d='m13.5 8.5-5 5M8.5 8.5l5 5'/><circle cx='11' cy='11' r='8'/>"
                "<path d='m21 21-4.3-4.3'/>",
    "dollar": "<line x1='12' y1='2' x2='12' y2='22'/>"
              "<path d='M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6'/>",
    "flag": "<path d='M4 22V4a1 1 0 0 1 .4-.8A6 6 0 0 1 8 2c3 0 5 2 7.5 2q2 0 "
            "3.5-.5a1 1 0 0 1 1 .98V14a1 1 0 0 1-.4.8A6 6 0 0 1 16 16c-3 "
            "0-5-2-7.5-2a7 7 0 0 0-4.5 1.5'/>",
}


def icono(nombre: str, size: int = 18, color: str = COLORS["text"]) -> str:
    """Icono SVG inline (trazo 2px, estilo Lucide)."""
    return (
        f"<svg width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' "
        f"stroke='{color}' stroke-width='2' stroke-linecap='round' "
        f"stroke-linejoin='round' style='flex-shrink:0;vertical-align:-3px'>"
        f"{ICONS[nombre]}</svg>"
    )


# ── Tema Plotly ──────────────────────────────────────────────────────────────
def registrar_tema() -> None:
    """Registra y activa un template oscuro de Plotly para todo el tablero.

    Tras llamarla, cualquier figura de plotly.express / graph_objects hereda
    fondo transparente, texto claro, grid sutil y la paleta del design system
    (series con tonos distinguibles también para daltonismo).
    """
    tpl = go.layout.Template()
    tpl.layout = go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Fira Sans, sans-serif", color=COLORS["muted"], size=13),
        title=dict(font=dict(color=COLORS["text"], size=15,
                             family="Fira Sans, sans-serif"), x=0, xanchor="left"),
        colorway=[COLORS["c1"], COLORS["c2"], COLORS["c3"],
                  COLORS["violet"], COLORS["red_chart"], COLORS["yellow"]],
        xaxis=dict(gridcolor=_GRID, zerolinecolor=_GRID, linecolor=COLORS["border"],
                   color=COLORS["muted"], tickfont=dict(family="Fira Code, monospace",
                                                        size=11)),
        yaxis=dict(gridcolor=_GRID, zerolinecolor=_GRID, linecolor=COLORS["border"],
                   color=COLORS["muted"], tickfont=dict(family="Fira Code, monospace",
                                                        size=11)),
        hoverlabel=dict(bgcolor=COLORS["card2"], bordercolor=COLORS["border2"],
                        font=dict(family="Fira Sans", color=COLORS["text"], size=13)),
        legend=dict(font=dict(color=COLORS["muted"])),
        margin=dict(l=10, r=10, t=48, b=10),
    )
    pio.templates[_TEMPLATE] = tpl
    pio.templates.default = _TEMPLATE


# ── CSS global ───────────────────────────────────────────────────────────────
def apply_styles(C: dict = COLORS) -> None:
    """Inyecta el CSS global del tablero (fuentes, fondos, inputs, tabs)."""
    st.markdown(
        f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@400;500;600;700&family=Fira+Code:wght@400;500;600&display=swap');
    html,body,[class*="css"] {{font-family:{_FONT_UI}}}
    .stApp,[data-testid="stAppViewContainer"] {{background:{C['bg']}}}
    #MainMenu,footer,header {{visibility:hidden}}
    .block-container {{padding-top:1.6rem;padding-bottom:3rem;max-width:1280px}}

    h1,h2,h3,h4 {{font-family:{_FONT_UI};color:{C['text']}!important;
        letter-spacing:-.01em}}
    h3 {{font-size:1.25rem!important}}
    p,span,label,li,div[data-testid="stMarkdownContainer"] {{color:{C['text']}}}
    .stCaption,.stCaption p,div[data-testid="stCaptionContainer"] p,small {{
        color:{C['muted']}!important}}
    ::selection {{background:{_rgba('#22C55E', .35)}}}
    ::-webkit-scrollbar {{width:10px;height:10px}}
    ::-webkit-scrollbar-track {{background:transparent}}
    ::-webkit-scrollbar-thumb {{background:{C['border2']};border-radius:6px}}
    ::-webkit-scrollbar-thumb:hover {{background:#48566E}}

    /* Inputs: panel oscuro, foco verde visible */
    .stTextInput input,.stNumberInput input,.stDateInput input,
    textarea,.stTextArea textarea {{
        background:{C['card']}!important;color:{C['text']}!important;
        font-family:{_FONT_NUM};font-variant-numeric:tabular-nums;
        border:1px solid {C['border2']}!important;border-radius:8px!important;
        transition:border-color 180ms ease,box-shadow 180ms ease}}
    .stTextInput input:focus,.stNumberInput input:focus,
    .stDateInput input:focus,.stTextArea textarea:focus {{
        border-color:{C['green']}!important;
        box-shadow:0 0 0 2px {_rgba('#22C55E', .30)}!important}}
    .stNumberInput button {{background:transparent!important;
        color:{C['muted']}!important;cursor:pointer}}
    .stNumberInput button:hover {{color:{C['text']}!important}}
    div[data-baseweb="select"]>div,div[data-baseweb="input"]>div {{
        background:{C['card']}!important;border:1px solid {C['border2']}!important;
        border-radius:8px!important;color:{C['text']}!important;cursor:pointer;
        transition:border-color 180ms ease}}
    div[data-baseweb="select"]>div:hover {{border-color:{_rgba('#22C55E', .6)}!important}}
    ul[data-testid="stSelectboxVirtualDropdown"],div[data-baseweb="popover"] ul {{
        background:{C['card2']}!important;border:1px solid {C['border']}!important}}
    li[role="option"] {{cursor:pointer}}

    /* Multiselect: chips legibles */
    .stMultiSelect span[data-baseweb="tag"] {{
        background:{_rgba('#38BDF8', .16)}!important;color:{C['c1']}!important;
        border:1px solid {_rgba('#38BDF8', .4)};border-radius:14px}}
    .stMultiSelect span[data-baseweb="tag"] span {{color:{C['c1']}!important}}

    /* Botones */
    .stButton>button,.stDownloadButton>button {{
        background:{_rgba('#22C55E', .14)}!important;color:#4ADE80!important;
        border:1px solid {_rgba('#22C55E', .45)}!important;border-radius:8px!important;
        font-weight:600!important;cursor:pointer!important;
        transition:background 180ms ease,box-shadow 180ms ease!important}}
    .stButton>button:hover,.stDownloadButton>button:hover {{
        background:{_rgba('#22C55E', .24)}!important;
        box-shadow:0 4px 18px {_rgba('#22C55E', .25)}!important}}
    .stButton>button:focus-visible,.stDownloadButton>button:focus-visible {{
        outline:2px solid {C['yellow']}!important;outline-offset:2px!important}}

    /* Tabs: subrayado amarillo de marca, hover suave */
    .stTabs [data-baseweb="tab-list"] {{gap:2px;border-bottom:1px solid {C['border']}}}
    .stTabs [data-baseweb="tab"] {{
        color:{C['muted']}!important;border-radius:8px 8px 0 0;
        padding:0 14px;cursor:pointer;
        transition:color 160ms ease,background 160ms ease}}
    .stTabs [data-baseweb="tab"]:hover {{
        color:{C['text']}!important;background:{_rgba('#38BDF8', .07)}}}
    .stTabs [aria-selected="true"] {{color:{C['text']}!important}}
    .stTabs [data-baseweb="tab-highlight"] {{background:{C['yellow']}!important;
        height:2px}}
    .stTabs [data-baseweb="tab"]:focus-visible {{
        outline:2px solid {C['yellow']}!important;outline-offset:-2px}}

    /* Slider y radio heredan primaryColor (config.toml); etiquetas legibles */
    .stSlider label,.stSelectbox label,.stNumberInput label,
    .stMultiSelect label,.stTextInput label {{color:{C['muted']}!important;
        font-size:13px!important}}
    .stSlider [data-testid="stTickBar"] div {{color:{C['muted']}!important}}
    .stSlider [data-testid="stSliderThumbValue"] {{
        font-family:{_FONT_NUM};color:{C['green']}!important}}

    /* Alertas nativas (respaldo): panel con borde, sin fondo chillón */
    .stAlert {{background:{C['card']}!important;
        border:1px solid {C['border']}!important;border-radius:10px!important}}
    .stAlert p {{color:{C['text']}!important}}
    div[data-testid="stExpander"] {{background:{C['card']}!important;
        border:1px solid {C['border']}!important;border-radius:10px!important}}
    div[data-testid="stExpander"] summary {{cursor:pointer}}
    div[data-testid="stExpander"] summary:focus-visible {{
        outline:2px solid {C['yellow']};outline-offset:2px}}
    .stDataFrame {{border:1px solid {C['border']}!important;border-radius:10px!important}}
    hr {{border-color:{C['border']}!important}}
    div[data-testid="stHorizontalBlock"] {{gap:.8rem}}
    code {{font-family:{_FONT_NUM}!important}}

    /* Spinner del tema */
    .stSpinner>div {{border-top-color:{C['green']}!important}}

    /* Tarjetas KPI */
    .cdi-kpi {{
        background:{C['card']};border:1px solid {C['border']};
        border-radius:12px;padding:14px 18px;height:100%;position:relative;
        overflow:hidden;
        transition:border-color 200ms ease,box-shadow 200ms ease}}
    .cdi-kpi:hover {{border-color:{C['border2']};
        box-shadow:0 8px 26px rgba(2,6,23,.6)}}
    .cdi-num {{font-family:{_FONT_NUM};font-variant-numeric:tabular-nums}}

    /* Responsive */
    @media (max-width: 740px) {{
        .block-container {{padding-left:1rem;padding-right:1rem;padding-top:1rem}}
        .cdi-kpi {{padding:12px 14px}}
    }}
    @media (prefers-reduced-motion: reduce) {{
        * {{transition:none!important;animation:none!important;
            scroll-behavior:auto!important}}
    }}
    </style>""",
        unsafe_allow_html=True,
    )


# ── Componentes HTML ─────────────────────────────────────────────────────────
def md(html: str) -> None:
    """Renderiza HTML custom."""
    st.markdown(html, unsafe_allow_html=True)


def header_app(titulo: str, subtitulo: str = "") -> str:
    """Encabezado de marca: wordmark + hairline tricolor (bandera abstracta)."""
    sub = (f"<div style='color:{COLORS['muted']};font-size:14px;margin-top:6px'>"
           f"{subtitulo}</div>") if subtitulo else ""
    return (
        f"<div style='margin:0 0 14px'>"
        f"<div style='display:flex;align-items:center;gap:12px'>"
        f"<div style='display:flex;flex-direction:column;gap:3px;width:26px'>"
        f"<span style='height:8px;border-radius:2px;background:{COLORS['yellow']}'></span>"
        f"<span style='height:4px;border-radius:2px;background:#2563EB'></span>"
        f"<span style='height:4px;border-radius:2px;background:#DC2626'></span></div>"
        f"<span style='font-size:30px;font-weight:700;letter-spacing:-.02em;"
        f"color:{COLORS['text']}'>{titulo}</span></div>{sub}</div>"
    )


def kpi(label: str, valor: str, delta: str = "", color: str = COLORS["c1"],
        ayuda: str = "") -> str:
    """Tarjeta KPI en HTML (reemplaza st.metric, compatible con tema oscuro)."""
    d = (f"<div style='color:{color};font-size:12px;font-weight:600;margin-top:4px'>"
         f"{delta}</div>") if delta else ""
    title = f" title='{ayuda}'" if ayuda else ""
    return (
        f"<div class='cdi-kpi'{title}>"
        f"<div style='position:absolute;inset:0 auto auto 0;width:100%;height:2px;"
        f"background:linear-gradient(90deg,{color},transparent 65%)'></div>"
        f"<div style=\"color:{COLORS['muted']};font-size:11px;font-weight:600;"
        f"text-transform:uppercase;letter-spacing:.05em\">{label}</div>"
        f"<div class='cdi-num' style=\"color:{COLORS['text']};font-size:25px;"
        f"font-weight:600;margin-top:5px\">{valor}</div>{d}</div>"
    )


def kpis_row(items: list[dict], gap: int = 12) -> str:
    """Fila de tarjetas KPI (ticker). Cada item: {label, valor, delta, color, ayuda}."""
    cards = "".join(
        f"<div style='flex:1;min-width:185px'>"
        f"{kpi(it['label'], it['valor'], it.get('delta', ''), it.get('color', COLORS['c1']), it.get('ayuda', ''))}"
        f"</div>"
        for it in items
    )
    return (f"<div style='display:flex;gap:{gap}px;flex-wrap:wrap;margin:8px 0 4px'>"
            f"{cards}</div>")


def badge(texto: str, color: str = COLORS["c2"]) -> str:
    """Etiqueta tipo pill con color de acento."""
    return (f"<span style='background:{color}22;color:{color};border:1px solid "
            f"{color}55;border-radius:20px;padding:2px 10px;font-size:11px;"
            f"font-weight:600'>{texto}</span>")


_CALLOUT = {
    "info":   ("info",           COLORS["c1"]),
    "exito":  ("check-circle",   COLORS["c2"]),
    "alerta": ("alert-triangle", COLORS["c3"]),
    "error":  ("alert-circle",   COLORS["red"]),
    "dato":   ("database",       COLORS["violet"]),
}


def callout(tipo: str, html: str, titulo: str = "") -> None:
    """Aviso con icono SVG (reemplaza st.info/warning/success con emojis).

    tipo: ``info`` · ``exito`` · ``alerta`` · ``error`` · ``dato``.
    """
    icn, color = _CALLOUT.get(tipo, _CALLOUT["info"])
    t = (f"<div style='font-weight:700;color:{COLORS['text']};margin-bottom:3px'>"
         f"{titulo}</div>") if titulo else ""
    md(
        f"<div style='display:flex;gap:11px;align-items:flex-start;"
        f"background:{COLORS['card']};border:1px solid {COLORS['border']};"
        f"border-left:3px solid {color};border-radius:10px;"
        f"padding:13px 16px;margin:10px 0'>"
        f"<span style='margin-top:1px'>{icono(icn, 18, color)}</span>"
        f"<div style='font-size:14px;color:{COLORS['text']};line-height:1.55'>"
        f"{t}{html}</div></div>"
    )


def empty_state(titulo: str, detalle: str = "", icn: str = "search-x") -> None:
    """Estado vacío explícito (sin datos, filtro sin resultados, CSV ausente)."""
    d = (f"<div style='color:{COLORS['muted']};font-size:13px;margin-top:5px;"
         f"max-width:430px'>{detalle}</div>") if detalle else ""
    md(
        f"<div style='display:flex;flex-direction:column;align-items:center;"
        f"justify-content:center;text-align:center;background:{COLORS['card']};"
        f"border:1px dashed {COLORS['border2']};border-radius:12px;"
        f"padding:34px 22px;margin:12px 0'>"
        f"{icono(icn, 30, COLORS['muted'])}"
        f"<div style='font-weight:600;font-size:15px;color:{COLORS['text']};"
        f"margin-top:10px'>{titulo}</div>{d}</div>"
    )


def fuente_dato(texto: str) -> str:
    """Pie de gráfico/tabla con la fuente del dato."""
    return (f"<div style='display:flex;align-items:center;gap:6px;"
            f"color:{COLORS['muted']};font-size:11.5px;margin:-4px 0 8px'>"
            f"{icono('database', 12, COLORS['muted'])}<span>{texto}</span></div>")
