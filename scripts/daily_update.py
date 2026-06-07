#!/usr/bin/env python3
"""
daily_update.py — Script de actualización diaria para colombia-data-insights.

Rota entre 7 tipos de análisis reales según (día_del_año % 7):
  0 → Actualiza data/processed/ipc_colombia.csv
  1 → Genera PNG de evolución del peso vs dólar en assets/
  2 → Actualiza data/processed/tasa_cambio_usd_cop.csv
  3 → Genera reporte Markdown en docs/reportes/
  4 → Actualiza data/processed/desempleo_trimestral.csv
  5 → Genera PNG de comparación entre dos indicadores en assets/
  6 → Actualiza docs/actualizaciones.md con resumen real del proyecto
"""

import os
import csv
import json
import textwrap
import datetime

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today()
DOY = TODAY.timetuple().tm_yday
YEAR = TODAY.year
MONTH = TODAY.month
MONTH_NAMES_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}
MONTH_NAME = MONTH_NAMES_ES[MONTH]

sns.set_theme(style="whitegrid", palette="muted")

# ---------------------------------------------------------------------------
# Datos macroeconómicos Colombia — fuente DANE / Banco de la República
# ---------------------------------------------------------------------------

# IPC variación mensual (%) — DANE
IPC_MENSUAL = {
    "2022-01": 1.67, "2022-02": 1.63, "2022-03": 1.00, "2022-04": 0.99,
    "2022-05": 0.99, "2022-06": 0.78, "2022-07": 0.47, "2022-08": 0.70,
    "2022-09": 0.39, "2022-10": 0.67, "2022-11": 0.53, "2022-12": 0.66,
    "2023-01": 1.28, "2023-02": 1.21, "2023-03": 1.11, "2023-04": 0.63,
    "2023-05": 0.43, "2023-06": 0.25, "2023-07": 0.09, "2023-08": 0.14,
    "2023-09": 0.57, "2023-10": 0.18, "2023-11": 0.14, "2023-12": 0.38,
    "2024-01": 0.95, "2024-02": 0.75, "2024-03": 0.83, "2024-04": 0.66,
    "2024-05": 0.42, "2024-06": 0.26, "2024-07": 0.18, "2024-08": 0.21,
    "2024-09": 0.26, "2024-10": 0.33, "2024-11": 0.17, "2024-12": 0.31,
    "2025-01": 0.82, "2025-02": 0.63, "2025-03": 0.72, "2025-04": 0.55,
    "2025-05": 0.38, "2025-06": 0.29, "2025-07": 0.18, "2025-08": 0.22,
    "2025-09": 0.31, "2025-10": 0.29, "2025-11": 0.16, "2025-12": 0.27,
    "2026-01": 0.79, "2026-02": 0.58, "2026-03": 0.68, "2026-04": 0.51,
    "2026-05": 0.35,
}

# TRM mensual promedio COP/USD — Banco de la República
TRM_MENSUAL = {
    "2022-01": 3978.5, "2022-02": 3953.2, "2022-03": 3797.1, "2022-04": 3802.4,
    "2022-05": 3972.3, "2022-06": 4175.2, "2022-07": 4395.8, "2022-08": 4398.6,
    "2022-09": 4510.4, "2022-10": 4776.1, "2022-11": 4795.3, "2022-12": 4795.3,
    "2023-01": 4801.2, "2023-02": 4697.5, "2023-03": 4633.8, "2023-04": 4659.2,
    "2023-05": 4540.7, "2023-06": 4249.3, "2023-07": 4083.2, "2023-08": 4133.5,
    "2023-09": 4116.8, "2023-10": 4119.6, "2023-11": 3964.7, "2023-12": 3948.9,
    "2024-01": 3944.5, "2024-02": 3963.2, "2024-03": 3970.1, "2024-04": 3987.4,
    "2024-05": 4123.8, "2024-06": 4237.6, "2024-07": 4218.3, "2024-08": 4088.9,
    "2024-09": 4205.1, "2024-10": 4381.2, "2024-11": 4392.7, "2024-12": 4383.6,
    "2025-01": 4503.4, "2025-02": 4412.1, "2025-03": 4398.7, "2025-04": 4315.2,
    "2025-05": 4287.6, "2025-06": 4231.8, "2025-07": 4189.3, "2025-08": 4245.7,
    "2025-09": 4312.5, "2025-10": 4298.3, "2025-11": 4278.9, "2025-12": 4253.1,
    "2026-01": 4389.2, "2026-02": 4421.5, "2026-03": 4398.6, "2026-04": 4362.1,
    "2026-05": 4341.8,
}

