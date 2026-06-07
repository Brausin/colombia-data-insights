"""
colombia-data-insights — Dashboard principal
============================================
Inteligencia económica colombiana en tiempo real.
Datos procesados de fuentes oficiales: DANE, Banco de la República, datos.gov.co.
"""

import sys
import os
from pathlib import Path

# Asegurar que el módulo colombia_data sea importable
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from colombia_data.trm_live import get_trm_hoy, get_historico_trm
from colombia_data.ipc import get_ipc, variacion_ipc, ajustar_por_inflacion
from colombia_data.desempleo import get_desempleo, comparar_ciudades, CIUDADES_DISPONIBLES
from colombia_data.exportaciones import get_exportaciones, top_productos
from colombia_data.utils import (
    formatear_pesos,
    calcular_poder_adquisitivo,
    smmlv_a_usd,
)

# ---------------------------------------------------------------------------
# Configuración de página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Colombia Data Insights",
    page_icon="🇨🇴",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# CSS personalizado
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255,200,0,0.3);
    }
    .stMetric label { font-size: 0.85rem !important; color: #aaa !important; }
    .stMetric [data-testid="stMetricValue"] { font-size: 1.8rem !important; }
    div[data-testid="stHorizontalBlock"] { gap: 1rem; }
    h1 { color: #FFD700; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🇨🇴 Colombia Data Insights")
st.caption("Datos económicos colombianos de fuentes oficiales: DANE · Banco de la República · datos.gov.co")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_trm, tab_ipc, tab_desempleo, tab_exportaciones, tab_calculadoras = st.tabs([
    "📈 TRM hoy",
    "📊 Inflación",
    "💼 Desempleo",
    "🌍 Exportaciones",
    "🧮 Calculadoras",
])

# ============================================================
# TAB 1 — TRM
# ============================================================
with tab_trm:
    st.subheader("Tasa Representativa del Mercado (TRM)")
    st.markdown(
        "La TRM es el precio oficial del dólar en Colombia, "
        "publicado diariamente por la Superintendencia Financiera. "
        "Afecta el precio de importaciones, exportaciones, deudas en dólares "
        "y el valor real de tus ingresos en moneda extranjera."
    )

    with st.spinner("Consultando TRM..."):
        trm_hoy = get_trm_hoy()
        historico_trm = get_historico_trm(meses=18)

    df_trm = pd.DataFrame(historico_trm)
    df_trm["fecha"] = pd.to_datetime(df_trm["fecha"])
    df_trm = df_trm.sort_values("fecha")

    # Métricas clave
    trm_anterior = df_trm.iloc[-2]["trm"] if len(df_trm) >= 2 else trm_hoy
    variacion_trm = trm_hoy - trm_anterior

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "TRM Vigente",
            f"${trm_hoy:,.2f}",
            f"{variacion_trm:+,.2f} vs mes anterior",
            help="Pesos colombianos por 1 dólar estadounidense",
        )
    with col2:
        trm_max = df_trm["trm"].max()
        st.metric("Máximo (período)", f"${trm_max:,.2f}", help="Valor más alto en el período mostrado")
    with col3:
        trm_min = df_trm["trm"].min()
        st.metric("Mínimo (período)", f"${trm_min:,.2f}", help="Valor más bajo en el período mostrado")
    with col4:
        trm_prom = df_trm["trm"].mean()
        st.metric("Promedio (período)", f"${trm_prom:,.2f}", help="TRM promedio en el período mostrado")

    # Gráfica
    fig_trm = px.area(
        df_trm,
        x="fecha",
        y="trm",
        title="TRM mensual (COP/USD)",
        labels={"fecha": "Mes", "trm": "TRM (COP/USD)"},
        color_discrete_sequence=["#FFD700"],
    )
    fig_trm.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(tickformat=",.0f", tickprefix="$"),
        hovermode="x unified",
    )
    fig_trm.update_traces(
        hovertemplate="<b>%{x|%b %Y}</b><br>TRM: $%{y:,.2f}<extra></extra>"
    )
    st.plotly_chart(fig_trm, use_container_width=True)

    # Interpretación
    st.info(
        f"💡 **¿Qué significa hoy?** Con TRM de ${trm_hoy:,.0f}, "
        f"USD 1.000 equivalen a **{formatear_pesos(trm_hoy * 1000)}**. "
        f"Si recibes ingresos en dólares, el nivel de la TRM afecta "
        f"directamente cuánto poder de compra tienes en Colombia."
    )

