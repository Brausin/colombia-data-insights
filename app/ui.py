"""
ui.py — Sistema de diseño BI para el dashboard colombia-data-insights.

Centraliza la paleta, el CSS global, los componentes HTML (tarjetas KPI,
ticker, badges, encabezado) y registra un template oscuro de Plotly que se
aplica a todos los gráficos del tablero. Evita los widgets por defecto que
rompen el tema oscuro (st.metric) usando tarjetas HTML propias.

Sistema de diseño (ui-ux-pro-max · Data-Dense Dashboard):
    - Tipografía Fira Sans (texto) + Fira Code (cifras), mood técnico/preciso.
    - Layout denso: padding contenido, KPIs compactos, grid eficiente.
    - Hover con feedback (tooltips, resaltado) sin saltos de layout.
    - Azul de datos + acentos bandera (amarillo/azul/rojo) para deltas.
    - Focus visible y respeto de prefers-reduced-motion.
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

# ── Paleta BI (bandera + acentos de dato) ────────────────────────────────────
COLORS = {
    "bg": "#0A0E1A",
    "card": "#111827",
    "border": "#243047",
    "yellow": "#FFD100",
    "blue": "#3B82F6",
    "red": "#CE1126",
    "c1": "#4F9CF9",
    "c2": "#48D0A4",
    "c3": "#F59E0B",
    "text": "#F1F5F9",
    "muted": "#94A3B8",
}

_GRID = "#1B2433"
_TEMPLATE = "cdi_dark"
_FONT = "'Fira Sans',sans-serif"
_FONT_NUM = "'Fira Code',monospace"


def registrar_tema() -> None:
    """Registra y activa un template oscuro de Plotly para todo el tablero.

    Tras llamarla, cualquier figura de plotly.express / graph_objects hereda
    fondo transparente, texto claro, grid sutil y la paleta de marca.
    """
    tpl = go.layout.Template()
    tpl.layout = go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Fira Sans, sans-serif", color=COLORS["muted"], size=13),
        title=dict(font=dict(color=COLORS["text"], size=16)),
        colorway=[COLORS["c1"], COLORS["c2"], COLORS["c3"],
                  COLORS["yellow"], COLORS["red"], COLORS["blue"]],
        xaxis=dict(gridcolor=_GRID, zerolinecolor=_GRID, linecolor=COLORS["border"],
                   color=COLORS["muted"]),
        yaxis=dict(gridcolor=_GRID, zerolinecolor=_GRID, linecolor=COLORS["border"],
                   color=COLORS["muted"]),
        hoverlabel=dict(bgcolor=COLORS["card"], bordercolor=COLORS["border"],
                        font=dict(family="Fira Sans", color=COLORS["text"])),
        legend=dict(font=dict(color=COLORS["muted"])),
    )
    pio.templates[_TEMPLATE] = tpl
    pio.templates.default = _TEMPLATE


def apply_styles(C: dict = COLORS) -> None:
    """Inyecta el CSS global del tablero (fuentes, fondos, inputs, tabs)."""
    st.markdown(
        f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@300;400;500;600;700&family=Fira+Code:wght@400;500;600&display=swap');
    * {{font-family:{_FONT}!important}}
    #MainMenu,footer,header {{visibility:hidden}}
    .block-container {{padding-top:1.2rem;padding-bottom:3rem;max-width:1280px}}
    .stApp {{background:{C['bg']}}}
    h1 {{color:{C['yellow']}!important;font-weight:700!important;letter-spacing:-.02em}}
    h2,h3,h4 {{color:{C['text']}!important}}
    p,span,label,li {{color:{C['text']}}}
    ::selection {{background:{C['c1']}44}}
    ::-webkit-scrollbar {{width:10px;height:10px}}
    ::-webkit-scrollbar-track {{background:{C['bg']}}}
    ::-webkit-scrollbar-thumb {{background:{C['card']};border-radius:6px}}
    ::-webkit-scrollbar-thumb:hover {{background:{C['border']}}}

    .stTextInput input,.stNumberInput input,.stDateInput input,textarea {{
        background:{C['card']}!important;color:{C['text']}!important;
        border:1px solid {C['border']}!important;border-radius:8px!important;
        transition:border-color 150ms ease!important}}
    .stTextInput input:focus,.stNumberInput input:focus {{
        border-color:{C['c1']}!important;
        box-shadow:0 0 0 1px {C['c1']}55!important}}
    div[data-baseweb="select"]>div,div[data-baseweb="input"]>div {{
        background:{C['card']}!important;border:1px solid {C['border']}!important;
        border-radius:8px!important;color:{C['text']}!important}}
    .stSlider [data-baseweb="slider"] div[role="slider"] {{background:{C['c3']}!important}}

    .stButton>button,.stDownloadButton>button {{
        background:{C['c3']}!important;color:#1A1304!important;border:none!important;
        border-radius:8px!important;font-weight:600!important;padding:.45rem 1.1rem!important;
        cursor:pointer!important;transition:filter 180ms ease,box-shadow 180ms ease!important}}
    .stButton>button:hover,.stDownloadButton>button:hover {{
        filter:brightness(1.1)!important;box-shadow:0 4px 16px {C['c3']}40!important}}
    .stButton>button:focus-visible,.stDownloadButton>button:focus-visible {{
        outline:2px solid {C['text']}!important;outline-offset:2px!important}}

    .stTabs [data-baseweb="tab-list"] {{gap:2px;border-bottom:1px solid {C['border']}}}
    .stTabs [data-baseweb="tab"] {{color:{C['muted']}!important;
        padding:8px 14px!important;transition:color 150ms ease!important}}
    .stTabs [data-baseweb="tab"]:hover {{color:{C['text']}!important}}
    .stTabs [aria-selected="true"] {{
        color:{C['text']}!important;border-bottom:2px solid {C['yellow']}!important}}

    div[data-testid="stHorizontalBlock"] {{gap:.8rem}}
    .stAlert {{background:{C['card']}!important;border:1px solid {C['border']}!important;
        border-radius:10px!important}}
    div[data-testid="stExpander"] {{background:{C['card']}!important;
        border:1px solid {C['border']}!important;border-radius:10px!important}}
    .stDataFrame {{border:1px solid {C['border']}!important;border-radius:10px!important}}
    hr {{border-color:{C['border']}!important}}

    .cdi-kpi {{transition:border-color 180ms ease,box-shadow 180ms ease}}
    .cdi-kpi:hover {{border-color:{C['muted']}66!important;
        box-shadow:0 6px 20px rgba(4,8,20,.5)}}

    @media (prefers-reduced-motion: reduce) {{
        * {{transition:none!important;animation:none!important}}
    }}
    </style>""",
        unsafe_allow_html=True,
    )