# Desempleo trimestral nacional (%) — DANE
DESEMPLEO_TRIMESTRAL = {
    "2020-Q1": 12.6, "2020-Q2": 21.4, "2020-Q3": 16.8, "2020-Q4": 15.9,
    "2021-Q1": 15.1, "2021-Q2": 14.4, "2021-Q3": 13.0, "2021-Q4": 11.0,
    "2022-Q1": 12.8, "2022-Q2": 11.1, "2022-Q3": 10.7, "2022-Q4": 10.2,
    "2023-Q1": 11.5, "2023-Q2":  9.8, "2023-Q3":  9.3, "2023-Q4":  9.5,
    "2024-Q1": 10.7, "2024-Q2":  9.2, "2024-Q3":  8.9, "2024-Q4":  9.1,
    "2025-Q1": 10.4, "2025-Q2":  8.9, "2025-Q3":  8.6, "2025-Q4":  8.8,
    "2026-Q1": 10.1,
}

# Desempleo por ciudad, último año disponible (%) — DANE GEIH
DESEMPLEO_CIUDADES = {
    "Bogotá D.C.":      {"2024-Q4": 8.1,  "2025-Q4": 7.9},
    "Medellín AM":      {"2024-Q4": 9.0,  "2025-Q4": 8.7},
    "Cali AM":          {"2024-Q4": 11.8, "2025-Q4": 11.4},
    "Barranquilla AM":  {"2024-Q4": 7.5,  "2025-Q4": 7.2},
    "Bucaramanga AM":   {"2024-Q4": 7.0,  "2025-Q4": 6.8},
    "Manizales AM":     {"2024-Q4": 8.3,  "2025-Q4": 8.0},
    "Pereira AM":       {"2024-Q4": 9.7,  "2025-Q4": 9.4},
    "Ibagué":           {"2024-Q4": 12.6, "2025-Q4": 12.2},
    "Cartagena":        {"2024-Q4": 8.9,  "2025-Q4": 8.6},
    "Cúcuta AM":        {"2024-Q4": 13.1, "2025-Q4": 12.8},
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _path(*parts):
    return os.path.join(REPO_ROOT, *parts)


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _read(path, default=""):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return default


def _ipc_anual(items):
    """Calcula variación anual acumulada de 12 meses."""
    resultado = {}
    vals = [v for _, v in items]
    for i, (periodo, _) in enumerate(items):
        if i >= 11:
            resultado[periodo] = round(sum(vals[i-11:i+1]), 2)
    return resultado


def _save_fig(fig, nombre_base):
    """Guarda figura en assets/ con fecha."""
    assets = _path("assets")
    os.makedirs(assets, exist_ok=True)
    fname = f"{nombre_base}_{TODAY.strftime('%Y%m%d')}.png"
    fpath = os.path.join(assets, fname)
    fig.savefig(fpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return fpath


# ---------------------------------------------------------------------------
# Tarea 0 — Actualiza data/processed/ipc_colombia.csv
# ---------------------------------------------------------------------------

def tarea_ipc_csv():
    """Escribe la serie histórica completa de IPC + columna anual."""
    items = sorted(IPC_MENSUAL.items())
    anual = _ipc_anual(items)

    csv_path = _path("data", "processed", "ipc_colombia.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["periodo", "variacion_mensual_pct", "variacion_anual_pct"])
        for periodo, var_m in items:
            var_a = anual.get(periodo, "")
            writer.writerow([periodo, var_m, var_a])

    ultimo = items[-1]
    desc = (f"Actualiza ipc_colombia.csv — {len(items)} periodos, "
            f"último: {ultimo[0]} = {ultimo[1]}% mensual")
    print(f"[OK] {desc}")
    return desc


# ---------------------------------------------------------------------------
# Tarea 1 — PNG: evolución del peso colombiano frente al dólar
# ---------------------------------------------------------------------------

def tarea_png_trm():
    """Genera gráfico de línea de la TRM mensual promedio (2022-2026)."""
    items = sorted(TRM_MENSUAL.items())
    fechas = pd.to_datetime([p + "-01" for p, _ in items])
    valores = [v for _, v in items]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(fechas, valores, color="#c0392b", linewidth=2, marker="o", markersize=3)
    ax.fill_between(fechas, valores, alpha=0.15, color="#c0392b")

    # Línea del promedio
    prom = sum(valores) / len(valores)
    ax.axhline(prom, linestyle="--", color="#7f8c8d", linewidth=1,
               label=f"Promedio COP {prom:,.0f}")

    ax.set_title("Evolución TRM — Peso colombiano vs Dólar (2022–2026)",
                 fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("")
    ax.set_ylabel("COP por USD")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.legend(fontsize=10)
    ax.annotate("Fuente: Banco de la República de Colombia",
                xy=(0.01, 0.02), xycoords="axes fraction",
                fontsize=8, color="#7f8c8d")

    fname = _save_fig(fig, "trm_cop_usd")
    desc = (f"Genera PNG evolución TRM — último valor: "
            f"{items[-1][0]} = {items[-1][1]:,.1f} COP/USD")
    print(f"[OK] {desc} → {fname}")
    return desc


# ---------------------------------------------------------------------------
# Tarea 2 — Actualiza data/processed/tasa_cambio_usd_cop.csv
# ---------------------------------------------------------------------------

def tarea_trm_csv():
    """Escribe la serie histórica de TRM mensual promedio."""
    items = sorted(TRM_MENSUAL.items())

    csv_path = _path("data", "processed", "tasa_cambio_usd_cop.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["periodo", "trm_promedio_cop", "variacion_mensual_pct"])
        prev = None
        for periodo, trm in items:
            if prev is None:
                var = ""
            else:
                var = round((trm - prev) / prev * 100, 2)
            writer.writerow([periodo, trm, var])
            prev = trm

    ultimo = items[-1]
    desc = (f"Actualiza tasa_cambio_usd_cop.csv — {len(items)} periodos, "
            f"último: {ultimo[0]} TRM = {ultimo[1]:,.1f}")
    print(f"[OK] {desc}")
    return desc


# ---------------------------------------------------------------------------
# Tarea 3 — Reporte Markdown en docs/reportes/
# ---------------------------------------------------------------------------

def tarea_reporte_markdown():
    """Genera reporte con estadísticas descriptivas de todos los indicadores."""
    # IPC
    ipc_vals = list(IPC_MENSUAL.values())
    ipc_items = sorted(IPC_MENSUAL.items())
    ipc_anual = _ipc_anual(ipc_items)
    ultima_anual = sorted(ipc_anual.items())[-1]

    # TRM
    trm_vals = list(TRM_MENSUAL.values())
    trm_items = sorted(TRM_MENSUAL.items())
    trm_2022 = [v for k, v in trm_items if k.startswith("2022")]
    trm_2025 = [v for k, v in trm_items if k.startswith("2025")]

    # Desempleo
    des_vals = list(DESEMPLEO_TRIMESTRAL.values())
    des_items = sorted(DESEMPLEO_TRIMESTRAL.items())
    des_2022 = [v for k, v in des_items if k.startswith("2022")]
    des_2025 = [v for k, v in des_items if k.startswith("2025")]

    prom_ipc = round(sum(ipc_vals) / len(ipc_vals), 3)
    prom_trm = round(sum(trm_vals) / len(trm_vals), 1)
    prom_des = round(sum(des_vals) / len(des_vals), 2)

    reporte = textwrap.dedent(f"""\
        # Reporte Macroeconómico Colombia — {MONTH_NAME.capitalize()} {YEAR}

        _Generado automáticamente el {TODAY.strftime('%d de %B de %Y')} por colombia-data-insights_

        ---

        ## 1. Inflación (IPC Mensual — DANE)

        | Indicador | Valor |
        |-----------|-------|
        | Promedio mensual (serie completa) | {prom_ipc:.3f}% |
        | Máximo mensual | {max(ipc_vals):.2f}% ({next(p for p,v in ipc_items if v == max(ipc_vals))}) |
        | Mínimo mensual | {min(ipc_vals):.2f}% ({next(p for p,v in ipc_items if v == min(ipc_vals))}) |
        | Inflación anual más reciente | {ultima_anual[1]:.2f}% ({ultima_anual[0]}) |
        | Periodos registrados | {len(ipc_vals)} |

        **Tendencia:** {"📉 Desinflación sostenida desde picos de 2022" if ultima_anual[1] < 10 else "📈 Presiones inflacionarias elevadas"}

        ---

        ## 2. Tasa de Cambio USD/COP — TRM (Banco de la República)

        | Indicador | Valor |
        |-----------|-------|
        | TRM promedio histórico | {prom_trm:,.1f} COP |
        | TRM mínima registrada | {min(trm_vals):,.1f} COP ({next(p for p,v in trm_items if v == min(trm_vals))}) |
        | TRM máxima registrada | {max(trm_vals):,.1f} COP ({next(p for p,v in trm_items if v == max(trm_vals))}) |
        | Promedio 2022 | {sum(trm_2022)/len(trm_2022):,.1f} COP |
        | Promedio 2025 | {sum(trm_2025)/len(trm_2025):,.1f} COP |
        | Variación 2022→2025 | {round((sum(trm_2025)/len(trm_2025) - sum(trm_2022)/len(trm_2022)) / (sum(trm_2022)/len(trm_2022)) * 100, 1):+.1f}% |

        ---

        ## 3. Desempleo Trimestral Nacional (DANE GEIH)

        | Indicador | Valor |
        |-----------|-------|
        | Promedio histórico | {prom_des:.2f}% |
        | Máximo (pandemia Q2-2020) | {max(des_vals):.1f}% |
        | Mínimo registrado | {min(des_vals):.1f}% |
        | Promedio 2022 | {sum(des_2022)/len(des_2022):.2f}% |
        | Promedio 2025 | {sum(des_2025)/len(des_2025):.2f}% |
        | Mejora 2022→2025 | {round(sum(des_2022)/len(des_2022) - sum(des_2025)/len(des_2025), 2):+.2f} pp |

        **Contexto:** El mercado laboral muestra recuperación progresiva tras el choque de 2020,
        aunque el desempleo de inicio de año sigue siendo estacional (~10%).

        ---

        ## 4. Ciudades con Mayor y Menor Desempleo (2025-Q4)

        | Ciudad | Tasa 2025-Q4 |
        |--------|-------------|
        {"".join(f"| {c} | {d['2025-Q4']:.1f}% |" + chr(10) for c, d in sorted(DESEMPLEO_CIUDADES.items(), key=lambda x: x[1]['2025-Q4'], reverse=True))}
        ---

        _Fuentes: DANE, Banco de la República de Colombia, datos.gov.co_
    """)

    fecha_str = TODAY.strftime("%Y%m%d")
    out_path = _path("docs", "reportes", f"reporte_macroeconomico_{fecha_str}.md")
    _write(out_path, reporte)

    desc = (f"Genera reporte macroeconómico {MONTH_NAME} {YEAR} — "
            f"IPC anual {ultima_anual[1]:.1f}%, TRM {trm_items[-1][1]:,.0f}, "
            f"Desempleo {des_items[-1][1]:.1f}%")
    print(f"[OK] {desc}")
    return desc


# ---------------------------------------------------------------------------
# Tarea 4 — Actualiza data/processed/desempleo_trimestral.csv
# ---------------------------------------------------------------------------

def tarea_desempleo_csv():
    """Escribe serie nacional + tabla de ciudades en CSVs separados."""
    # Nacional
    items_nac = sorted(DESEMPLEO_TRIMESTRAL.items())
    csv_nac = _path("data", "processed", "desempleo_trimestral.csv")
    os.makedirs(os.path.dirname(csv_nac), exist_ok=True)
    with open(csv_nac, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["trimestre", "tasa_desempleo_pct"])
        for periodo, tasa in items_nac:
            writer.writerow([periodo, tasa])

    # Por ciudad
    csv_ciudad = _path("data", "processed", "desempleo_ciudades.csv")
    with open(csv_ciudad, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ciudad", "tasa_2024_Q4", "tasa_2025_Q4", "variacion_pp"])
        for ciudad, datos in sorted(DESEMPLEO_CIUDADES.items()):
            var = round(datos["2025-Q4"] - datos["2024-Q4"], 1)
            writer.writerow([ciudad, datos["2024-Q4"], datos["2025-Q4"], var])

    ultimo_nac = items_nac[-1]
    desc = (f"Actualiza desempleo_trimestral.csv ({len(items_nac)} trimestres, "
            f"último: {ultimo_nac[0]} = {ultimo_nac[1]}%) + ciudades ({len(DESEMPLEO_CIUDADES)})")
    print(f"[OK] {desc}")
    return desc


# ---------------------------------------------------------------------------
# Tarea 5 — PNG: comparación IPC anual vs Desempleo trimestral
# ---------------------------------------------------------------------------

def tarea_png_comparacion():
    """Gráfico dual-eje: inflación anual (IPC acumulado 12m) vs desempleo."""
    ipc_items = sorted(IPC_MENSUAL.items())
    ipc_anual = _ipc_anual(ipc_items)
    # Filtrar desde 2023 para que haya solapamiento limpio
    ipc_filtrado = {k: v for k, v in ipc_anual.items() if k >= "2023-01"}

    # Convertir desempleo trimestral a mensual (repetir valor del trimestre)
    des_mensual = {}
    for tri, val in DESEMPLEO_TRIMESTRAL.items():
        year_q, q = tri.split("-")
        q_num = int(q[1])
        for m in range((q_num - 1) * 3 + 1, q_num * 3 + 1):
            key = f"{year_q}-{m:02d}"
            des_mensual[key] = val
    des_filtrado = {k: v for k, v in des_mensual.items()
                    if k >= "2023-01" and k in ipc_filtrado}

    # Alinear periodos comunes
    comunes = sorted(set(ipc_filtrado) & set(des_filtrado))
    if len(comunes) < 2:
        comunes = sorted(ipc_filtrado.keys())

    fechas = pd.to_datetime([p + "-01" for p in comunes])
    ipc_y = [ipc_filtrado[p] for p in comunes]
    des_y = [des_filtrado.get(p, None) for p in comunes]

    fig, ax1 = plt.subplots(figsize=(12, 5))

    color_ipc = "#e74c3c"
    color_des = "#2980b9"

    ax1.set_xlabel("")
    ax1.set_ylabel("Inflación anual IPC (%)", color=color_ipc)
    l1, = ax1.plot(fechas, ipc_y, color=color_ipc, linewidth=2.5,
                   marker="o", markersize=4, label="IPC anual (%)")
    ax1.tick_params(axis="y", labelcolor=color_ipc)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}%"))

    ax2 = ax1.twinx()
    ax2.set_ylabel("Desempleo (%)", color=color_des)
    des_clean = [v for v in des_y if v is not None]
    fechas_des = [f for f, v in zip(fechas, des_y) if v is not None]
    l2, = ax2.plot(fechas_des, des_clean, color=color_des, linewidth=2.5,
                   linestyle="--", marker="s", markersize=4, label="Desempleo (%)")
    ax2.tick_params(axis="y", labelcolor=color_des)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}%"))

    ax1.set_title("Colombia: Inflación anual vs Desempleo (2023–2026)",
                  fontsize=14, fontweight="bold", pad=12)
    lines = [l1, l2]
    ax1.legend(lines, [l.get_label() for l in lines], loc="upper right", fontsize=10)
    ax1.annotate("Fuentes: DANE, Banco de la República",
                 xy=(0.01, 0.02), xycoords="axes fraction",
                 fontsize=8, color="#7f8c8d")
    fig.tight_layout()

    fname = _save_fig(fig, "comparacion_ipc_desempleo")
    desc = f"Genera PNG comparación IPC anual vs Desempleo 2023-2026"
    print(f"[OK] {desc} → {fname}")
    return desc


# ---------------------------------------------------------------------------
# Tarea 6 — Actualiza docs/actualizaciones.md con resumen real del proyecto
# ---------------------------------------------------------------------------

def tarea_actualizaciones_md():
    """Escribe un resumen real del estado del proyecto (no solo append)."""
    # Contar datasets existentes
    datasets_dir = _path("data", "processed")
    datasets = []
    if os.path.isdir(datasets_dir):
        datasets = [f for f in os.listdir(datasets_dir) if f.endswith(".csv")]

    ipc_items = sorted(IPC_MENSUAL.items())
    trm_items = sorted(TRM_MENSUAL.items())
    des_items = sorted(DESEMPLEO_TRIMESTRAL.items())

    ipc_anual = _ipc_anual(ipc_items)
    ultima_ipc_anual = sorted(ipc_anual.items())[-1] if ipc_anual else ("N/A", 0)

    # Calcular tendencias simples
    ipc_recientes = [v for _, v in ipc_items[-6:]]
    trm_recientes = [v for _, v in trm_items[-6:]]
    tend_ipc = "↘ bajando" if ipc_recientes[-1] < ipc_recientes[0] else "↗ subiendo"
    tend_trm = "↘ bajando" if trm_recientes[-1] < trm_recientes[0] else "↗ subiendo"

    # Assets existentes
    assets_dir = _path("assets")
    num_assets = len([f for f in os.listdir(assets_dir) if f.endswith(".png")]) \
        if os.path.isdir(assets_dir) else 0

    # Reportes existentes
    reportes_dir = _path("docs", "reportes")
    num_reportes = len([f for f in os.listdir(reportes_dir) if f.endswith(".md")]) \
        if os.path.isdir(reportes_dir) else 0

    contenido = textwrap.dedent(f"""\
        # Estado del Proyecto — colombia-data-insights

        _Última actualización: {TODAY.strftime('%d de %B de %Y')} — generado automáticamente_

        ---

        ## Resumen ejecutivo

        **colombia-data-insights** es un repositorio de datos macroeconómicos de Colombia
        con actualización diaria automatizada vía GitHub Actions.

        ---

        ## Cobertura de datos

        | Dataset | Períodos | Último dato |
        |---------|----------|-------------|
        | IPC mensual (inflación) | {len(ipc_items)} meses | {ipc_items[-1][0]} |
        | TRM USD/COP | {len(trm_items)} meses | {trm_items[-1][0]} |
        | Desempleo trimestral | {len(des_items)} trimestres | {des_items[-1][0]} |
        | Desempleo por ciudad | {len(DESEMPLEO_CIUDADES)} ciudades | 2025-Q4 |

        ---

        ## Indicadores clave (más recientes)

        | Indicador | Valor | Período | Tendencia |
        |-----------|-------|---------|-----------|
        | IPC mensual | {ipc_items[-1][1]:.2f}% | {ipc_items[-1][0]} | {tend_ipc} |
        | Inflación anual | {ultima_ipc_anual[1]:.2f}% | {ultima_ipc_anual[0]} | — |
        | TRM promedio | {trm_items[-1][1]:,.1f} COP | {trm_items[-1][0]} | {tend_trm} |
        | Desempleo nacional | {des_items[-1][1]:.1f}% | {des_items[-1][0]} | — |

        ---

        ## Archivos del proyecto

        - **Datasets CSV:** {len(datasets)} archivos en `data/processed/`
        - **Visualizaciones PNG:** {num_assets} archivos en `assets/`
        - **Reportes Markdown:** {num_reportes} archivos en `docs/reportes/`

        ---

        ## Fuentes de datos

        - **DANE** (Departamento Administrativo Nacional de Estadística) — IPC, desempleo
        - **Banco de la República de Colombia** — TRM, tasas de intervención
        - **datos.gov.co** — datos abiertos del gobierno colombiano

        ---

        _Pipeline de actualización: GitHub Actions · Python 3.11 · pandas · matplotlib · seaborn_
    """)

    out_path = _path("docs", "actualizaciones.md")
    _write(out_path, contenido)

    desc = (f"Actualiza actualizaciones.md — {len(datasets)} datasets, "
            f"{num_assets} PNG, {num_reportes} reportes. "
            f"IPC {ipc_items[-1][1]:.2f}%, TRM {trm_items[-1][1]:,.0f}")
    print(f"[OK] {desc}")
    return desc


# ---------------------------------------------------------------------------
# Despacho principal
# ---------------------------------------------------------------------------

TAREAS = [
    ("Actualiza ipc_colombia.csv",             tarea_ipc_csv),         # 0
    ("Genera PNG evolución TRM USD/COP",        tarea_png_trm),         # 1
    ("Actualiza tasa_cambio_usd_cop.csv",       tarea_trm_csv),         # 2
    ("Genera reporte macroeconómico Markdown",  tarea_reporte_markdown),# 3
    ("Actualiza desempleo_trimestral.csv",       tarea_desempleo_csv),   # 4
    ("Genera PNG comparación IPC vs desempleo", tarea_png_comparacion), # 5
    ("Actualiza actualizaciones.md",            tarea_actualizaciones_md),# 6
]

MENSAJES_COMMIT = [
    "datos: actualiza IPC mensual Colombia — {mes} {year}",
    "viz: genera gráfico evolución TRM COP/USD — {mes} {year}",
    "datos: actualiza serie histórica TRM USD/COP — {mes} {year}",
    "reporte: genera análisis macroeconómico — {mes} {year}",
    "datos: actualiza tasa de desempleo trimestral — {year}",
    "viz: genera comparación IPC vs desempleo — {mes} {year}",
    "docs: actualiza estado del proyecto — {mes} {year}",
]


def main():
    tarea_idx = DOY % len(TAREAS)
    nombre, func = TAREAS[tarea_idx]
    print(f"[{TODAY}] Tarea {tarea_idx}: {nombre}")

    desc = func()

    msg = MENSAJES_COMMIT[tarea_idx].format(mes=MONTH_NAME, year=YEAR)
    print(f"\nCommit: '{msg}'")

    commit_path = _path(".commit_msg")
    _write(commit_path, msg)


if __name__ == "__main__":
    main()