# ============================================================
# TAB 2 — INFLACIÓN / IPC
# ============================================================
with tab_ipc:
    st.subheader("Inflación en Colombia (IPC)")
    st.markdown(
        "El Índice de Precios al Consumidor (IPC) mide cuánto suben los precios "
        "en un año. Si el IPC es 10%, algo que costaba $100.000 ahora cuesta $110.000. "
        "El DANE lo publica mensualmente con datos de 24 ciudades."
    )

    df_ipc = get_ipc()
    anios_ipc = sorted(df_ipc["anio"].unique(), reverse=True)
    anio_sel = st.selectbox("Año de referencia", anios_ipc, index=0, key="ipc_anio")

    ipc_anio = df_ipc[df_ipc["anio"] == anio_sel]
    variacion = variacion_ipc(df_ipc, anio_sel)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            f"Inflación {anio_sel}",
            f"{variacion:.2f}%",
            help="Variación anual promedio del IPC para el año seleccionado",
        )
    with col2:
        max_mes = ipc_anio.loc[ipc_anio["variacion_ipc"].idxmax()]
        st.metric(
            "Mes más alto",
            f"{max_mes['variacion_ipc']:.2f}%",
            f"mes {int(max_mes['mes'])}",
        )
    with col3:
        smmlv_2024 = 1_300_000
        smmlv_ajustado = ajustar_por_inflacion(smmlv_2024, variacion / 100)
        st.metric(
            "SMMLV ajustado por inflación",
            formatear_pesos(smmlv_ajustado),
            help=f"Valor del SMMLV base ${smmlv_2024:,} ajustado por inflación {anio_sel}",
        )

    # Gráfica histórica IPC
    fig_ipc = px.line(
        df_ipc,
        x="fecha",
        y="variacion_ipc",
        title="Inflación mensual histórica (variación anual %)",
        labels={"fecha": "Mes", "variacion_ipc": "Variación anual (%)"},
        color_discrete_sequence=["#E74C3C"],
    )
    fig_ipc.add_hline(
        y=3.0, line_dash="dash", line_color="green",
        annotation_text="Meta Banrep 3%", annotation_position="bottom right"
    )
    fig_ipc.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(ticksuffix="%"),
        hovermode="x unified",
    )
    st.plotly_chart(fig_ipc, use_container_width=True)

    st.info(
        "💡 **Contexto:** La meta de inflación del Banco de la República es 3% anual. "
        "En 2022 Colombia alcanzó inflación de 13.1%, la más alta en 20 años, "
        "impulsada por la pandemia, la guerra en Ucrania y el alza global de alimentos."
    )