def md(html: str) -> None:
    """Renderiza HTML custom."""
    st.markdown(html, unsafe_allow_html=True)


def header_app(titulo: str, subtitulo: str = "") -> None:
    """Encabezado del tablero con franja tricolor (bandera de Colombia)."""
    sub = (f"<div style='color:{COLORS['muted']};font-size:13px;margin-top:4px'>"
           f"{subtitulo}</div>") if subtitulo else ""
    st.markdown(
        f"<div style='margin:2px 0 10px'>"
        f"<div style='display:flex;border-radius:3px;overflow:hidden;width:64px;"
        f"height:6px;margin-bottom:10px'>"
        f"<div style='flex:2;background:{COLORS['yellow']}'></div>"
        f"<div style='flex:1;background:#003087'></div>"
        f"<div style='flex:1;background:{COLORS['red']}'></div></div>"
        f"<div style='font-size:30px;font-weight:700;letter-spacing:-.02em;"
        f"color:{COLORS['yellow']}'>{titulo}</div>{sub}</div>",
        unsafe_allow_html=True,
    )


def kpi(label: str, valor: str, delta: str = "", color: str = COLORS["c1"],
        ayuda: str = "") -> str:
    """Tarjeta KPI en HTML (reemplaza st.metric, compatible con tema oscuro)."""
    d = (f"<div style='color:{color};font-size:12px;font-weight:600;margin-top:4px'>"
         f"{delta}</div>") if delta else ""
    title = f" title='{ayuda}'" if ayuda else ""
    return (
        f"<div{title} class='cdi-kpi' style=\"background:{COLORS['card']};"
        f"border:1px solid {COLORS['border']};border-left:3px solid {color};"
        f"border-radius:12px;padding:14px 18px;height:100%\">"
        f"<div style=\"color:{COLORS['muted']};font-size:11px;font-weight:600;"
        f"text-transform:uppercase;letter-spacing:.05em\">{label}</div>"
        f"<div style=\"color:{COLORS['text']};font-size:25px;font-weight:600;"
        f"font-family:{_FONT_NUM};font-variant-numeric:tabular-nums;"
        f"margin-top:5px\">{valor}</div>{d}</div>"
    )


def kpis_row(items: list[dict], gap: int = 12) -> str:
    """Fila de tarjetas KPI (ticker). Cada item: {label, valor, delta, color, ayuda}."""
    cards = "".join(
        f"<div style='flex:1;min-width:180px'>"
        f"{kpi(it['label'], it['valor'], it.get('delta',''), it.get('color',COLORS['c1']), it.get('ayuda',''))}"
        f"</div>"
        for it in items
    )
    return (f"<div style='display:flex;gap:{gap}px;flex-wrap:wrap;margin:8px 0 4px'>"
            f"{cards}</div>")


def badge(texto: str, color: str = COLORS["c2"]) -> str:
    return (f"<span style='background:{color}22;color:{color};border:1px solid "
            f"{color}55;border-radius:20px;padding:2px 10px;font-size:11px;"
            f"font-weight:600'>{texto}</span>")
