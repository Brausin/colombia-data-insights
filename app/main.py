"""
colombia-data-insights — Dashboard principal
============================================
Inteligencia económica colombiana con estética BI oscura ("Data-Dense
Dashboard", ui-ux-pro-max — ver app/ui.py y design-system/).
Datos procesados de fuentes oficiales: DANE, Banco de la República,
datos.gov.co.

Ejecutar:
    streamlit run app/main.py
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
import pandas as pd
import plotly.express as px

from colombia_data.trm_live import get_trm_hoy, get_historico_trm
from colombia_data.ipc import get_ipc
from colombia_data.desempleo import get_desempleo, comparar_ciudades, CIUDADES_DISPONIBLES
from colombia_data.exportaciones import get_exportaciones, top_productos
from colombia_data.utils import (
    formatear_pesos,
    calcular_poder_adquisitivo,
    smmlv_a_usd,
)

import ui
from ui import COLORS as C, kpi, kpis_row, badge, md, callout, empty_state

SMMLV_REF = 1_300_000  # SMMLV de referencia (COP/mes)

# ---------------------------------------------------------------------------
# Configuración de página + tema
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Colombia Data Insights",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="collapsed",
)
ui.apply_styles()
ui.registrar_tema()

PLOTLY_CFG = {"displayModeBar": False}


def _clamp(valor: float, minimo: float, maximo: float) -> float:
    """Acota un valor al rango [minimo, maximo] para defaults de widgets.

    Evita StreamlitAPIException cuando un dato en vivo (p. ej. la TRM)
    queda fuera del rango permitido del number_input.
    """
    return float(min(max(valor, minimo), maximo))


# ---------------------------------------------------------------------------
# Cargadores de datos (cacheados) — normalizan columnas del CSV crudo
# ---------------------------------------------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def cargar_trm_hoy() -> float:
    return get_trm_hoy()


@st.cache_data(ttl=1800, show_spinner=False)
def cargar_historico_trm(meses: int = 18) -> pd.DataFrame:
    df = pd.DataFrame(get_historico_trm(meses=meses))
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df.sort_values("fecha").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def cargar_ipc() -> pd.DataFrame:
    df = get_ipc().rename(columns={"año": "anio", "variacion_anual": "variacion_ipc"})
    df["fecha"] = pd.to_datetime(df["periodo"])
    return df.sort_values(["anio", "mes"]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def cargar_inflacion_anual() -> pd.DataFrame:
    """Inflación anual del Banco Mundial (data/processed/inflacion_anual.csv)."""
    ruta = _REPO_ROOT / "data" / "processed" / "inflacion_anual.csv"
    df = pd.read_csv(ruta)
    return df.sort_values("anio").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def cargar_desempleo() -> pd.DataFrame:
    return get_desempleo().rename(columns={"año": "anio"}).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def cargar_exportaciones() -> pd.DataFrame:
    return get_exportaciones()


# ---------------------------------------------------------------------------
# Header + KPI ticker (datos reales de los CSV procesados)
# ---------------------------------------------------------------------------
md(ui.header_app(
    "Colombia Data Insights",
    "Datos económicos colombianos de fuentes oficiales: DANE · Banco de la "
    "República · Superintendencia Financiera · datos.gov.co",
))

try:
    with st.spinner("Cargando indicadores..."):
        trm_hoy = cargar_trm_hoy()
        df_ipc = cargar_ipc()
        df_des = cargar_desempleo()
        df_trm_tick = cargar_historico_trm(meses=18)
except Exception as exc:  # CSV ausente, columnas inesperadas, sin red…
    empty_state(
        "No fue posible cargar los indicadores",
        "Verifica que los CSV de <code>data/processed/</code> existan "
        "(ejecuta el pipeline de datos) y que haya conexión para la TRM. "
        f"Detalle técnico: <code>{type(exc).__name__}: {exc}</code>",
        icn="alert-circle",
    )
    if st.button("Reintentar carga"):
        st.cache_data.clear()
        st.rerun()
    st.stop()

if df_ipc.empty or df_des.empty or df_trm_tick.empty:
    empty_state(
        "Los archivos de datos están vacíos",
        "Los CSV de <code>data/processed/</code> no contienen filas. "
        "Vuelve a generar los datos con el pipeline del repositorio.",
        icn="database",
    )
    st.stop()

ult_ipc = df_ipc.iloc[-1]
ult_des = df_des.iloc[-1]
smmlv_usd = SMMLV_REF / trm_hoy if trm_hoy else 0.0

# Delta de la TRM frente al valor de hace ~30 días (CSV histórico)
_fecha_ult_trm = df_trm_tick["fecha"].max()
_prev = df_trm_tick[df_trm_tick["fecha"] <= _fecha_ult_trm - pd.Timedelta(days=30)]
trm_30d = _prev.iloc[-1]["trm"] if len(_prev) else df_trm_tick.iloc[0]["trm"]
diff_trm = trm_hoy - trm_30d
if diff_trm >= 0:
    trm_delta, trm_delta_color = f"▲ +{diff_trm:,.0f} vs hace 30 días", C["red"]
else:
    trm_delta, trm_delta_color = f"▼ -{abs(diff_trm):,.0f} vs hace 30 días", C["c2"]

md(kpis_row([
    {"label": "TRM hoy", "valor": f"${trm_hoy:,.0f}", "delta": trm_delta,
     "color": trm_delta_color, "ayuda": "Variación de la TRM frente a hace 30 días"},
    {"label": f"Inflación anual ({ult_ipc['periodo']})",
     "valor": f"{ult_ipc['variacion_ipc']:.2f}%", "delta": "variación 12 meses",
     "color": C["c3"], "ayuda": "IPC: variación anual del último mes disponible"},
    {"label": f"Desempleo ({ult_des['periodo']})",
     "valor": f"{ult_des['tasa_desempleo']:.1f}%", "delta": "tasa nacional",
     "color": C["c1"], "ayuda": "Tasa de desempleo nacional del último trimestre"},
    {"label": "SMMLV en USD", "valor": f"${smmlv_usd:,.0f}",
     "delta": f"{formatear_pesos(SMMLV_REF)} / mes", "color": C["c2"],
     "ayuda": "Salario mínimo mensual convertido a dólares a la TRM de hoy"},
]))

# ---------------------------------------------------------------------------
# Tabs (Material Symbols — vector, nunca emoji)
# ---------------------------------------------------------------------------
tab_trm, tab_ipc, tab_desempleo, tab_exportaciones, tab_calculadoras = st.tabs([
    ":material/payments: TRM hoy",
    ":material/monitoring: Inflación",
    ":material/work: Desempleo",
    ":material/public: Exportaciones",
    ":material/calculate: Calculadoras",
])

# ============================================================
# TAB 1 — TRM
# ============================================================
with tab_trm:
    st.subheader("Tasa Representativa del Mercado (TRM)")
    st.markdown(
        "La TRM es el precio oficial del dólar en Colombia, publicado diariamente "
        "por la Superintendencia Financiera. Afecta el precio de importaciones, "
        "exportaciones, deudas en dólares y el valor real de tus ingresos en "
        "moneda extranjera."
    )

    df_trm = cargar_historico_trm(meses=18)
    trm_anterior = df_trm.iloc[-2]["trm"] if len(df_trm) >= 2 else trm_hoy
    variacion_trm = trm_hoy - trm_anterior

    md(kpis_row([
        {"label": "TRM vigente", "valor": f"${trm_hoy:,.0f}",
         "delta": f"{variacion_trm:+,.0f} vs mes anterior",
         "color": C["yellow"] if variacion_trm >= 0 else C["c2"]},
        {"label": "Máximo (período)", "valor": f"${df_trm['trm'].max():,.0f}",
         "color": C["red"]},
        {"label": "Mínimo (período)", "valor": f"${df_trm['trm'].min():,.0f}",
         "color": C["c2"]},
        {"label": "Promedio (período)", "valor": f"${df_trm['trm'].mean():,.0f}",
         "color": C["c1"]},
    ]))

    fig_trm = px.area(
        df_trm, x="fecha", y="trm",
        title="TRM mensual (COP/USD)",
        labels={"fecha": "Mes", "trm": "TRM (COP/USD)"},
        color_discrete_sequence=[C["yellow"]],
    )
    fig_trm.update_layout(yaxis=dict(tickformat=",.0f", tickprefix="$"),
                          hovermode="x unified")
    fig_trm.update_traces(
        hovertemplate="<b>%{x|%b %Y}</b><br>TRM: $%{y:,.2f}<extra></extra>")

    # Marca "Hoy": línea vertical punteada + punto en el valor más reciente
    fecha_ult_trm = df_trm["fecha"].max()
    trm_ult = df_trm.iloc[-1]["trm"]
    fig_trm.add_scatter(
        x=[fecha_ult_trm, fecha_ult_trm],
        y=[df_trm["trm"].min(), df_trm["trm"].max()],
        mode="lines", line=dict(color=C["muted"], dash="dot", width=1),
        showlegend=False, hoverinfo="skip")
    fig_trm.add_scatter(
        x=[fecha_ult_trm], y=[trm_ult], mode="markers+text",
        marker=dict(color=C["yellow"], size=11, line=dict(color=C["bg"], width=1)),
        text=["Hoy"], textposition="top center", showlegend=False,
        hovertemplate="Hoy: $%{y:,.0f}<extra></extra>")
    st.plotly_chart(fig_trm, width="stretch", config=PLOTLY_CFG)
    md(ui.fuente_dato("Superintendencia Financiera vía datos.gov.co · serie mensual"))

    # Conversor integrado USD → COP (en vivo, sin botón)
    st.markdown("#### Conversor USD → COP")
    usd_conv = st.number_input("Dólares a convertir (USD)", min_value=0.0,
                               max_value=1_000_000_000.0,
                               value=1_000.0, step=100.0, key="trm_conv")
    md(kpi("Equivalen en pesos", formatear_pesos(usd_conv * trm_hoy),
           f"a la TRM de hoy (${trm_hoy:,.0f})", C["c2"]))

    callout(
        "info",
        f"<b>¿Qué significa hoy?</b> Con TRM de ${trm_hoy:,.0f}, USD 1.000 "
        f"equivalen a <b>{formatear_pesos(trm_hoy * 1000)}</b>. Si recibes ingresos "
        f"en dólares, el nivel de la TRM afecta directamente tu poder de compra "
        f"en Colombia.",
    )

# ============================================================
# TAB 2 — INFLACIÓN / IPC
# ============================================================
with tab_ipc:
    st.subheader("Inflación en Colombia (IPC)")
    st.markdown(
        "El Índice de Precios al Consumidor (IPC) mide cuánto suben los precios. "
        "Si la inflación anual es 10%, algo que costaba $100.000 ahora cuesta "
        "$110.000. El DANE lo publica mensualmente."
    )

    anios_ipc = sorted(df_ipc["anio"].unique(), reverse=True)
    anio_sel = st.selectbox("Año de referencia", anios_ipc, index=0, key="ipc_anio")

    ipc_anio = df_ipc[df_ipc["anio"] == anio_sel].sort_values("mes")
    ipc_anio_valido = ipc_anio.dropna(subset=["variacion_ipc"])

    if ipc_anio_valido.empty:
        empty_state(
            f"Sin datos de IPC para {anio_sel}",
            "El CSV procesado no tiene filas con variación anual para este año. "
            "Elige otro año en el selector.",
        )
    else:
        inflacion_anual = ipc_anio_valido["variacion_ipc"].iloc[-1]   # YoY al cierre
        mes_alto = ipc_anio_valido.loc[ipc_anio_valido["variacion_ipc"].idxmax()]
        indice_dic = ipc_anio_valido["ipc"].iloc[-1]

        md(kpis_row([
            {"label": f"Inflación anual {anio_sel}", "valor": f"{inflacion_anual:.2f}%",
             "delta": "variación 12 meses al cierre", "color": C["c3"],
             "ayuda": "Variación anual del IPC al último mes disponible del año"},
            {"label": "Mes más alto", "valor": f"{mes_alto['variacion_ipc']:.2f}%",
             "delta": f"mes {int(mes_alto['mes'])}", "color": C["red"]},
            {"label": "Índice IPC (cierre)", "valor": f"{indice_dic:,.1f}",
             "delta": "base dic-2018 = 100", "color": C["c1"]},
        ]))

        fig_ipc = px.line(
            df_ipc, x="fecha", y="variacion_ipc",
            title="Inflación mensual histórica (variación anual %)",
            labels={"fecha": "Mes", "variacion_ipc": "Variación anual (%)"},
            color_discrete_sequence=[C["red_chart"]],
        )
        fig_ipc.add_hline(y=3.0, line_dash="dash", line_color=C["c2"],
                          annotation_text="Meta BR 3%",
                          annotation_position="bottom right")
        fig_ipc.update_layout(yaxis=dict(ticksuffix="%"), hovermode="x unified")
        st.plotly_chart(fig_ipc, width="stretch", config=PLOTLY_CFG)
        md(ui.fuente_dato("DANE · IPC mensual, variación anual"))

        _sobre_meta = inflacion_anual > 3
        callout(
            "alerta" if _sobre_meta else "exito",
            f"La inflación de <b>{anio_sel}</b> fue <b>{inflacion_anual:.1f}%</b> — "
            f"{'por encima' if _sobre_meta else 'por debajo'} de la meta del 3% "
            f"del Banco de la República.",
        )

        callout(
            "dato",
            "<b>Contexto:</b> La meta de inflación del Banco de la República es "
            "3% anual. En 2022 Colombia alcanzó 13.1%, la más alta en más de 20 "
            "años, impulsada por la pandemia, la guerra en Ucrania y el alza "
            "global de alimentos.",
        )

    # ---- Comparación anual de largo plazo (Banco Mundial) -------------------
    st.markdown("#### Inflación anual de largo plazo")
    st.caption(
        "Variación anual del IPC según el Banco Mundial "
        "(indicador FP.CPI.TOTL.ZG), un único dato por año para ver la "
        "tendencia de la última década. Se actualiza con un cron mensual."
    )
    try:
        df_inf_anual = cargar_inflacion_anual()
    except FileNotFoundError:
        df_inf_anual = pd.DataFrame()
    except Exception:
        df_inf_anual = pd.DataFrame()

    if df_inf_anual.empty:
        empty_state(
            "No se encontró la serie anual del Banco Mundial",
            "Falta <code>data/processed/inflacion_anual.csv</code>. Genera el "
            "archivo con el cron/pipeline del repo para ver esta gráfica.",
            icn="database",
        )
    else:
        fig_anual = px.bar(
            df_inf_anual, x="anio", y="inflacion_pct",
            title="Inflación anual de Colombia (Banco Mundial)",
            labels={"anio": "Año", "inflacion_pct": "Inflación (%)"},
            color_discrete_sequence=[C["c3"]],
        )
        fig_anual.add_hline(y=3.0, line_dash="dash", line_color=C["c2"],
                            annotation_text="Meta BR 3%",
                            annotation_position="top left")
        fig_anual.update_layout(yaxis=dict(ticksuffix="%"), hovermode="x unified",
                                xaxis=dict(dtick=1))
        st.plotly_chart(fig_anual, width="stretch", config=PLOTLY_CFG)
        md(ui.fuente_dato("Banco Mundial · FP.CPI.TOTL.ZG"))

# ============================================================
# TAB 3 — DESEMPLEO
# ============================================================
with tab_desempleo:
    st.subheader("Mercado Laboral Colombiano")
    st.markdown(
        "La tasa de desempleo mide el porcentaje de personas que buscan trabajo "
        "activamente y no lo encuentran. El DANE la publica con datos nacionales "
        "y por ciudad principal (GEIH)."
    )

    ultimo = df_des.iloc[-1]
    anterior = df_des.iloc[-2] if len(df_des) > 1 else ultimo
    delta_des = ultimo["tasa_desempleo"] - anterior["tasa_desempleo"]

    md(kpis_row([
        {"label": "Tasa actual", "valor": f"{ultimo['tasa_desempleo']:.1f}%",
         "delta": f"{delta_des:+.1f} pp vs trimestre anterior",
         "color": C["c2"] if delta_des <= 0 else C["red"],
         "ayuda": "Población económicamente activa que está desempleada"},
        {"label": "Pico histórico", "valor": f"{df_des['tasa_desempleo'].max():.1f}%",
         "delta": "T2-2020 (pandemia)", "color": C["red"]},
        {"label": "Mínimo histórico", "valor": f"{df_des['tasa_desempleo'].min():.1f}%",
         "color": C["c2"]},
    ]))

    fig_des = px.bar(
        df_des, x="periodo", y="tasa_desempleo",
        title="Tasa de desempleo trimestral nacional (%)",
        labels={"periodo": "Trimestre", "tasa_desempleo": "Tasa (%)"},
        color="tasa_desempleo", color_continuous_scale="RdYlGn_r",
    )
    fig_des.update_layout(coloraxis_showscale=False, yaxis=dict(ticksuffix="%"),
                          xaxis=dict(tickangle=-45))
    fig_des.update_traces(
        hovertemplate="<b>%{x}</b><br>Desempleo: %{y:.1f}%<extra></extra>")

    # Anotación COVID-19 en el pico histórico si cae en 2020
    idx_pico = df_des["tasa_desempleo"].idxmax()
    periodo_pico = str(df_des.loc[idx_pico, "periodo"])
    if "2020" in periodo_pico:
        fig_des.add_annotation(
            x=periodo_pico, y=df_des.loc[idx_pico, "tasa_desempleo"],
            text="COVID-19 ▲", showarrow=True, arrowhead=2, ay=-40,
            font=dict(color=C["red"], size=12), arrowcolor=C["red"])
    st.plotly_chart(fig_des, width="stretch", config=PLOTLY_CFG)
    md(ui.fuente_dato("DANE · GEIH, tasa de desempleo trimestral"))

    st.divider()
    st.markdown("### Comparar ciudades")
    st.markdown(
        "Compara el desempleo entre ciudades para un año específico. Los datos "
        "provienen de la Gran Encuesta Integrada de Hogares (GEIH) del DANE."
    )

    col_cit, col_yr = st.columns([3, 1])
    with col_cit:
        ciudades_sel = st.multiselect(
            "Selecciona ciudades", options=CIUDADES_DISPONIBLES,
            default=["bogota", "medellin", "cali", "barranquilla", "bucaramanga"],
            help="Selecciona entre 2 y 10 ciudades para comparar",
        )
    with col_yr:
        anio_comp = st.selectbox("Año", options=list(range(2015, 2025)), index=8,
                                 help="Promedio anual de los 4 trimestres")

    if not ciudades_sel:
        empty_state("Sin ciudades seleccionadas",
                    "Elige al menos 2 ciudades en el selector para ver la "
                    "comparación.")
    elif len(ciudades_sel) < 2:
        callout("info", "Selecciona al menos <b>2 ciudades</b> para ver la "
                        "comparación.")
    else:
        try:
            df_comp = comparar_ciudades(ciudades_sel, anio_comp)
            if df_comp.empty:
                empty_state(
                    f"Sin datos GEIH para {anio_comp}",
                    "No hay registros para esa combinación de ciudades y año. "
                    "Prueba con un año entre 2015 y 2023.",
                )
            else:
                fig_comp = px.bar(
                    df_comp, x="ciudad", y="tasa_desempleo_pct",
                    title=f"Desempleo por ciudad — {anio_comp} (promedio anual, %)",
                    labels={"ciudad": "Ciudad", "tasa_desempleo_pct": "Tasa (%)"},
                    color="tasa_desempleo_pct", color_continuous_scale="RdYlGn_r",
                    text="tasa_desempleo_pct",
                )
                fig_comp.update_traces(
                    texttemplate="%{text:.1f}%", textposition="outside",
                    cliponaxis=False,
                    hovertemplate="<b>%{x}</b><br>Desempleo: %{y:.1f}%<extra></extra>")
                fig_comp.update_layout(coloraxis_showscale=False,
                                       yaxis=dict(ticksuffix="%"), showlegend=False)
                st.plotly_chart(fig_comp, width="stretch", config=PLOTLY_CFG)
                md(ui.fuente_dato("DANE · GEIH por ciudad, promedio anual"))
        except KeyError as e:
            callout("error",
                    f"No hay datos para el año o ciudad seleccionados ({e}). "
                    f"Prueba con un año entre 2015 y 2023.")
        except Exception as e:
            callout("error",
                    "No fue posible generar la comparación de ciudades. "
                    f"Detalle: <code>{type(e).__name__}: {e}</code>")

    callout(
        "dato",
        "<b>Contexto:</b> Colombia tiene una de las tasas de desempleo más "
        "altas de América Latina. El desempleo juvenil (18-28 años) casi "
        "duplica la tasa nacional.",
    )

# ============================================================
# TAB 4 — EXPORTACIONES
# ============================================================
with tab_exportaciones:
    st.subheader("Exportaciones Colombianas")
    st.markdown(
        "Colombia exporta principalmente petróleo, carbón y café. La alta "
        "dependencia del petróleo hace la economía vulnerable a los precios "
        "internacionales del crudo."
    )

    df_exp = cargar_exportaciones()
    if df_exp.empty:
        empty_state("Sin datos de exportaciones",
                    "El CSV procesado de exportaciones está vacío o no se generó.",
                    icn="database")
    else:
        anios_exp = sorted(df_exp["anio"].unique(), reverse=True)
        anio_exp = st.selectbox("Año", anios_exp, index=0, key="exp_anio")

        top = top_productos(anio=anio_exp, n=8)

        if top.empty:
            empty_state(f"Sin exportaciones registradas en {anio_exp}",
                        "Elige otro año del selector.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                fig_pie = px.pie(
                    top, values="valor_millones_usd", names="producto",
                    title=f"Composición de exportaciones {anio_exp}", hole=0.45,
                )
                fig_pie.update_traces(
                    textposition="inside", textinfo="percent+label",
                    hovertemplate="<b>%{label}</b><br>USD %{value:.0f}M "
                                  "(%{percent})<extra></extra>")
                st.plotly_chart(fig_pie, width="stretch", config=PLOTLY_CFG)

            with col2:
                fig_bar = px.bar(
                    top.sort_values("valor_millones_usd"),
                    x="valor_millones_usd", y="producto", orientation="h",
                    title=f"Top exportaciones {anio_exp} (USD millones)",
                    labels={"valor_millones_usd": "USD millones", "producto": ""},
                    color="valor_millones_usd", color_continuous_scale="YlGnBu",
                )
                fig_bar.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig_bar, width="stretch", config=PLOTLY_CFG)

            md(ui.fuente_dato("DANE · exportaciones FOB por producto"))

        petroleo_df = df_exp[df_exp["producto"] == "Petroleo y derivados"]
        if len(petroleo_df) > 1:
            fig_pet = px.area(
                petroleo_df.sort_values("anio"), x="anio", y="valor_millones_usd",
                title="Exportaciones de petróleo y derivados por año",
                labels={"anio": "Año", "valor_millones_usd": "USD millones"},
                color_discrete_sequence=[C["c1"]],
            )
            st.plotly_chart(fig_pet, width="stretch", config=PLOTLY_CFG)

        callout(
            "alerta",
            "<b>Dependencia petrolera:</b> el petróleo representa entre el "
            "40-55% de las exportaciones. Cuando el precio del crudo cae, "
            "Colombia recibe menos dólares → el peso se devalúa → las "
            "importaciones suben.",
        )

# ============================================================
# TAB 5 — CALCULADORAS
# ============================================================
with tab_calculadoras:
    st.subheader("Calculadoras económicas")
    st.markdown("Herramientas para entender el impacto de la economía en tu bolsillo.")

    calc1, calc2, calc3 = st.tabs([
        ":material/savings: Poder adquisitivo",
        ":material/attach_money: Tu salario en USD",
        ":material/history: Devaluación histórica",
    ])

    # ---- Calculadora 1: Poder adquisitivo ----
    with calc1:
        st.markdown(
            "**¿Cuánto vale hoy lo que valía antes?**  \n"
            "La inflación erosiona el poder de compra: $1.000.000 de hace unos "
            "años no compra lo mismo hoy."
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            monto = st.number_input("Monto a calcular (COP)", 10_000, 1_000_000_000,
                                    1_000_000, 100_000)
        with col2:
            inflacion_prom = st.slider("Inflación anual promedio (%)", 1.0, 20.0,
                                       6.5, 0.5,
                                       help="IPC 2022 = 13.1%, IPC 2023 = 9.3%")
        with col3:
            anios_calc = st.slider("Años", 1, 20, 5)

        infl_acumulada = ((1 + inflacion_prom / 100) ** anios_calc - 1) * 100
        r = calcular_poder_adquisitivo(monto, infl_acumulada)

        st.divider()
        md(kpis_row([
            {"label": "Valor nominal hoy", "valor": formatear_pesos(monto),
             "color": C["c1"]},
            {"label": f"Poder de compra real en {anios_calc} años",
             "valor": formatear_pesos(r["salario_real"]),
             "delta": f"inflación acumulada {infl_acumulada:.1f}%", "color": C["c3"]},
            {"label": "Necesitas para mantenerlo",
             "valor": formatear_pesos(r["se_necesita_para_mantener"]),
             "delta": f"-{r['perdida_poder_adquisitivo_pct']:.1f}% de poder",
             "color": C["red"]},
        ]))

        callout(
            "info",
            f"Con inflación de {inflacion_prom}% anual durante {anios_calc} años "
            f"(acumulada {infl_acumulada:.1f}%), {formatear_pesos(monto)} de hoy "
            f"tendrán el poder de compra de "
            f"<b>{formatear_pesos(r['salario_real'])}</b>. Necesitarías "
            f"<b>{formatear_pesos(r['se_necesita_para_mantener'])}</b> "
            f"para mantener el mismo nivel de vida.",
        )

    # ---- Calculadora 2: Salario en USD ----
    with calc2:
        st.markdown(
            "**¿Cuánto ganas en dólares?**  \n"
            "Convierte tu salario en pesos a dólares según la TRM, y compáralo "
            "con el salario mínimo."
        )
        col1, col2 = st.columns(2)
        with col1:
            salario_cop = st.number_input("Tu salario mensual (COP)", 0, 100_000_000,
                                          3_000_000, 100_000)
        with col2:
            trm_calc = st.number_input("TRM a usar (COP/USD)", 1_000.0, 30_000.0,
                                       _clamp(trm_hoy, 1_000.0, 30_000.0), 10.0)

        res_usd = smmlv_a_usd(salario_cop, trm_calc)
        smmlv_usd_calc = SMMLV_REF / trm_calc
        ratio = salario_cop / SMMLV_REF if SMMLV_REF else 0

        md(kpis_row([
            {"label": "Tu salario en USD", "valor": f"${res_usd['smmlv_usd']:,.2f}",
             "color": C["c2"]},
            {"label": "SMMLV en USD", "valor": f"${smmlv_usd_calc:,.2f}",
             "delta": "salario mínimo en dólares", "color": C["yellow"]},
            {"label": "Salarios mínimos", "valor": f"{ratio:.1f}x",
             "delta": "cuántos SMMLV representa", "color": C["c1"]},
        ]))

    # ---- Calculadora 3: Devaluación ----
    with calc3:
        st.markdown(
            "**¿Cuánto se ha devaluado el peso?**  \n"
            "Mira cómo cambió el valor del dólar entre dos momentos."
        )
        col1, col2 = st.columns(2)
        with col1:
            trm_inicio_val = st.number_input("TRM de referencia (pasado)", 500.0,
                                             30_000.0, 3_200.0, 50.0)
        with col2:
            trm_fin_val = st.number_input("TRM actual", 500.0, 30_000.0,
                                          _clamp(trm_hoy, 500.0, 30_000.0), 50.0)

        if trm_inicio_val > 0:
            devaluacion = (trm_fin_val / trm_inicio_val - 1) * 100
            md(kpis_row([
                {"label": "Devaluación del peso", "valor": f"{devaluacion:+.1f}%",
                 "delta": "positivo = el dólar subió",
                 "color": C["red"] if devaluacion > 0 else C["c2"]},
                {"label": "Impacto en importaciones", "valor": f"{devaluacion:+.1f}%",
                 "delta": "las importaciones suben igual", "color": C["c3"]},
            ]))

            if devaluacion > 0:
                callout(
                    "alerta",
                    f"El peso perdió <b>{devaluacion:.1f}%</b> de su valor frente "
                    f"al dólar. Lo que costaba USD 100 (${trm_inicio_val:,.0f}), "
                    f"ahora cuesta ${trm_fin_val:,.0f}.",
                )
            else:
                callout(
                    "exito",
                    f"El peso se fortaleció <b>{abs(devaluacion):.1f}%</b> frente "
                    "al dólar. Las importaciones se abaratan y los ingresos en "
                    "dólares valen menos en pesos.",
                )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
md(f"<div style='display:flex;gap:8px;align-items:flex-start;"
   f"color:{C['muted']};font-size:12px;line-height:1.6'>"
   f"{ui.icono('database', 14, C['muted'])}"
   f"<span>Fuentes oficiales: DANE · Banco de la República · Superintendencia "
   f"Financiera · datos.gov.co<br>Los valores de respaldo corresponden a "
   f"series históricas documentadas.</span></div>")