# ============================================================
# TAB 3 — DESEMPLEO
# ============================================================
with tab_desempleo:
    st.subheader("Mercado Laboral Colombiano")
    st.markdown(
        "La tasa de desempleo mide el porcentaje de personas que buscan trabajo "
        "activamente y no lo encuentran. El DANE la publica trimestralmente con "
        "datos nacionales y por ciudad principal."
    )

    df_des = get_desempleo()

    # Métricas
    ultimo = df_des.iloc[-1]
    anterior = df_des.iloc[-2] if len(df_des) > 1 else ultimo
    delta_des = ultimo["tasa_desempleo"] - anterior["tasa_desempleo"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Tasa actual",
            f"{ultimo['tasa_desempleo']:.1f}%",
            f"{delta_des:+.1f}pp vs trimestre anterior",
            help="Porcentaje de la población económicamente activa que está desempleada",
        )
    with col2:
        max_des = df_des["tasa_desempleo"].max()
        st.metric("Pico histórico", f"{max_des:.1f}%", "T2-2020 (pandemia)")
    with col3:
        min_des = df_des["tasa_desempleo"].min()
        st.metric("Mínimo histórico", f"{min_des:.1f}%")

    # Gráfico de evolución nacional — usa columna "periodo" (formato YYYY-TN)
    fig_des = px.bar(
        df_des,
        x="periodo",
        y="tasa_desempleo",
        title="Tasa de desempleo trimestral nacional (%)",
        labels={"periodo": "Trimestre", "tasa_desempleo": "Tasa (%)"},
        color="tasa_desempleo",
        color_continuous_scale="RdYlGn_r",
    )
    fig_des.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        yaxis=dict(ticksuffix="%"),
        xaxis=dict(tickangle=-45),
    )
    fig_des.update_traces(
        hovertemplate="<b>%{x}</b><br>Desempleo: %{y:.1f}%<extra></extra>"
    )
    st.plotly_chart(fig_des, use_container_width=True)

    # ── Comparador de ciudades ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🏙️ Comparar ciudades")
    st.markdown(
        "Compara el desempleo entre distintas ciudades para un año específico. "
        "Los datos provienen de la Gran Encuesta Integrada de Hogares (GEIH) del DANE."
    )

    col_cit, col_yr = st.columns([3, 1])
    with col_cit:
        ciudades_sel = st.multiselect(
            "Selecciona ciudades",
            options=CIUDADES_DISPONIBLES,
            default=["bogota", "medellin", "cali", "barranquilla", "bucaramanga"],
            help="Puedes seleccionar entre 2 y 10 ciudades para comparar",
        )
    with col_yr:
        anio_comp = st.selectbox(
            "Año",
            options=list(range(2015, 2025)),
            index=8,  # 2023
            help="Año de la comparación (promedio anual de los 4 trimestres)",
        )

    if len(ciudades_sel) >= 2:
        try:
            df_comp = comparar_ciudades(ciudades_sel, anio_comp)
            fig_comp = px.bar(
                df_comp,
                x="ciudad",
                y="tasa_desempleo_pct",
                title=f"Desempleo por ciudad — {anio_comp} (promedio anual, %)",
                labels={"ciudad": "Ciudad", "tasa_desempleo_pct": "Tasa (%)"},
                color="tasa_desempleo_pct",
                color_continuous_scale="RdYlGn_r",
                text="tasa_desempleo_pct",
            )
            fig_comp.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Desempleo: %{y:.1f}%<extra></extra>",
            )
            fig_comp.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                yaxis=dict(ticksuffix="%"),
                showlegend=False,
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        except Exception as e:
            st.error(f"Error al comparar ciudades: {e}")
    else:
        st.info("Selecciona al menos 2 ciudades para ver la comparación.")

    st.info(
        "💡 **Contexto:** Colombia tiene una de las tasas de desempleo más altas "
        "de América Latina. El desempleo juvenil (18-28 años) duplica la tasa nacional. "
        "Ciudades como Ibagué y Cúcuta superan históricamente el 15%."
    )

