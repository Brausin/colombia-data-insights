"""
ui.py — Sistema de diseño BI para el dashboard colombia-data-insights.

Centraliza la paleta, el CSS global, los componentes HTML (tarjetas KPI, ticker,
badges) y registra un template oscuro de Plotly que se aplica a todos los
gráficos del tablero. Evita los widgets por defecto que rompen el tema oscuro
(st.metric) usando tarjetas HTML propias.
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

# ── Paleta BI (bandera + acentos de dato) ────────────────────────────────────
COLORS = {
    "bg": "#0A0E1A",
    "card": "#111827",
    "border": "#1F2937",
    "yellow": "#FFD100",
    "blue": "#003087",
    "red": "#CE1126",
    "c1": "#4F9CF9",
    "c2": "#48D0A4",
    "c3": "#F97316",
    "text": "#F1F5F9",
    "muted": "#94A3B8",
}

_GRID = "#1B2433"
_TEMPLATE = "cdi_dark"


def registrar_tema() -> None:
    """Registra y activa un template oscuro de Plotly para todo el tablero.

    Tras llamarla, cualquier figura de plotly.express / graph_objects hereda
    fondo transparente, texto claro, grid sutil y la paleta de marca.
    """
    tpl = go.layout.Template()
    tpl.layout = go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=COLORS["muted"], size=13),
        title=dict(font=dict(color=COLORS["text"], size=16)),
        colorway=[COLORS["c1"], COLORS["c2"], COLORS["c3"],
                  COLORS["yellow"], COLORS["red"], COLORS["blue"]],
        xaxis=dict(gridcolor=_GRID, zerolinecolor=_GRID, linecolor=COLORS["border"],
                   color=COLORS["muted"]),
        yaxis=dict(gridcolor=_GRID, zerolinecolor=_GRID, linecolor=COLORS["border"],
                   color=COLORS["muted"]),
        hoverlabel=dict(bgcolor=COLORS["card"], bordercolor=COLORS["border"],
                        font=dict(family="Inter", color=COLORS["text"])),
        legend=dict(font=dict(color=COLORS["muted"])),
    )
    pio.templates[_TEMPLATE] = tpl
    pio.templates.default = _TEMPLATE


def apply_styles(C: dict = COLORS) -> None:
    """Inyecta el CSS global del tablero (fuentes, fondos, inputs, tabs)."""
    st.markdown(
        f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * {{font-family:'Inter',sans-serif!important}}
    #MainMenu,footer,header {{visibility:hidden}}
    .block-container {{padding-top:1.4rem;padding-bottom:3rem;max-width:1240px}}
    .stApp {{background:{C['bg']}}}
    h1 {{color:{C['yellow']}!important;font-weight:700!important;letter-spacing:-.02em}}
    h2,h3,h4 {{color:{C['text']}!important}}
    p,span,label,li {{color:{C['text']}}}
    .stTextInput input,.stNumberInput input,.stDateInput input,textarea {{
        background:{C['card']}!important;color:{C['text']}!important;
        border:1px solid {C['border']}!important;border-radius:8px!important}}
    div[data-baseweb="select"]>div,div[data-baseweb="input"]>div {{
        background:{C['card']}!important;border:1px solid {C['border']}!important;
        border-radius:8px!important;color:{C['text']}!important}}
    .stSlider [data-baseweb="slider"] div[role="slider"] {{background:{C['yellow']}!important}}
    .stTabs [data-baseweb="tab-list"] {{gap:4px;border-bottom:1px solid {C['border']}}}
    .stTabs [data-baseweb="tab"] {{color:{C['muted']}!important}}
    .stTabs [aria-selected="true"] {{
        color:{C['text']}!important;border-bottom:2px solid {C['yellow']}!important}}
    div[data-testid="stHorizontalBlock"] {{gap:.8rem}}
    .stAlert {{background:{C['card']}!important;border:1px solid {C['border']}!important;
        border-radius:10px!important}}
    div[data-testid="stExpander"] {{background:{C['card']}!important;
        border:1px solid {C['border']}!important;border-radius:10px!important}}
    hr {{border-color:{C['border']}!important}}
    </style>""",
        unsafe_allow_html=True,
    )


def md(html: str) -> None:
    """Renderiza HTML custom."""
    st.markdown(html, unsafe_allow_html=True)


def kpi(label: str, valor: str, delta: str = "", color: str = COLORS["c1"],
        ayuda: str = "") -> str:
    """Tarjeta KPI en HTML (reemplaza st.metric, compatible con tema oscuro)."""
    d = (f"<div style='color:{color};font-size:12px;font-weight:600;margin-top:4px'>"
         f"{delta}</div>") if delta else ""
    title = f" title='{ayuda}'" if ayuda else ""
    return (
        f"<div{title} style=\"background:{COLORS['card']};border:1px solid "
        f"{COLORS['border']};border-left:3px solid {color};border-radius:12px;"
        f"padding:14px 18px;height:100%\">"
        f"<div style=\"color:{COLORS['muted']};font-size:11px;font-weight:600;"
        f"text-transform:uppercase;letter-spacing:.05em\">{label}</div>"
        f"<div style=\"color:{COLORS['text']};font-size:26px;font-weight:700;"
        f"font-variant-numeric:tabular-nums;margin-top:5px\">{valor}</div>{d}</div>"
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