# ============================================================
# TAB 4 — EXPORTACIONES
# ============================================================
with tab_exportaciones:
    st.subheader("Exportaciones Colombianas")
    st.markdown(
        "Colombia exporta principalmente petróleo, carbón y café. "
        "La alta dependencia del petróleo hace la economía vulnerable "
        "a los precios internacionales del crudo."
    )

    df_exp = get_exportaciones()
    anios_exp = sorted(df_exp["anio"].unique(), reverse=True)
    anio_exp = st.selectbox("Año", anios_exp, index=0, key="exp_anio")

    top = top_productos(df_exp, n=8, anio=anio_exp)

    col1, col2 = st.columns(2)

    with col1:
        fig_pie = px.pie(
            top,
            values="valor_usd_millones",
            names="producto",
            title=f"Composición de exportaciones {anio_exp}",
            hole=0.4,
        )
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>USD %{value:.0f}M (%{percent})<extra></extra>",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_bar = px.bar(
            top.sort_values("valor_usd_millones"),
            x="valor_usd_millones",
            y="producto",
            orientation="h",
            title=f"Top exportaciones {anio_exp} (USD millones)",
            labels={"valor_usd_millones": "USD millones", "producto": ""},
            color="valor_usd_millones",
            color_continuous_scale="Blues",
        )
        fig_bar.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Evolución temporal
    petroleo_df = df_exp[df_exp["producto"] == "Petróleo y derivados"]
    if not petroleo_df.empty:
        fig_pet = px.area(
            petroleo_df,
            x="anio",
            y="valor_usd_millones",
            title="Exportaciones de petróleo y derivados (1970–presente)",
            labels={"anio": "Año", "valor_usd_millones": "USD millones"},
            color_discrete_sequence=["#2C3E50"],
        )
        st.plotly_chart(fig_pet, use_container_width=True)

    st.warning(
        "⚠️ **Dependencia petrolera:** El petróleo representa entre el 40-55% "
        "de las exportaciones totales. Cuando el precio del crudo cae, "
        "Colombia recibe menos dólares → el peso se devalúa → importaciones suben."
    )

# ============================================================
# TAB 5 — CALCULADORAS
# ============================================================
with tab_calculadoras:
    st.subheader("Calculadoras económicas")
    st.markdown("Herramientas para entender el impacto de la economía en tu bolsillo.")

    calc1, calc2, calc3 = st.tabs([
        "💰 Poder adquisitivo",
        "💵 Tu salario en USD",
        "📅 Devaluación histórica",
    ])

    # ---- Calculadora 1: Poder adquisitivo ----
    with calc1:
        st.markdown(
            "**¿Cuánto vale hoy lo que valía antes?**  \n"
            "La inflación erosiona el poder de compra: $1.000.000 en 2018 "
            "no compra lo mismo que $1.000.000 en 2024."
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            monto = st.number_input(
                "Monto a calcular (COP)",
                min_value=10_000,
                max_value=1_000_000_000,
                value=1_000_000,
                step=100_000,
                help="Valor en pesos colombianos que quieres ajustar por inflación",
            )
        with col2:
            inflacion_anual = st.slider(
                "Inflación anual promedio (%)",
                min_value=1.0,
                max_value=20.0,
                value=6.5,
                step=0.5,
                help="Usa la inflación del año que te interesa. IPC 2022 = 13.1%, IPC 2023 = 9.3%",
            )
        with col3:
            anios_calc = st.slider(
                "Años a calcular",
                min_value=1,
                max_value=20,
                value=5,
                help="Número de años hacia el futuro o el pasado",
            )

        resultado = calcular_poder_adquisitivo(monto, inflacion_anual / 100, anios_calc)

        st.divider()
        r1, r2, r3 = st.columns(3)
        with r1:
            st.metric("Valor hoy", formatear_pesos(monto))
        with r2:
            st.metric(
                f"Equivale a en {anios_calc} años",
                formatear_pesos(resultado["monto_futuro"]),
                help="Cuánto necesitarías en el futuro para mantener el mismo poder de compra",
            )
        with r3:
            st.metric(
                "Poder de compra perdido",
                f"{resultado['perdida_poder_pct']:.1f}%",
                help="Porcentaje de poder adquisitivo que pierdes por la inflación",
            )

        st.info(
            f"💡 Si tienes ${monto:,.0f} hoy y la inflación es {inflacion_anual}% anual, "
            f"en {anios_calc} años ese dinero tendrá el poder de compra de "
            f"**{formatear_pesos(resultado['equivalente_hoy'])}** de hoy. "
            f"Necesitarías {formatear_pesos(resultado['monto_futuro'])} para mantener "
            f"el mismo nivel de vida."
        )

    # ---- Calculadora 2: Salario en USD ----
    with calc2:
        st.markdown(
            "**¿Cuánto ganas en dólares?**  \n"
            "Convierte tu salario en pesos a dólares según la TRM vigente, "
            "y compáralo con el salario mínimo mensual."
        )
        col1, col2 = st.columns(2)
        with col1:
            salario_cop = st.number_input(
                "Tu salario mensual (COP)",
                min_value=0,
                max_value=100_000_000,
                value=3_000_000,
                step=100_000,
                help="Ingresa tu ingreso mensual bruto en pesos colombianos",
            )
        with col2:
            trm_calc = st.number_input(
                "TRM a usar (COP/USD)",
                min_value=1_000.0,
                max_value=10_000.0,
                value=float(get_trm_hoy()),
                step=10.0,
                help="Por defecto se usa la TRM vigente. Puedes cambiarla para simular escenarios",
            )

        resultado_usd = smmlv_a_usd(salario_cop, trm_calc)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tu salario en USD", f"${resultado_usd['equivalente_usd']:,.2f}")
        with col2:
            smmlv_2024_ref = 1_300_000
            smmlv_usd = smmlv_2024_ref / trm_calc
            st.metric("SMMLV en USD", f"${smmlv_usd:,.2f}", help="Salario mínimo en dólares")
        with col3:
            ratio = salario_cop / smmlv_2024_ref
            st.metric("Salarios mínimos", f"{ratio:.1f}x", help="Cuántos SMMLV representa tu ingreso")

    # ---- Calculadora 3: Devaluación ----
    with calc3:
        st.markdown(
            "**¿Cuánto se ha devaluado el peso?**  \n"
            "Mira cómo ha cambiado el valor del dólar en Colombia "
            "entre dos momentos diferentes."
        )
        df_trm_hist = get_historico_trm(meses=36)
        df_trm_df = pd.DataFrame(df_trm_hist)

        col1, col2 = st.columns(2)
        with col1:
            trm_inicio_val = st.number_input(
                "TRM de referencia (pasado)",
                value=3200.0,
                min_value=500.0,
                step=50.0,
                help="TRM en la fecha de inicio (puedes consultarla en el tab TRM hoy)",
            )
        with col2:
            trm_fin_val = st.number_input(
                "TRM actual",
                value=float(get_trm_hoy()),
                min_value=500.0,
                step=50.0,
                help="TRM en la fecha de comparación",
            )

        if trm_inicio_val > 0:
            devaluacion = (trm_fin_val / trm_inicio_val - 1) * 100
            impacto_importacion = devaluacion  # 1% devaluación = 1% más caro importar

            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Devaluación del peso",
                    f"{devaluacion:+.1f}%",
                    help="Positivo = el dólar subió = el peso se devaluó",
                )
            with col2:
                st.metric(
                    "Impacto en importaciones",
                    f"{impacto_importacion:+.1f}%",
                    help="Las importaciones suben en este porcentaje cuando el peso se devalúa",
                )

            if devaluacion > 0:
                st.warning(
                    f"⚠️ El peso perdió **{devaluacion:.1f}%** de su valor frente al dólar. "
                    f"Lo que antes costaba USD 100 ($  {trm_inicio_val:,.0f}), "
                    f"ahora cuesta ${trm_fin_val * 1:,.0f}."
                )
            else:
                st.success(
                    f"✅ El peso se fortaleció **{abs(devaluacion):.1f}%** frente al dólar. "
                    "Las importaciones se abaratan y los ingresos en dólares valen menos en pesos."
                )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Fuentes oficiales: DANE · Banco de la República · Superintendencia Financiera · datos.gov.co  \n"
    "Datos actualizados automáticamente. Los valores de respaldo corresponden a series históricas documentadas."
)
